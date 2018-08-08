from Coinbase import Coinbase
from Binance import Binance
from time import sleep

REBALANCE_FREQ = 10
class Engine:

    def __init__(self):
        self.coinbase = Coinbase()
        self.binance = Binance()
        
        self.Threashold = 0.0013
        self.pretend_delay = 0.1

    def getTotalPortfolioValue(self):
        return self.coinbase.getPortfolioValue() + self.binance.getPortfolioValue()

    def run(self):
        start_value = self.getTotalPortfolioValue()
        rebalance_check_counter = 0

        while True:
            coinbase_btc = self.coinbase.getLastTradedPrice('BTC-USD')
            binance_btc = self.binance.getLastTradedPrice('BTCUSDT')

            percent_difference = (coinbase_btc - binance_btc)/min(coinbase_btc, binance_btc)
            if abs(percent_difference) > self.Threashold:

                print(str(percent_difference) + '\t\t' + 'TRADING')
                if percent_difference > 0:
                    sleep(self.pretend_delay)     #pretend delay
                    self.coinbase.pretend_sell_BTC()
                    self.binance.pretend_buy_BTC()
                else:
                #    sleep(0.05)     #pretend delay
                    self.coinbase.pretend_buy_BTC()
                    self.binance.pretend_sell_BTC()

                print('Percent change: ' + str((self.getTotalPortfolioValue()-start_value)/start_value))
                print()
                print('Coinbase:')
                print(self.coinbase.assets)
                print()
                print('Binance:')
                print(self.binance.assets)
                print()
                print()
                print()

                rebalance_check_counter += 1
                if rebalance_check_counter > REBALANCE_FREQ:
                    rebalance_check_counter = 0
                    self.rebalanceAssets()

    def rebalanceAssets(self):
        assets = {
            'btc' : 0,
            'eth' : 0,
            'usd' : 0
        }
        assets['btc'] = (self.coinbase.assets['btc']+self.binance.assets['btc'])/2
        assets['eth'] = (self.coinbase.assets['eth']+self.binance.assets['eth'])/2
        assets['usd'] = (self.coinbase.assets['usd']+self.binance.assets['usd'])/2

        self.coinbase.assets['btc'] = assets['btc']
        self.coinbase.assets['eth'] = assets['eth']
        self.coinbase.assets['usd'] = assets['usd']
        self.binance.assets['btc'] = assets['btc']
        self.binance.assets['eth'] = assets['eth']
        self.binance.assets['usd'] = assets['usd']
