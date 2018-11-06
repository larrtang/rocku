from binance.client import Client
import threading
import time
from math import floor

class slave(threading.Thread):

    def __init__ (self, m, index):
        threading.Thread.__init__(self)
        self.market = m
        self.ma = []
        self.prev_ma = []
        self.num_ma = 2
        self.ma_len = [70, 40]
        self.slope_thresh = 1.0004
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
    
    def run(self):
        while True:
            tickers = self.client.get_all_tickers()
            price = float(tickers[self.index]['price'])
            
            quantity = round((self.btc_start/2)/price,3)
            #check if only trades integer quantities
            if quantity > 1:
                quantity = floor(quantity)


            for i in range(self.num_ma):
                self.ma[i].append(price)
            
                if len(self.ma[i]) > self.ma_len[i]:
                    self.ma[i].pop(0)
            
            self.ready = len(self.ma[0]) == self.ma_len[0]

            if not self.ready:
                print('.')
            else:
               
                
                ma0 = float(sum(self.ma[0]))/float(self.ma_len[0])
                ma1 = float(sum(self.ma[1]))/float(self.ma_len[1])
                print('ma:',ma0,ma1)
                
                if self.first:
                    print('-->> Starting:', self.market)
                    self.p_ma0 = ma0
                    self.p_ma1 = ma1
                    self.first = False
                    time.sleep(60)
                    continue

                dma0 = ma0/self.p_ma0
                dma1 = ma1/self.p_ma1
                print('dma:', dma0, dma1)
                if self.holding == False and dma0 > 1:

                    if ma1/ma0 < 1.003 and ma1/ma0 >= 0.998 and dma1 > self.slope_thresh:
                        self.holding = True
                        order = None
                        try:
                            #print('buy')
                            order = self.client.order_market_buy(
                            symbol=self.market,
                            quantity=quantity)
                            self.fix_quant = quantity
                        except Exception as e:
                            print(e)
                            self.holding = False
                            self.fix_quant = 0

                        print(order)
                        self.buy_price = price
                if self.holding:
                    if dma1 <= 1 or float(price)/float(self.buy_price) < self.stop_loss:
                        self.holding = False
                        order = None
                        try:
                            order = self.client.order_market_sell(
                            symbol=self.market,
                            quantity=self.fix_quant)
                        except Exception as e:
                            print(e)
                            self.holding = True
                        print(order)

                self.p_ma0 = ma0
                self.p_ma1 = ma1
            time.sleep(60)        