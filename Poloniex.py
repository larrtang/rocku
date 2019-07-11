from exchange import Exchange
from poloniex import Poloniex

class poloniex(Exchange):
    def __init__(self):
        self.client = Poloniex()

        self.assets = {
            'btc' : 2,
            'eth' : 0,
            'usd' : 10000000000,
            'xrp' : 10000
        }
    
        self.maker_fee = 0.001 * 1  
    def getMarketDepth(self, sym):
        return self.client.returnOrderBook(currencyPair = sym, depth = 10)
    
    def getLastTradingPrice(self, sym):
        return self.client.returnTicker()[sym]['last']

    def getPortfolioValue(self):
        return self.assets['btc'], self.assets['xrp']
        #return float(self.assets['btc'] + self.assets['xrp'] * float(self.client.returnTicker()['BTC_XRP']['last']))
