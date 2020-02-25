#!/usr/bin/python
from OrderBook import OrderBook, Order
import copy
import threading
import time

class MarketState:
    """Market state and information that trading reacts upon"""

    def __init__(self, market='BTC', target="BTC", base="USDT"):
        self.market = market
        self.order_book = OrderBook(market, depth=50)
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
        # self.MAKER_FEE = 0.00075
        # self.TAKER_FEE = 0.00075
        self.MAKER_FEE = 0.0
        self.TAKER_FEE = 0.0
        self.MIN_TICK = 0.00001

        # An order book with only my orders
        self.open_orders = OrderBook(market)

        self.num_buy_orders = 0
        self.num_sell_orders = 0
        self.num_buy_cancels = 0
        self.num_sell_cancels = 0
        self.total_buy_quantity = 0.0
        self.total_sell_quantity = 0.0

        self.VOLUME_ALERT_THRESH = 30
        self.historical_volume = [{"vol": 0.0, "alert": 0.0}]
        self.history_len = 6
        self.historical_thread = threading.Thread(target=self.__update_historical_volume)
        self.historical_lock = threading.Lock()
        self.historical_thread.start()
        self.num_alerts = 0


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

        self.historical_lock.acquire()
        self.historical_volume[0]["vol"] += self.last_trade.quantity
        self.historical_lock.release()

    def __update_historical_volume(self):
        while True:
            time.sleep(60)
            self.historical_lock.acquire()

            if self.historical_volume[0]['vol'] > self.VOLUME_ALERT_THRESH:
                self.historical_volume[0]['alert'] = 1.0
                self.num_alerts += 1

            self.historical_volume.insert(0, {"vol": 0.0, "alert": 0.0})
            if len(self.historical_volume) > self.history_len:
                popped = self.historical_volume.pop(len(self.historical_volume) - 1)
                if popped['alert'] > 0.0:
                    self.num_alerts -= 1

            self.historical_lock.release()

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


    def binance_incremental_trade_update_handler(self, msg):
        traded_orders = self.order_book.binance_incremental_trade_update_handler(msg)
        traded_open_orders = self.open_orders.binance_incremental_trade_update_handler(msg)
        if len(traded_orders) > 0:
            self.last_trade_orders = traded_orders
        for traded_order in traded_orders:
            if traded_order is not None and traded_order.position_quantity > 0:
                self.num_trades += 1
                if traded_order.side == 'b':
                    # Bid got filled
                    self.num_buy_orders += 1
                    self.total_buy_quantity += traded_order.position_quantity * (1-self.MAKER_FEE)
                    self.portfolio_dict['BTC'] += traded_order.position_quantity * (1-self.MAKER_FEE)
                    self.power['BTC'] += traded_order.position_quantity * (1 - self.MAKER_FEE)
                    self.portfolio_dict['USDT'] -= traded_order.price * traded_order.position_quantity
                else:
                    # Ask got filled
                    self.num_sell_orders += 1
                    self.total_sell_quantity += traded_order.position_quantity
                    self.portfolio_dict['BTC'] -= traded_order.position_quantity
                    self.portfolio_dict['USDT'] += traded_order.price * traded_order.position_quantity\
                                                   * (1-self.MAKER_FEE)
                    self.power['USDT'] += traded_order.price * traded_order.position_quantity \
                                                   * (1 - self.MAKER_FEE)


    def __str__(self):
        return "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" \
               "\nPortfolio\t: "+str(self.portfolio_dict)+ "\t{:12.4f}".format(self.calc_value_ratio()) + \
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
               "\npos_spread\t= "+ str(self.getPositionSpread()) + \
               "\n\nLast Trade\t= " + \
               str(self.last_trade) + \
               "\nVolume\t\t:\n" +self.__historical_volume_str__() + \
               "\n" + str(self.order_book)

    """Mock Trading Stuff"""
    def new_limit_buy(self, order: Order):
        self.order_book.add_modify_delete(order, side='b', my_order=True)
        self.open_orders.add_modify_delete(order, side='b', my_order=True)
        self.power['USDT'] -= order.price * order.position_quantity

    def new_limit_sell(self, order: Order):
        self.order_book.add_modify_delete(order, side='a', my_order=True)
        self.open_orders.add_modify_delete(order, side='a', my_order=True)
        self.power['BTC'] -= order.position_quantity

    def cancel_limit_buy(self, order: Order):
      #  print("order cancel coming in  :", order)
        self.order_book.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0),
                                          side='b', my_order=True)
        self.open_orders.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0),
                                          side='b', my_order=True)
        self.power['USDT'] += order.price * order.position_quantity
        self.num_buy_cancels += 1

    def cancel_limit_sell(self, order: Order):
      #  print("order cancel coming in  :", order)
        self.order_book.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0, side='a'),
                                          side='a', my_order=True)
        self.open_orders.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0, side='a'),
                                           side='a', my_order=True)
        self.power['BTC'] += order.position_quantity
        self.num_sell_cancels += 1


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
