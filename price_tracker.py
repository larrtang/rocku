from Coinbase import Coinbase
from Binance import Binance
from engine import Engine
from Poloniex import poloniex
import sys

class C:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

b = Binance()
p = poloniex()
engine = Engine()



while True:
    polo_price = float(p.getLastTradingPrice('BTC_XRP'))
    binance_price = float(b.client.get_all_tickers()[88]['price'])
    percent_difference = (polo_price - binance_price)/min(polo_price, binance_price)    

    pd = str(percent_difference)
    if (percent_difference) > engine.Threshold:
        pd = C.OKBLUE + str(percent_difference) + C.ENDC
    elif abs(percent_difference) > engine.Threshold:
        pd = C.OKGREEN + str(percent_difference) + C.ENDC
    
    print polo_price, '\t' , binance_price, '\t', pd 
    
