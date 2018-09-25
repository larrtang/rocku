from exchange import Exchange
from coinbase.wallet.client import Client


class Coinbase(Exchange):
    API_ENDPT = 'https://api.pro.coinbase.com/'

    def __init__(self):
        self.assets = {
            'btc' : 40,
            'eth' : 0,
            'usd' : 10000000000
        }
        self.api_key = '1408e8172c342f0278fd8c3dab847354'
        self.api_secret = 'vCpeLBQpfqj5Ta37qcBkWH+fg//6CoAjjmWRVGqEl7Izu18toEyCcooL/p1N7+ar7eYvYKFskTrXwQVk2+AscQ=='
        self.client = Client(self.api_key, self.api_secret)
        self.account_id = ''

        self.taker_fee = 0.000

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

