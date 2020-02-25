from MarketState import MarketState
from OrderBook import OrderBook, Order

BID = 'b'
ASK = 'a'


def can_buy(market_state: MarketState) -> bool:
    return market_state.portfolio_dict[market_state.base] > 0.0


def can_sell(market_state: MarketState) -> bool:
    return market_state.portfolio_dict[market_state.target] > 0.0


class TestTrader:
    def __init__(self):
        self.DEFAULT_POSITION_QUANTITY = 0.01
        self.MAX_SPREAD_WIDTH = 3.1
        self.MIN_SPREAD_WIDTH = 1
        self.AUTO_CANCEL_PRICE_THRESHOLD = 3
        self.AUTO_CANCEL_DEPTH_THRESHOLD = 25
        self.do_once_done = False

    def submit_depth_order(self, market_state: MarketState, side, depth, quantity):
        # depth starts at 0 (top of book)
        if side == BID:
            price = market_state.order_book.bids.sortedOrderList[depth].price + market_state.MIN_TICK
            new_order = Order(price=price,
                              quantity=quantity,
                              pos_quantity=quantity,
                              side=side)
            market_state.new_limit_buy(new_order)
        else:
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

    def on_trade_event(self, market_state: MarketState):
        #self.do_once_beginning(market_state)
        mid_dist = 0.5
        if market_state.num_alerts >= 2:
            mid_dist *= 2

        b = -mid_dist
        if market_state.calc_value_ratio() > 0.2:
            b -= 0.2

        if len(market_state.open_orders.bids) == 0:
            if can_buy(market_state):
                self.submit_depth_price_order(market_state,
                                              side=BID,
                                              depth=0,
                                              price_offset=b,
                                              quantity=self.DEFAULT_POSITION_QUANTITY)
        if len(market_state.open_orders.asks) == 0:
            if can_sell(market_state):
                ask_position_quantity = self.DEFAULT_POSITION_QUANTITY
                if market_state.calc_value_ratio() > 0.2:
                    ask_position_quantity = self.DEFAULT_POSITION_QUANTITY * 2

                self.submit_depth_price_order(market_state,
                                              side=ASK,
                                              depth=0,
                                              price_offset=mid_dist,
                                              quantity=ask_position_quantity)

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


    def on_book_event(self, market_state : MarketState):
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

            else:
                break
        for i in range(len(abook)-1, -1, -1):
            if (abook[i].price > market_state.last_trade.price + self.AUTO_CANCEL_PRICE_THRESHOLD) \
            or (market_state.order_book.getDepthOfPrice(abook[i].price, side='a') >= self.AUTO_CANCEL_DEPTH_THRESHOLD):
                market_state.cancel_limit_sell(abook[i])
                #abook.pop(i)
            else:
                break
        # if len(bbook) == market_state.open_orders.depth or len(abook) == market_state.open_orders.depth:
        #     print(market_state.open_orders)


    def calc_desired_spread(self, market_state: MarketState, width=2):
        ratio = market_state.calc_value_ratio()
        b = -width * ratio
        a = b + width
        return b, a
