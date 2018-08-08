from exchange import Exchange
from binance.client import Client


class Binance(Exchange):

    def __init__(self):
        super().__init__()
        self.api_key = ''
        self.api_secret = ''
        self.client = Client(self.api_key, self.api_secret)
        self.fee_rate = 0.001
        
    def getMarketDepth(self, sym):
        return client.get_order_book(symbol=sym)

    def getLastTradedPrice(self, pair):
        tickers = self.client.get_all_tickers()
        if pair == 'BTCUSDT':
            return float(tickers[11]['price'])
        elif pair == 'ETHUSDT':
            return float(tickers[12]['price'])

                
    def getPortfolioValue(self):
        value = 0
        for k, v in self.assets.items():
            if k == 'btc':
                value += v * self.getLastTradedPrice('BTCUSDT')
            if k == 'eth':
                value += v * self.getLastTradedPrice('ETHUSDT')
            if k == 'usd':
                value += v

        return value

    def pretend_buy_BTC(self):
        btc_usd = self.getLastTradedPrice('BTCUSDT')
        btc_amount = (self.position_sizes['usd'] * (1-self.fee_rate)) / btc_usd
        
        self.assets['btc'] += btc_amount
        self.assets['usd'] -= self.position_sizes['usd']
    
    
    def pretend_sell_BTC(self):         
        btc_usd = self.getLastTradedPrice('BTCUSDT')
        btc_amount = (self.position_sizes['usd'] * (1-self.fee_rate)) / btc_usd
        
        self.assets['btc'] -= btc_amount
        self.assets['usd'] += self.position_sizes['usd']