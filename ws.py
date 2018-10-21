from binance.client import Client
from binance.websockets import BinanceSocketManager

api_key = 'IUxQsnE724D1R9zKbwGy5YnFQ4uFtGbeHglVyGGv8o25mZA4L5PGpoCCKQJkHHmg'
api_secret = 'TvaHvvWTxZTzpfDsqDvmEJLf0n3Q5xVjZvxaNReo21qa7y8mIAYjDVmb4ajtCnEZ'
client = Client(api_key, api_secret)

def ws_handler(msg):
    print("message type: {}".format(msg['e']))
    print(msg)

bm = BinanceSocketManager(client, user_timeout=60)
conn_key = bm.start_depth_socket('MDABTC', ws_handler)
# then start the socket manager
bm.start()