#!/usr/bin/python
from OrderBook import OrderBook, Order
from TradeCache import TradeCache
import copy
import threading
import time
import logging
import copy
import numpy as np

BID = 'b'
ASK = 'a'
UP = "up"
NEUTRAL = "neutral"
DOWN = "down"

logger = logging.getLogger(__name__)
# logger.addHandler(logging.FileHandler("TheMaker_orders.log"))
# logger.setLevel(logging.DEBUG)


class MarketState:
    """Market state and information that trading reacts upon"""

    def __init__(self, market='BTC', target="BTC", base="USDT"):
        self.market = market
        self.order_book = OrderBook(market, depth=60)
        self.portfolio_dict = {
            target:  0.0,
            base: 10000.0
        }
        self.starting_portfolio = copy.deepcopy(self.portfolio_dict)
        self.power = copy.deepcopy(self.portfolio_dict)

        self.target = target
        self.base = base
        self.last_trade = Order(0.0, 0.0)
        self.last_trade_orders = []
        self.last_trade_msg = "{}"
        self.starting_portfolio_value = -1
        self.num_trades = 0
        self.MAKER_FEE = 0.0002
        self.TAKER_FEE = 0.0002
        # self.MAKER_FEE = 0.0
        # self.TAKER_FEE = 0.0
        self.MIN_TICK = 0.00001

        # An order book with only my orders
        self.open_orders = OrderBook(market)
        self.fills = []

        self.num_buy_orders = 0
        self.num_sell_orders = 0
        self.sum_of_buy_values = 0.0
        self.sum_of_sell_values = 0.0

        self.num_buy_cancels = 0
        self.num_sell_cancels = 0
        self.total_buy_quantity = 0.0
        self.total_sell_quantity = 0.0

        self.VOLUME_ALERT_THRESH = 2
        self.historical_volume = [{"vol": 0.0, "alert": 0.0}]
        self.history_len = 20    # minutes
        self._clock_thread = threading.Thread(target=self.__update_clock)
        self._clock_lock = threading.Lock()
        self._clock_thread.start()
        self.num_alerts = 0

        self.moving_averages = [{"ma_total": 0.0, "vwma_total": 0.0, "total_trades": 0, "total_volume": 0.0}]
        self.moving_averages_len = 7    # minutes
        self.moving_average = {'ma': 0.0, 'vwma': 0.0}
        self._moving_average_last = {'ma': 0.0, 'vwma': 0.0}
        self.moving_average_slope = NEUTRAL

        self.longer_moving_averages = [{"ma_total": 0.0, "vwma_total": 0.0, "total_trades": 0, "total_volume": 0.0}]
        self.longer_moving_averages_len = 25  # minutes
        self.longer_moving_average = {'ma': 0.0, 'vwma': 0.0}
        self._longer_moving_average_last = {'ma': 0.0, 'vwma': 0.0}
        self.longer_moving_average_slope = NEUTRAL

        self.trend_switched = True
        self.micro_trend = NEUTRAL
        self.macro_trend = NEUTRAL

        self.elapse_min = False     # set false until moving average length has elapsed

        self.trade_cache = None


    def getTargetValue(self):
        return self.portfolio_dict[self.target] * self.last_trade.price

    def getPortfolioValue(self, base="USDT"):
        ret = -1
        if base == "USDT" and self.last_trade.quantity != 0.0:
            assert type(self.last_trade) is Order
            ret = float(self.last_trade.price) * float(self.portfolio_dict[self.target])+\
                  float(self.portfolio_dict['USDT'])

        if self.starting_portfolio_value == -1:
            self.starting_portfolio_value = ret
        return ret

    def getStartingPortfolioValue(self, base="USDT"):
        ret = -1
        if base == "USDT" and self.last_trade.quantity != 0.0:
            assert type(self.last_trade) is Order
            ret = float(self.last_trade.price) * float(self.starting_portfolio[self.target])+\
                  float(self.starting_portfolio['USDT'])

        if self.starting_portfolio_value == -1:
            self.starting_portfolio_value = ret
        return ret

    def calc_value_ratio(self):
        """ratio of total value of holding assets"""
        return self.getTargetValue() / self.getPortfolioValue()

    def getProfitLoss(self):
        ret = -1
        if self.starting_portfolio_value != -1:
            ret = (self.getPortfolioValue() - self.starting_portfolio_value)
        return ret

    def getPnLPercent(self):
        ret = -1
        if self.starting_portfolio_value != -1:
            ret = float(self.getProfitLoss())/float(self.starting_portfolio_value)
        return ret

    def setLastTrade(self, msg):
        self.last_trade.price = float(msg['p'])
        self.last_trade.quantity = float(msg['q'])
        if msg['m'] is True:
            self.last_trade.side = 'b'
        else:
            self.last_trade.side = 'a'
        self.last_trade_msg = msg

        if self.trade_cache is None:
            self.trade_cache = TradeCache(self.last_trade.price)
        self.trade_cache.update(self.last_trade.price, self.last_trade.side)

        self._clock_lock.acquire()

        self.historical_volume[0]["vol"] += self.last_trade.quantity

        self.moving_averages[0]['ma_total'] += self.last_trade.price
        self.moving_averages[0]['vwma_total'] += self.last_trade.price * self.last_trade.quantity
        self.moving_averages[0]['total_trades'] += 1
        self.moving_averages[0]['total_volume'] += self.last_trade.quantity

        self.longer_moving_averages[0]['ma_total'] += self.last_trade.price
        self.longer_moving_averages[0]['vwma_total'] += self.last_trade.price * self.last_trade.quantity
        self.longer_moving_averages[0]['total_trades'] += 1
        self.longer_moving_averages[0]['total_volume'] += self.last_trade.quantity

        self._clock_lock.release()


    timeout = 5
    def __update_clock(self):
        while True:
            time.sleep(self.timeout)
            self._clock_lock.acquire()

            self.__update_historical_volume()
            self.__set_moving_averages()

            self._clock_lock.release()

    def __update_historical_volume(self):
        if self.historical_volume[0]['vol'] > self.VOLUME_ALERT_THRESH:
            self.historical_volume[0]['alert'] = 1.0
            self.num_alerts += 1

        self.historical_volume.insert(0, {"vol": 0.0, "alert": 0.0})
        if len(self.historical_volume) > self.history_len:
            popped = self.historical_volume.pop(len(self.historical_volume) - 1)
            if popped['alert'] > 0.0:
                self.num_alerts -= 1

    def __set_moving_averages(self):
        self.moving_averages.insert(0, {"ma_total": 0.0, "vwma_total": 0.0, "total_trades": 0, "total_volume": 0.0})
        if len(self.moving_averages) > self.moving_averages_len:
            ma_total = 0.0
            vwma_total = 0.0
            total_trades = 0.0
            total_volume = 0.0
            for i in self.moving_averages:
                ma_total += i['ma_total']
                vwma_total += i['vwma_total']
                total_trades += i['total_trades']
                total_volume += i['total_volume']
            self._moving_average_last = copy.deepcopy(self.moving_average)
            self.moving_average['ma'] = ma_total / total_trades
            self.moving_average['vwma'] = vwma_total / total_volume
            popped = self.moving_averages.pop(len(self.moving_averages) - 1)

            if self.moving_average['vwma'] > self._moving_average_last['vwma']:
                self.moving_average_slope = UP
            elif self.moving_average['vwma'] < self._moving_average_last['vwma']:
                self.moving_average_slope = DOWN

            self.elapse_min = True


        self.longer_moving_averages.insert(0, {"ma_total": 0.0, "vwma_total": 0.0, "total_trades": 0, "total_volume": 0.0})
        if len(self.longer_moving_averages) > self.longer_moving_averages_len:
            ma_total = 0.0
            vwma_total = 0.0
            total_trades = 0.0
            total_volume = 0.0
            for i in self.longer_moving_averages:
                ma_total += i['ma_total']
                vwma_total += i['vwma_total']
                total_trades += i['total_trades']
                total_volume += i['total_volume']
            self._longer_moving_average_last = copy.deepcopy(self.longer_moving_average)
            self.longer_moving_average['ma'] = ma_total / total_trades
            self.longer_moving_average['vwma'] = vwma_total / total_volume
            popped = self.longer_moving_averages.pop(len(self.longer_moving_averages) - 1)

            if self.longer_moving_average['vwma'] > self._longer_moving_average_last['vwma']:
                self.longer_moving_average_slope = UP
            elif self.longer_moving_average['vwma'] < self._longer_moving_average_last['vwma']:
                self.longer_moving_average_slope = DOWN


    def acquire_elapse_min(self):
        self._clock_lock.acquire()

        if self.elapse_min:
            self.elapse_min = False
            self._clock_lock.release()
            return True
        else:
            self._clock_lock.release()
            return False


    def __historical_volume_str__(self):
        ret = ""
        for dict in self.historical_volume:
            if  dict['vol'] > self.VOLUME_ALERT_THRESH:
                ret += C.FAIL + str(dict) + C.ENDC +"\n"
            else:
                ret += str(dict) +"\n"
        return ret

    def getPositionSpread(self):
        if len(self.open_orders.bids) > 0 and len(self.open_orders.asks) > 0:
            return self.open_orders.asks.sortedOrderList[0].price - self.open_orders.bids.sortedOrderList[0].price
        else:
            return -1

    def getAverageBuyPrice(self) -> float:
        """VWAP of buys"""
        if self.total_buy_quantity > 0:
            return self.sum_of_buy_values / self.total_buy_quantity
        return -1.0

    def getAverageSellPrice(self) -> float:
        """VWAP of sells"""
        if self.total_sell_quantity > 0:
            return self.sum_of_sell_values / self.total_sell_quantity
        return -1.0

    last_filled_bid = None
    last_filled_ask = None
    def binance_incremental_trade_update_handler(self, msg):
        ## TODO: only apply maker fee to USDT (base currency)
        self.setLastTrade(msg)
        traded_orders = self.order_book.binance_incremental_trade_update_handler(msg)
        traded_open_orders = self.open_orders.binance_incremental_trade_update_handler(msg)

        if len(traded_orders) > 0:
            self.last_trade_orders = traded_orders
        for traded_order in traded_open_orders:
            if traded_order is not None and traded_order.position_quantity > 0:
                logger.debug("ORDER FILLED\t\t:\t-> {}".format(traded_order))
                self.fills.append(traded_order)
                self.num_trades += 1

                if traded_order.side == 'b':
                    # Bid got filled
                    self.num_buy_orders += 1
                    self.total_buy_quantity += traded_order.position_quantity
                    self.portfolio_dict['BTC'] += traded_order.position_quantity
                    self.power['BTC'] += traded_order.position_quantity
                    self.portfolio_dict['USDT'] -= traded_order.price * traded_order.position_quantity \
                                                   * (1+self.MAKER_FEE)
                    self.sum_of_buy_values += traded_order.price * traded_order.position_quantity
                    self.last_filled_bid = traded_order
                else:
                    # Ask got filled
                    self.num_sell_orders += 1
                    self.total_sell_quantity += traded_order.position_quantity
                    self.portfolio_dict['BTC'] -= traded_order.position_quantity
                    self.portfolio_dict['USDT'] += traded_order.price * traded_order.position_quantity \
                                                   * (1-self.MAKER_FEE)
                    self.power['USDT'] += traded_order.price * traded_order.position_quantity \
                                                   * (1 - self.MAKER_FEE)

                    # no maker fee included
                    self.sum_of_sell_values += traded_order.price * traded_order.position_quantity

                    self.last_filled_ask = traded_order

                #round
                self.__round_portfolio()
        self.__health_check()

    def binance_incremental_depth_update_handler(self, msg):
        self.trend_switched = False
        # set direction statistic
        if self.order_book.getMidPrice() > self.moving_average['vwma']:
            if self.micro_trend != UP:
                self.trend_switched = True
            else:
                self.trend_switched = False

            self.micro_trend = UP

        elif self.order_book.getMidPrice() < self.moving_average['vwma']:
            if self.micro_trend != DOWN:
                self.trend_switched = True
            else:
                self.trend_switched = False

            self.micro_trend = DOWN

        if self.order_book.getMidPrice() > self.longer_moving_average['vwma']:
            self.macro_trend = UP
        elif self.order_book.getMidPrice() < self.longer_moving_average['vwma']:
            self.macro_trend = DOWN

    def get_fills(self):
        fills = []
        if len(self.fills) > 0:
            fills = copy.deepcopy(self.fills)
            self.fills.clear()
        return fills

    def __round_portfolio(self):
        """Rounds everything off after calculations"""
        self.portfolio_dict[self.target] = round(self.portfolio_dict[self.target], 4)
        self.portfolio_dict[self.base] = round(self.portfolio_dict[self.base], 4)
        self.power[self.target] = round(self.power[self.target], 4)
        self.power[self.base] = round(self.power[self.base], 4)

    def __str__(self):
        # return "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n " \
        return "Portfolio\t: "+str(self.portfolio_dict)+ "{:12.4f}".format(self.calc_value_ratio()) + \
               "\n(b/s)power\t: " + str(self.power) + \
               "\nPortfolio_value\t= "+str(self.getPortfolioValue())+ \
               "\nStart_value\t= "+str(self.getStartingPortfolioValue())+\
               "\nPnL\t\t= "+ str(self.getProfitLoss()) + \
               "\nPnL%\t\t= " + str(self.getPnLPercent()) + \
               "\n# Trades\t= " + str(self.num_trades) + "\tb: {:2.2f}".format(self.total_buy_quantity) + \
               "\ts: {:2.2f}".format(self.total_sell_quantity) + \
               "\nopen orders\t=\tb: "+str(len(self.open_orders.bids)) + \
               "\ts: " + str(len(self.open_orders.asks)) + \
               "\ncancels \t= "+ str(self.num_buy_cancels+self.num_sell_cancels)+\
               "\tb: " + str(self.num_buy_cancels) + \
               "\ts: " + str(self.num_sell_cancels) + \
               "\navg price\t:\tb: {:2.4f}".format(self.getAverageBuyPrice()) + \
               "\ts: {:2.4f}".format(self.getAverageSellPrice()) + \
               "\nma (length {})\t: {:2.4f}\tvwma: {:2.4f}"\
                   .format(self.moving_averages_len, self.moving_average['ma'], self.moving_average['vwma']) + \
               "\ndirection:\t: {}" \
                   .format(self.micro_trend) + \
               "\npos_spread\t= "+ str(self.getPositionSpread()) + \
               "\n\nLast Trade\t= " + \
               str(self.last_trade) + \
               "\nVolume\t\t:\n" +self.__historical_volume_str__() + \
               "\n" + str(self.order_book)

    """Mock Trading Stuff"""
    def new_limit_buy(self, order: Order):
        logger.debug("new_limit_buy\t\t: {}".format(order))
        total = float(order.price * order.quantity)
        if self.power['USDT'] - total < 0.0:
            logger.debug("REJECTED: order=[" + str(order) +"] Reason=not enough base buying power")
            return False
        self.order_book.add_modify_delete(order, side='b', my_order=True)
        self.open_orders.add_modify_delete(order, side='b', my_order=True)
        self.power['USDT'] -= order.price * order.position_quantity * (1+self.MAKER_FEE)
        self.__round_portfolio()
        return True

    def new_limit_sell(self, order: Order):
        logger.debug("new_limit_sell\t: {}".format(order))
        if self.power['BTC'] - float(order.quantity) < 0.0:
            logger.debug("REJECTED: order=[" + str(order) + "] Reason=not enough target selling power")
            return False
        self.order_book.add_modify_delete(order, side='a', my_order=True)
        self.open_orders.add_modify_delete(order, side='a', my_order=True)
        self.power['BTC'] -= order.position_quantity
        self.__round_portfolio()
        return True

    def cancel_limit_buy(self, order: Order):
        assert (order.side == BID)
        logger.debug("cancel_limit_buy\t: {}".format(order))
      #  print("order cancel coming in  :", order)
        self.order_book.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0),
                                          side='b', my_order=True)
        self.open_orders.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0),
                                          side='b', my_order=True)
        self.power['USDT'] += order.price * order.position_quantity * (1+self.MAKER_FEE)
        self.num_buy_cancels += 1
        self.__round_portfolio()

    def cancel_limit_sell(self, order: Order):
        assert(order.side == ASK)
        logger.debug("cancel_limit_sell\t: {}".format(order))
      #  print("order cancel coming in  :", order)
        self.order_book.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0, side='a'),
                                          side='a', my_order=True)
        self.open_orders.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0, side='a'),
                                           side='a', my_order=True)
        self.power['BTC'] += order.position_quantity
        self.num_sell_cancels += 1
        self.__round_portfolio()


    def __health_check(self):
        self.order_book.health_check()
        self.open_orders.health_check()

        # verify buying power is less than portfolio values
        if self.power[self.base] > self.portfolio_dict[self.base] \
                or self.power[self.target] > self.portfolio_dict[self.target]:
            raise Exception("Buying power exceeds portfolio value:\nportfolio:\t{}\nBuying power:\t{}\nLast Trade:\t{}\n"
                            .format(self.portfolio_dict, self.power, self.last_trade))

        # verify buying power and portfolio values are not negative
        if self.power[self.base] < -0.0000001 or self.power[self.target] < -0.0000001:
            raise Exception("Buying power is negative:{}".format(self.power))
        if self.portfolio_dict[self.base] < -0.0000001 or self.portfolio_dict[self.target] < -0.0000001:
            raise Exception("Portfolio value is negative:{}".format(self.portfolio_dict))

class C:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if __name__ == "__main__":
    ## TESTS ##
    mkt = MarketState('BTCUSDT')
    print(mkt)
