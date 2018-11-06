from binance.client import Client
import threading
import time
from math import floor



'''
The ADX is a combination of two other indicators developed by Wilder, the positive directional indicator (abbreviated +DI) and negative directional indicator (-DI).[2] The ADX combines them and smooths the result with a smoothed moving average.

To calculate +DI and -DI, one needs price data consisting of high, low, and closing prices each period (typically each day). One first calculates the directional movement (+DM and -DM):

UpMove = today's high − yesterday's high
DownMove = yesterday's low − today's low
if UpMove > DownMove and UpMove > 0, then +DM = UpMove, else +DM = 0
if DownMove > UpMove and DownMove > 0, then -DM = DownMove, else -DM = 0
After selecting the number of periods (Wilder used 14 days originally), +DI and -DI are:

+DI = 100 times the smoothed moving average of (+DM) divided by average true range
-DI = 100 times the smoothed moving average of (-DM) divided by average true range
The smoothed moving average is calculated over the number of periods selected, and the average true range is a smoothed average of the true ranges. Then:

ADX = 100 times the smoothed moving average of the absolute value of (+DI − -DI) divided by (+DI + -DI)
Variations of this calculation typically involve using different types of moving averages, such as an exponential moving average, a weighted moving average or an adaptive moving average[3].
'''

class slave(threading.Thread):

    def __init__ (self, m, index):
        threading.Thread.__init__(self)
        self.market = m
        self.ma_list = []
        self.ma_len = 14
        self.index = index

        for i in range(self.num_ma):
            self.ma.append([])
            self.prev_ma.append([])

        self.api_key = ''
        self.api_secret = ''
        self.client = Client(self.api_key, self.api_secret)
        self.ready = False
        print('--> Initalizing:', self.market)
        self.holding = False
        self.btc_start = float(self.client.get_asset_balance(asset='BTC')['free'])
        self.fix_quant = 0
        self.first = True
        self.stop_loss = 0.97
        self.buy_price = 0
        self.p_ma0 = 0
        self.p_ma1 = 0
        self.prev_price = 0

        self.responses = []
        self.length = 14
        

        def ws_handler(msg):
            if len(self.responses) == 0:
                self.responses.append(msg)
            if self.responses[len(self.responses)-1]['k']['t'] = msg['k']['t']:
                self.responses[len(self.responses)-1] = msg
            else:
                self.responses.append(msg)
                
        self.bm = BinanceSocketManager(client, user_timeout=60)
        self.conn_key = bm.start_kline_socket('RVNBTC', ws_handler)# then start the socket manager
        self.bm.start()



    def run(self):
        while True:
            tickers = self.client.get_all_tickers()
            price = float(tickers[self.index]['price'])
            
            quantity = round((self.btc_start/2)/price,3)
            #check if only trades integer quantities
            if quantity > 1:
                quantity = floor(quantity)


            if len(self.responses) > 1:
                upmove = self.responses[-1]['k']['h'] - self.responses[-2]['k']['h']
                downmove = self.response[-2]['k']['l'] - self.responses[-1]['k']['l']

                Dup = 0
                Ddown = 0
                if upmove > downmove and upmove > 0:
                    Dup = upmove
                if downmove > upmove and downmove > 0:
                    Ddown = downmove



            self.prev_price = price
            time.sleep(60)        