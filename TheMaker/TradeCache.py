import numpy as np

BID = 'b'
ASK = 'a'

class TradeCache:
    size = 200
    bids = []
    asks = []
    last_trades = []

    def __init__(self, last_trade_price: float):
        self.bids = np.linspace(last_trade_price - 1, last_trade_price + 1, self.size + 1)[0:-1]
        self.asks = np.linspace(last_trade_price - 1, last_trade_price + 1, self.size + 1)[0:-1]
        self.last_trades = np.linspace(last_trade_price - 1, last_trade_price + 1, self.size + 1)[0:-1]

    def update(self, last_trade_price, side):
        if side == BID:
            self.bids[-1] = last_trade_price
            self.asks[-1] = self.asks[-2]
        else:
            self.bids[-1] = self.bids[-2]
            self.asks[-1] = last_trade_price

        self.last_trades[-1] = last_trade_price

        #TODO: ????
        self.bids = np.append(self.bids[1:], 0.0)
        self.asks = np.append(self.asks[1:], 0.0)
        self.last_trades = np.append(self.last_trades[1:], 0.0)

