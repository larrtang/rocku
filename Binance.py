from exchange import Exchange
from binance.client import Client


class Binance(Exchange):

    def __init__(self):
        super().__init__()
        self.api_key = ''
        self.api_secret = ''
        self.client = Client(self.api_key, self.api_secret)

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