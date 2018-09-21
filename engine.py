from Coinbase import Coinbase
from Binance import Binance

class Engine:

    def __init__(self):
        self.coinbase = Coinbase()
        self.binance = Binance()
        
        self.Threashold = 0.0006

         self.order_volume = {
            'btc' : 0.5,
            'eth' : 1,
            'usd' : 1000
        }

    def getTotalPortfolioValue(self):
        return self.coinbase.getPortfolioValue() + self.binance.getPortfolioValue()

    def run(self):
        while True:
            coinbase_btc = self.coinbase.getLastTradedPrice('BTC-USD')
            binance_btc = self.binance.getLastTradedPrice('BTCUSDT')

            percent_difference = (coinbase_btc - binance_btc)/min(coinbase_btc, binance_btc)
            if abs(percent_difference) > self.Threashold:
                if percent_difference > 0:
                    self.coinbase.buy('btc',self.order_volume['btc'])
                    self.coinbase.assets['btc'] += self.order_volume['btc']
                    self.coinbase.assets['usd'] -= self.order_volume['btc'] * coinbase_btc

                    self.binance.sell('BTCUSDT',self.order_volume['btc'])
                    self.binance.assets['btc'] -= self.order_volume['btc'] 
                    self.binance.assets['usd'] += self.order_volume['btc'] * binance_btc

                else:
                    self.coinbase.sell('btc',self.order_volume['btc'])
                    self.coinbase.assets['btc'] -= self.order_volume['btc']
                    self.coinbase.assets['usd'] += self.order_volume['btc'] * coinbase_btc

                    self.binance.buy('BTCUSDT',self.order_volume['btc'])
                    self.binance.assets['btc'] += self.order_volume['btc']
                    self.binance.assets['usd'] -= self.order_volume['btc'] * binance_btc


