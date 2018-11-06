from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
api_key = ''
api_secret = ''
client = Client(api_key, api_secret)

def ws_handler(msg):
    print("message type: {}".format(msg['e']))
    print(msg)

bm = BinanceSocketManager(client, user_timeout=60)
conn_key = bm.start_kline_socket('RVNBTC', ws_handler)# then start the socket manager
bm.start()