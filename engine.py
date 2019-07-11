from Coinbase import Coinbase
from Binance import Binance
from Poloniex import poloniex

import cbpro
import sys
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Engine:

    def __init__(self):
        self.start_value = 0
        self.coinbase = Coinbase()
        self.binance = Binance()
        self.polo = poloniex()
        self.Threshold = 0.0021

        self.num_trades = 0

        self.order_volume = {
            'btc' : 0.5,
            'eth' : 1,
            'usd' : 1000,
            'xrp' : 100
        }
        self.start_value = 0

    def getTotalPortfolioValue(self):
        btc,xrp = self.polo.getPortfolioValue() 
        btc1,xrp1 = self.binance.getPortfolioValue()
        btc += btc1
        xrp += xrp1
        return btc + xrp * float(self.binance.client.get_all_tickers()[88]['price'])

    
    def checkXRPBTC(self):
        #coinbase_btc = self.coinbase.getLastTradedPrice('BTC-USD')
        #binance_btc = self.binance.getLastTradedPrice('BTCUSDT')
        
        binanceOB = self.binance.client.get_order_book(symbol='XRPBTC', limit= 10)
        #coinbaseOB = cbpro.PublicClient().get_product_order_book('btc-usd', level=2)
        poloOB = self.polo.getMarketDepth('BTC_XRP')

        polo_price = float(self.polo.getLastTradingPrice('BTC_XRP'))
        binance_price = float(self.binance.client.get_all_tickers()[88]['price'])

        #print polo_price, binance_price 
        
        percent_difference = (polo_price - binance_price)/min(polo_price, binance_price)
    
        if abs(percent_difference) > self.Threshold:
            self.num_trades += 1
            print '.',
            sys.stdout.flush()
            #print bcolors.OKBLUE+'Trading:'+ bcolors.ENDC, percent_difference,'\t', polo_price, binance_price
            if percent_difference > 0:
                #self.coinbase.sell('btc',self.order_volume['btc'])
                self.polo.assets['xrp'] -= self.order_volume['xrp']
                self.polo.assets['btc'] += (1-self.polo.maker_fee)*self.order_volume['xrp'] * polo_price

                #self.binance.buy('BTCUSDT',self.order_volume['btc'])
                self.binance.assets['xrp'] += self.order_volume['xrp'] 
                self.binance.assets['btc'] -= (1+self.binance.taker_fee)*self.order_volume['xrp'] * binance_price

            else:
                #self.coinbase.buy('btc',self.order_volume['btc'])
                self.polo.assets['xrp'] += self.order_volume['xrp']
                self.polo.assets['btc'] -= (1+self.polo.maker_fee)*self.order_volume['xrp'] * polo_price

                #self.binance.sell('BTCUSDT',self.order_volume['btc'])
                self.binance.assets['xrp'] -= self.order_volume['xrp']
                self.binance.assets['btc'] += (1-self.binance.taker_fee)*self.order_volume['xrp'] * binance_price


            #delay to sim live trading (wont be making the same trade over andd over again if the prices dont change)
            time.sleep(5)
    
    
    def print_info(self):
        print 
        print 'number of Trades:', self.num_trades
        print 'Percent Change:  ', (self.getTotalPortfolioValue()-self.start_value)/self.start_value
        print 'Profit/Loss:     ', (self.getTotalPortfolioValue()-self.start_value)
        print 'Polo:            ', [str(i) for k, i in self.polo.assets.items()]
        print 'Binance:         ', [str(i) for k, i in self.binance.assets.items()]
        print 'Total Bitcoin:   ', self.binance.assets['btc'] + self.polo.assets['btc']
        

    def run(self):
        self.start_value = self.getTotalPortfolioValue()
        while self.num_trades < 100:
            #s = ['XRPUSDT', 'BTCUSDT', 'ETHUSDT']
            #start = time.clock()
            
            self.checkXRPBTC()

            #print time.clock()-start
            
            #ticks = self.binance.client.get_all_tickers()
            #for t in ticks:
            #    if t['symbol'] in s:
            #        print t['symbol'], '\t', float(t['price'])*1.00
            #self.print_info()

    def __del__(self):
        self.print_info()