from exchange import Exchange
from coinbase.wallet.client import Client


class Coinbase(Exchange):
    API_ENDPT = 'https://api.pro.coinbase.com/'

    def __init__(self):
        super().__init__()
        self.api_key = ''
        self.api_secret = ''
        self.client = Client(self.api_key, self.api_secret)
        self.account_id = ''

    def getLastTradedPrice(self, pair):
        return float(self.client.get_spot_price(currency_pair = pair)['amount'])   

    def getPortfolioValue(self):
        value = 0
        for k, v in self.assets.items():
            if k == 'btc':
                value += v * self.getLastTradedPrice('BTC-USD')
            if k == 'eth':
                value += v * self.getLastTradedPrice('ETH-USD')
            if k == 'usd':
                value += v

        return value

    def buy(self, currency, amount):
        order = self.client.buy(self.account_id, amount=amount, currency=currency)
        order.commit()
        return order 

    def sell(self, currency, amount):
        order = self.client.sell(self.account_id, amount=amount, currency=currency)
        order.commit()
        return order

