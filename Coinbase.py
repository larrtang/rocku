from exchange import Exchange
from coinbase.wallet.client import Client
from time import sleep

class Coinbase(Exchange):
    API_ENDPT = 'https://api.pro.coinbase.com/'

    def __init__(self):
        super().__init__()
        self.api_key = ''
        self.api_secret = ''
        self.client = Client(self.api_key, self.api_secret)
        self.fee_rate = 0.0149

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

    def pretend_buy_BTC(self):         
        btc_usd = self.getLastTradedPrice('BTC-USD')
        btc_amount = (self.position_sizes['usd'] * (1-self.fee_rate)) / btc_usd
        
        self.assets['btc'] += btc_amount
        self.assets['usd'] -= self.position_sizes['usd']
    

    def pretend_sell_BTC(self):         
        btc_usd = self.getLastTradedPrice('BTC-USD')
        btc_amount = (self.position_sizes['usd'] * (1-self.fee_rate)) / btc_usd
        
        self.assets['btc'] -= btc_amount
        self.assets['usd'] += self.position_sizes['usd']

