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
            return tickers[11]['price']
        elif pair == 'ETHUSDT':
            return tickers[12]['price']

                
