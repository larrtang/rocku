#!/usr/bin/python

from MarketState import MarketState
from OrderBook import OrderBook, Order
from BinanceTradeEngine import BinanceTradeEngine
from random import randrange
import random

BID = 'b'
ASK = 'a'



def can_buy(market_state: MarketState) -> bool:
    return market_state.power[market_state.base] > 0.001


def can_sell(market_state: MarketState) -> bool:
    return market_state.power[market_state.target] > 0.001

class Test:
    def __init__(self):
        self.DEFAULT_POSITION_QUANTITY = 0.01
        self.MAX_SPREAD_WIDTH = 3.1
        self.MIN_SPREAD_WIDTH = 1
        self.AUTO_CANCEL_PRICE_THRESHOLD = 7.0
        self.AUTO_CANCEL_DEPTH_THRESHOLD = 60

        self.do_once_done = False


    def submit_depth_order(self, market_state: MarketState, side, depth, quantity):
        # depth starts at 0 (top of book)
        if side == BID:
            if depth >= len(market_state.order_book.bids):
                return None
            price = market_state.order_book.bids.sortedOrderList[depth].price + market_state.MIN_TICK
            new_order = Order(price=price,
                              quantity=quantity,
                              pos_quantity=quantity,
                              side=side)
            market_state.new_limit_buy(new_order)
        else:
            if depth >= len(market_state.order_book.asks):
                return None
            price = market_state.order_book.asks.sortedOrderList[depth].price - market_state.MIN_TICK
            new_order = Order(price=price,
                              quantity=quantity,
                              pos_quantity=quantity,
                              side=side)
            market_state.new_limit_sell(new_order)
        return new_order

    def submit_depth_price_order(self, market_state: MarketState, side, depth, price_offset, quantity):
        """price_offset - distance from mid price which the order has to be, or the depth will increase"""
        # check if price offsets are crossed with mid price
        # depth starts at 0 (top of book)
        d = depth
        mid = market_state.order_book.getMidPrice()
        target_price = mid + price_offset
        if side == BID:
            if target_price > mid or len(market_state.order_book.bids.sortedOrderList) < d+1:
                return None
            price = market_state.order_book.bids.sortedOrderList[d].price + market_state.MIN_TICK
            # new bid must be less than target price, or at least target price
            while price > target_price:
                d += 1
                if len(market_state.order_book.bids.sortedOrderList) < d+1:
                    return None
                price = market_state.order_book.bids.sortedOrderList[d].price + market_state.MIN_TICK
            new_order = Order(price=price,
                              quantity=quantity,
                              pos_quantity=quantity,
                              side=side)
            market_state.new_limit_buy(new_order)
        else:
            if target_price < mid or len(market_state.order_book.asks.sortedOrderList) < d+1:
                return None
            price = market_state.order_book.asks.sortedOrderList[d].price - market_state.MIN_TICK
            # new ask must be greater than target price, or at least target price
            while price < target_price:
                d += 1
                if len(market_state.order_book.asks.sortedOrderList) < d+1:
                    return None
                price = market_state.order_book.asks.sortedOrderList[d].price - market_state.MIN_TICK
            new_order = Order(price=price,
                              quantity=quantity,
                              pos_quantity=quantity,
                              side=side)
            market_state.new_limit_sell(new_order)
        return new_order

    def on_trade_update(self, market_state: MarketState):
        #self.do_once_beginning(market_state)
        mid_dist = 4
        if market_state.num_alerts >= 2:
            mid_dist *= 2

        b = -mid_dist
        if market_state.calc_value_ratio() > 0.24:
            b -= 0.5

        if len(market_state.open_orders.bids) == 0 or True:
            if can_buy(market_state):
                self.submit_depth_order(market_state, side=BID, depth=randrange(4), quantity=0.01)

        if len(market_state.open_orders.asks) == 0 or True:
        #if len(market_state.open_orders.bids) > 0:
            if can_sell(market_state):
                self.submit_depth_order(market_state, side=ASK, depth=randrange(4), quantity=0.01)

# FIXME something logically is not right, more sells are happening than buys, buying power and portfolio values are going negative.
# FIXME Problem still exists, buying power will exceed portfolio value, sell orders are being placed when they shouldn't

                # target_spread = mid_dist * 2
                # market_state.new_limit_sell(Order(price=market_state.last_filled_bid.price+target_spread,
                #                                   quantity=ask_position_quantity,
                #                                   pos_quantity=ask_position_quantity,
                #                                   side='a'))

# END FIXME
        self.auto_cancel_orders(market_state)

    def do_once_beginning(self, market_state: MarketState):
        if not self.do_once_done:
            self.do_once_done = True

        self.submit_depth_price_order(market_state,
                                      side=BID,
                                      depth=5,
                                      price_offset=-0.3,
                                      quantity=self.DEFAULT_POSITION_QUANTITY)
        if can_sell(market_state):
            self.submit_depth_price_order(market_state,
                                          side=ASK,
                                          depth=5,
                                          price_offset=0.3,
                                          quantity=self.DEFAULT_POSITION_QUANTITY)


    def on_depth_update(self, market_state : MarketState):
        self.auto_cancel_orders(market_state)

    def auto_cancel_orders(self, market_state: MarketState):
        """Cancels orders that have been pushed off the book"""
        bbook = market_state.open_orders.bids.sortedOrderList
        abook = market_state.open_orders.asks.sortedOrderList
        for i in range(len(bbook)-1, -1, -1):
            if (bbook[i].price < market_state.last_trade.price - self.AUTO_CANCEL_PRICE_THRESHOLD) \
            or (market_state.order_book.getDepthOfPrice(bbook[i].price, side='b') >= self.AUTO_CANCEL_DEPTH_THRESHOLD):
                market_state.cancel_limit_buy(bbook[i])
                #bbook.pop(i)
            elif market_state.order_book.getTotalFromPrice(bbook[i].price, side='b') > 9.0:
                break
                market_state.cancel_limit_buy(bbook[i])

            else:
                break
        for i in range(len(abook)-1, -1, -1):
            if (abook[i].price > market_state.last_trade.price + self.AUTO_CANCEL_PRICE_THRESHOLD) \
            or (market_state.order_book.getDepthOfPrice(abook[i].price, side='a') >= self.AUTO_CANCEL_DEPTH_THRESHOLD):
                market_state.cancel_limit_sell(abook[i])
                #abook.pop(i)

            elif market_state.order_book.getTotalFromPrice(abook[i].price, side='a') > 9.0:
                break
                market_state.cancel_limit_sell(abook[i])

            else:
                break
        # if len(bbook) == market_state.open_orders.depth or len(abook) == market_state.open_orders.depth:
        #     print(market_state.open_orders)


    def calc_desired_spread(self, market_state: MarketState, width=2):
        ratio = market_state.calc_value_ratio()
        b = -width * ratio
        a = b + width
        return b, a



def speed_test():
    orderbook = OrderBook("")
    for i in range(1000):
        j = randrange(0,2)
        if j == 0:
            order = Order(float(random.uniform(1.0, 5.0)), float(randrange(0, 3)), 0.0, BID)
            orderbook.add_modify_delete(order, BID)
        else:
            order = Order(float(random.uniform(5.0, 9.0)), float(randrange(0, 3)), 0.0, ASK)
            orderbook.add_modify_delete(order, ASK)

        print(orderbook)

if __name__ == "__main__":
   # speed_test()

     engine = BinanceTradeEngine()
     engine.trader = Test()
     engine.start()
