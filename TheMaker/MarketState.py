#!/usr/bin/python
from OrderBook import OrderBook, Order
import copy

class MarketState:
    """Market state and information that trading reacts upon"""
    def __init__(self, market='BTCUSDT', target="BTC", base="USDT"):
        self.market = market
        self.order_book = OrderBook(market)
        self.portfolio_dict = {
            'BTC':  10.0,
            'USDT': 100000.0
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
        # self.MAKER_FEE = 0.075
        # self.TAKER_FEE = 0.075
        self.MAKER_FEE = 0.0
        self.TAKER_FEE = 0.0
        self.MIN_TICK = 0.00001
        # An order book with only my orders
        self.open_orders = OrderBook(market, depth=20)
        self.num_buy_orders = 0
        self.num_sell_orders = 0

    def getTargetValue(self):
        return self.portfolio_dict[self.target] * self.last_trade.price

    def getPortfolioValue(self, base="USDT"):
        ret = -1
        if base == "USDT" and self.last_trade.quantity != 0.0:
            assert type(self.last_trade) is Order
            ret = float(self.last_trade.price) * float(self.portfolio_dict['BTC'])+\
                  float(self.portfolio_dict['USDT'])

        if self.starting_portfolio_value == -1:
            self.starting_portfolio_value = ret
        return ret

    def getStartingPortfolioValue(self, base="USDT"):
        ret = -1
        if base == "USDT" and self.last_trade.quantity != 0.0:
            assert type(self.last_trade) is Order
            ret = float(self.last_trade.price) * float(self.starting_portfolio['BTC'])+\
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
                    self.portfolio_dict['BTC'] += traded_order.position_quantity * (1-self.MAKER_FEE)
                    self.power['BTC'] += traded_order.position_quantity * (1 - self.MAKER_FEE)
                    self.portfolio_dict['USDT'] -= traded_order.price * traded_order.position_quantity
                else:
                    # Ask got filled
                    self.num_sell_orders += 1
                    self.portfolio_dict['BTC'] -= traded_order.position_quantity
                    self.portfolio_dict['USDT'] += traded_order.price * traded_order.position_quantity\
                                                   * (1-self.MAKER_FEE)
                    self.power['USDT'] += traded_order.price * traded_order.position_quantity \
                                                   * (1 - self.MAKER_FEE)

    def __str__(self):
        return "\n\n\n\n\n\n\n\n\n\n\n\n\n\n" \
               "\nPortfolio\t: "+str(self.portfolio_dict)+ "\t{:12.4f}".format(self.calc_value_ratio()) + \
               "\n(b/s)power\t: " + str(self.power) + \
               "\nPortfolio_value\t= "+str(self.getPortfolioValue())+ \
               "\nStart_value\t= "+str(self.getStartingPortfolioValue())+\
               "\nPnL\t\t= "+ str(self.getProfitLoss()) + \
               "\nPnL%\t\t= " + str(self.getPnLPercent()) + \
               "\n# Trades\t= " + str(self.num_trades) + "\tb: "+str(self.num_buy_orders) + \
               "\ts: " + str(self.num_sell_orders) + \
               "\nopen orders\t=\tb: "+str(len(self.open_orders.bids)) + \
               "\ts: " + str(len(self.open_orders.asks)) +\
               "\n\nLast Trade\t= " + \
               str(self.last_trade) + "\n" + str(self.order_book)

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
        self.order_book.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0),
                                          side='b')
        self.open_orders.add_modify_delete(Order(order.price, quantity=0.0, pos_quantity=0.0),
                                          side='b')
        self.power['USDT'] += order.price * order.position_quantity

    def cancel_limit_sell(self, order: Order):
        self.order_book.add_modify_delete(Order(order.price, quantity=0.0, side='a'),
                                          side='a')
        self.open_orders.add_modify_delete(Order(order.price, quantity=0.0, side='a'),
                                           side='a')
        self.power['BTC'] += order.position_quantity

if __name__ == "__main__":
    ## TESTS ##
    mkt = MarketState('BTCUSDT')
    print(mkt)
