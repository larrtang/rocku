from Coinbase import Coinbase
from Binance import Binance

class Engine:

    def __init__(self):
        self.coinbase = Coinbase()
        self.binance = Binance()
        
        self.Threashold = 0.0006

    def getTotalPortfolioValue(self):
        return self.coinbase.getPortfolioValue() + self.binance.getPortfolioValue()

    def run(self):
        while True:
            coinbase_btc = self.coinbase.getLastTradedPrice('BTC-USD')
            binance_btc = self.binance.getLastTradedPrice('BTCUSDT')

            percent_difference = (coinbase_btc - binance_btc)/min(coinbase_btc, binance_btc)
            if abs(percent_difference) > self.Threashold:
                