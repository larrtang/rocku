from exchange import Exchange
from poloniex import Poloniex

class Poloniex(Exchange):
    def __init__(self):
        self.client = Poloniex()

ticker = polo.returnTicker()['BTC_ETH']
print(ticker)