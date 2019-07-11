#!/usr/bin/python3
from binance.client import Client
from ma_slave import slave
import time

class C:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
api_key = ''
api_secret = ''
client = Client(api_key, api_secret)
btc_start = float(client.get_asset_balance(asset='BTC')['free'])

t = slave('RVNBTC', 377)
t.start()


while True:
    try:
        percentchange = (float(client.get_asset_balance(asset='BTC')['free']) - btc_start)/float(btc_start)

        if (percentchange >= 0): print(C.OKGREEN , '+' +str(percentchange) +'%'+ C.ENDC) 
        else: print(C.OKBLUE + str(percentchange) +'%'+ C.ENDC) 
        time.sleep(10)
    except Exception as e:
        print(e)
        continue