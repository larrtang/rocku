from OrderBook import OrderBook


class MarketState:
    """Market state and information that trading reacts upon"""
    def __init__(self,
                 market):
        self.market = market
        self.orderBook = OrderBook(market)


if __name__ == "__main__":
    ## TESTS ##
    mkt = MarketState('BTCUSD')
    print(mkt.orderBook)
