from MarketState import MarketState
from OrderBook import OrderBook, Order


def can_buy(market_state : MarketState, order : Order):
    return market_state.portfolio_dict[market_state.base] - order.price*order.position_quantity > 0


def can_sell(market_state : MarketState, order : Order):
    return market_state.portfolio_dict[market_state.target] - order.position_quantity > 0


class TestTrader:
    def __init__(self):
        self.DEFAULT_POSITION_QUANTITY = 1.0

    def on_trade_event(self, market_state : MarketState):
        new_bid_order = Order(price=market_state.last_trade.price - 1,
                                     quantity=self.DEFAULT_POSITION_QUANTITY,
                                     pos_quantity=self.DEFAULT_POSITION_QUANTITY,
                                     side='b')
        if can_buy(market_state, new_bid_order):
            market_state.new_limit_buy(new_bid_order)

        new_ask_order = Order(price=market_state.last_trade.price + 1,
                                      quantity=self.DEFAULT_POSITION_QUANTITY,
                                      pos_quantity=self.DEFAULT_POSITION_QUANTITY,
                                      side='a')
        if can_sell(market_state, new_ask_order):
            market_state.new_limit_sell(new_ask_order)



    def on_book_event(self, market_state : MarketState):
        pass

