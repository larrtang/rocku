from exchange import Exchange
from binance.client import Client


class Binance(Exchange):

    def __init__(self):
        self.assets = {
            'btc' : 400,
            'eth' : 0,
            'usd' : 10000000000
        }
       
        self.api_key = 'IUxQsnE724D1R9zKbwGy5YnFQ4uFtGbeHglVyGGv8o25mZA4L5PGpoCCKQJkHHmg'
        self.api_secret = 'TvaHvvWTxZTzpfDsqDvmEJLf0n3Q5xVjZvxaNReo21qa7y8mIAYjDVmb4ajtCnEZ'
        self.client = Client(self.api_key, self.api_secret)
        
        self.taker_fee = 0.001
        # TODO: Get assets manually
    

    def getMarketDepth(self, sym):
        return self.client.get_order_book(symbol=sym)

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

        # return value
        return self.assets['usd']

    def buy(self, currency, amount):
        order = self.client.order_market_buy(symbol=currency, quantity=amount)
        return order

    def sell(self, currency, amount):
        order = self.client.order_market_sell(symbol=currency, quantity=amount)
        return order   

    def getBids(self, limit = 10):
        orders = self.client.get_order_book(symbol='BTCUSDT', limit= limit)
        return orders['bids']
        
    def getAsks(self, limit = 10):
        orders = self.client.get_order_book(symbol='BTCUSDT', limit= limit)
        return orders['asks']