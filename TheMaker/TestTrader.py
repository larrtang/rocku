from MarketState import MarketState
from OrderBook import OrderBook, Order

BID = 'b'
ASK = 'a'

def can_buy(market_state : MarketState, order : Order):
    return True
    return market_state.power[market_state.base] - order.price*order.position_quantity > 0


def can_sell(market_state : MarketState, order : Order):
    return True
    return market_state.power[market_state.target] - order.position_quantity > 0


class TestTrader:
    def __init__(self):
        self.DEFAULT_POSITION_QUANTITY = 0.01
        self.MAX_SPREAD_WIDTH = 3.1
        self.MIN_SPREAD_WIDTH = 1
        self.AUTO_CANCEL_THRESHOLD = 2.5
        self.do_once_done = False

    def submit_depth_order(self, market_state: MarketState, side, depth, quantity):
        # depth starts at 0 (top of book)
        if side == BID:
            price = market_state.order_book.bids.sortedOrderList[depth].price + market_state.MIN_TICK
            new_order = Order(price=price,
                              quantity=quantity,
                              position_quantity=quantity,
                              side=side)
            market_state.new_limit_buy(new_order, side=side)
        else:
            price = market_state.order_book.asks.sortedOrderList[depth].price - market_state.MIN_TICK
            new_order = Order(price=price,
                              quantity=quantity,
                              position_quantity=quantity,
                              side=side)
            market_state.new_limit_sell(new_order, side=side)
        return new_order

    def submit_depth_price_order(self, market_state: MarketState, side, depth, price_offset, quantity):
        """price_offset - distance from mid price which the order has to be, or the depth will increase"""
        # check if price offsets are crossed with mid price
        # depth starts at 0 (top of book)
        d = depth
        mid = market_state.order_book.getMidPrice()
        target_price = mid + price_offset
        if side == BID:
            if target_price > mid:
                return None
            price = market_state.order_book.bids.sortedOrderList[d].price + market_state.MIN_TICK
            # new bid must be less than target price, or at least target price
            while price > target_price:
                d += 1
                price = market_state.order_book.bids.sortedOrderList[d].price + market_state.MIN_TICK
            new_order = Order(price=price,
                              quantity=quantity,
                              position_quantity=quantity,
                              side=side)
            market_state.new_limit_buy(new_order, side=side)
        else:
            if target_price < mid:
                return None
            price = market_state.order_book.asks.sortedOrderList[depth].price - market_state.MIN_TICK
            # new ask must be greater than target price, or at least target price
            while price < target_price:
                d += 1
                price = market_state.order_book.bids.sortedOrderList[d].price + market_state.MIN_TICK
            new_order = Order(price=price,
                              quantity=quantity,
                              position_quantity=quantity,
                              side=side)
            market_state.new_limit_sell(new_order, side=side)
        return new_order

    def on_trade_event(self, market_state: MarketState):
        # self.do_once_beginning(market_state)
        b, a = self.calc_desired_spread(market_state)
        new_bid_order = Order(price=market_state.last_trade.price + b,
                              quantity=self.DEFAULT_POSITION_QUANTITY,
                              pos_quantity=self.DEFAULT_POSITION_QUANTITY,
                              side='b')
        market_state.new_limit_buy(new_bid_order)

        new_ask_order = Order(price=market_state.last_trade.price + a,
                              quantity=self.DEFAULT_POSITION_QUANTITY,
                              pos_quantity=self.DEFAULT_POSITION_QUANTITY,
                              side='a')
        market_state.new_limit_sell(new_ask_order)

        self.auto_cancel_orders(market_state)

    def do_once_beginning(self, market_state: MarketState):
        if not self.do_once_done:
            self.do_once_done = True
            new_bid_order = Order(price=market_state.last_trade.price - 1,
                                  quantity=self.DEFAULT_POSITION_QUANTITY,
                                  pos_quantity=self.DEFAULT_POSITION_QUANTITY,
                                  side='b')
            market_state.new_limit_buy(new_bid_order)

            new_ask_order = Order(price=market_state.last_trade.price + 1,
                                  quantity=self.DEFAULT_POSITION_QUANTITY,
                                  pos_quantity=self.DEFAULT_POSITION_QUANTITY,
                                  side='a')
            market_state.new_limit_sell(new_ask_order)


    def on_book_event(self, market_state : MarketState):
        self.auto_cancel_orders(market_state)

    def auto_cancel_orders(self, market_state: MarketState):
        """Cancels orders that have been pushed off the book"""
        bbook = market_state.open_orders.bids.sortedOrderList
        abook = market_state.open_orders.asks.sortedOrderList
        for i in range(len(bbook)-1, -1, -1):
            if bbook[i].price < market_state.last_trade.price - self.AUTO_CANCEL_THRESHOLD:
                market_state.cancel_limit_buy(bbook[i])
                # bbook.pop(i)
            else:
                break
        for i in range(len(abook)-1, -1, -1):
            if abook[i].price > market_state.last_trade.price + self.AUTO_CANCEL_THRESHOLD:
                market_state.cancel_limit_sell(abook[i])
                # abook.pop(i)
            else:
                break
        # if len(bbook) == market_state.open_orders.depth or len(abook) == market_state.open_orders.depth:
        #     print(market_state.open_orders)

    def calc_desired_spread(self, market_state: MarketState):
        ratio = market_state.calc_value_ratio()
        width = 3
        b = -(width) * ratio
        a = b + width
        return b, a
