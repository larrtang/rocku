from exchange import Exchange
from coinbase.wallet.client import Client


class Coinbase(Exchange):
    API_ENDPT = 'https://api.pro.coinbase.com/'

    def __init__(self):
        super().__init__()
        self.api_key = ''
        self.api_secret = ''
        self.client = Client(self.api_key, self.api_secret)


    def getLastTradedPrice(self, pair):
        return self.client.get_spot_price(currency_pair = pair)['amount']       



