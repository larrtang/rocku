from Coinbase import Coinbase
from Binance import Binance

class Engine:

    def __init__(self):

        self.coinbase = Coinbase()
        self.binance = Binance()

        self.Threashold = 0.002

        self.order_volume = {
            'btc' : 0.5,
            'eth' : 1,
            'usd' : 1000
        }

    def getTotalPortfolioValue(self):
        return self.coinbase.getPortfolioValue() + self.binance.getPortfolioValue()

    
    def checkBTCUSDT(self):
        coinbase_btc = self.coinbase.getLastTradedPrice('BTC-USD')
        binance_btc = self.binance.getLastTradedPrice('BTCUSDT')
        
        percent_difference = (coinbase_btc - binance_btc)/min(coinbase_btc, binance_btc)
        if abs(percent_difference) > self.Threashold:
            print 'trading:', percent_difference,'\t', coinbase_btc, binance_btc
            if percent_difference > 0:
                #self.coinbase.sell('btc',self.order_volume['btc'])
                self.coinbase.assets['btc'] -= self.order_volume['btc']
                self.coinbase.assets['usd'] += (1-self.coinbase.taker_fee)*self.order_volume['btc'] * coinbase_btc

                #self.binance.buy('BTCUSDT',self.order_volume['btc'])
                self.binance.assets['btc'] += self.order_volume['btc'] 
                self.binance.assets['usd'] -= (1+self.binance.taker_fee)*self.order_volume['btc'] * binance_btc

            else:
                #self.coinbase.buy('btc',self.order_volume['btc'])
                self.coinbase.assets['btc'] += self.order_volume['btc']
                self.coinbase.assets['usd'] -= (1+self.coinbase.taker_fee)*self.order_volume['btc'] * coinbase_btc

                #self.binance.sell('BTCUSDT',self.order_volume['btc'])
                self.binance.assets['btc'] -= self.order_volume['btc']
                self.binance.assets['usd'] += (1-self.binance.taker_fee)*self.order_volume['btc'] * binance_btc


    

    def run(self):
        start_value = self.getTotalPortfolioValue()
        while True:
            #s = ['XRPUSDT', 'BTCUSDT', 'ETHUSDT']
            self.checkBTCUSDT()
            #ticks = self.binance.client.get_all_tickers()
            #for t in ticks:
            #    if t['symbol'] in s:
            #        print t['symbol'], '\t', float(t['price'])*1.005
            print 'Percent Change:', (self.getTotalPortfolioValue()-start_value)/start_value
            print 'Coinbase: \t', [str(i) for k, i in self.coinbase.assets.items()]
            print 'Binance: \t', [str(i) for k, i in self.binance.assets.items()]
            print

