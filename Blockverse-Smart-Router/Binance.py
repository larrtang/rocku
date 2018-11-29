from binance.client import Client
from binance.websockets import BinanceSocketManager


MARKET = {
'ETHBTC' : 0,
'BTCUSDT' : 11,
'ETHUSDT' : 12,
'MDABTC' : 48,
'ZRXBTC' : 25,
'BCCBTC' : 8,
'BATBTC' : 120,
'EOSBTC' : 5,
'RVNBTC' : 377,
'GOBTC'  : 371,
'MCOBTC' : 16,
'MFTBTC' : 347,
'DOCKBTC' : 362
}


class Binance:

    def __init__(self, market='MDABTC'):
       
        self.api_key = ''
        self.api_secret = ''
        self.client = Client(self.api_key, self.api_secret)
        self.order_book = self.client.get_order_book(symbol=market)
        self.old_order_book = self.order_book
        self.m = 1.04
        
        
        
        
        def websocket_handler(msg):
            # print("message type: {}".format(msg['e']))
            # print(msg)
            update_bids = msg['b']
            update_asks = msg['a']
            
           # print(update_bids)
           # print(update_asks)
            self.old_order_book = self.order_book

            for bid in update_bids:
                updated = False
                for b in range(len(self.order_book['bids'])):
                    if b >= len(self.order_book['bids']):
                        #self.order_book['bids'].append(bid)
                        pass
                    elif float(bid[0]) == float(self.order_book['bids'][b][0]):
                        if float(bid[1]) == 0:
                     #       print('pop')
                            self.order_book['bids'].pop(b)
                        else:
                            self.order_book['bids'][b][1] = bid[1]
                    #        print(self.order_book['bids'][b])
                        updated = True
                    elif float(bid[0]) > float(self.order_book['bids'][b][0]):
                        if float(bid[1]) != 0:
                            print('new')
                            self.order_book['bids'].insert(b, bid)
                        updated = True
                    if updated:
                        break
                if not updated:
                    #self.order_book['bids'].append(bid)
                   # pr
                   # int('fucked')
                   pass
            
            for ask in update_asks:
                updated = False
                for a in range(len(self.order_book['asks'])):
                    if a >= len(self.order_book['asks']):
                        #self.order_book['asks'].append(ask)
                        pass
                    elif float(ask[0]) == float(self.order_book['asks'][a][0]):
                        if float(ask[1]) == 0:
                            #print ('pop ask')
                            self.order_book['asks'].pop(a)
                        else:
                            self.order_book['asks'][a][1] = ask[1]               
                           # print (self.order_book['asks'][a] )        
                        updated = True
                    elif float(ask[0]) < float(self.order_book['asks'][a][0]):
                        #print(ask)
                        if float(ask[1]) != 0:
                            self.order_book['bids'].insert(a, ask)
                        updated = True
                    
                    if updated:
                        break
                if not updated:
                    #self.order_book['asks'].append(ask)
                    pass

        
        
        
        self.bm = BinanceSocketManager(self.client, user_timeout=60)
        self.conn_key = self.bm.start_depth_socket(market, websocket_handler)
        # # then start the socket manager
        #self.bm.start()
      
        self.taker_fee = 0.001 * 1
        # TODO: Get assets manually
    



    def getMarketDepth(self, sym):
        try:
            return self.client.get_order_book(symbol=sym)
            #print(len(self.order_book['bids']))
            #return self.order_book
        except:
            return None



    def getLastTradedPrice(self, pair):
        try:
            tickers = self.client.get_all_tickers()
        
            return self.m* float(tickers[MARKET[pair]]['price'])
        except Exception as e:
            print(e)
            return -1

        # if pair == 'BTCUSDT':
        #     return float(tickers[11]['price'])
        # elif pair == 'ETHUSDT':
        #     return float(tickers[12]['price'])
        # elif pair == 'MDABTC':
        #     return float(tickers[48]['price'])
        # elif pair == 'ZRXBTC':
        #     return float(tickers[25]['price'])

    
    
    
    def getMarketPrice(self, pair):
        return self.getLastTradedPrice(pair)




    def getPortfolioValue(self):
        return self.assets['btc'], self.assets['xrp']
        #return float(self.assets['btc'] + self.assets['xrp'] * float(self.client.get_all_tickers()[88]['price']))
        

    def market_buy(self, currency, amount):
        order = self.client.order_market_buy(symbol=currency, quantity=amount)
        return order

    def market_sell(self, currency, amount):
        order = self.client.order_market_sell(symbol=currency, quantity=amount)
        return order   

    def limit_buy(self, currency, amount, price):
        order = self.client.order_limit_buy(symbol=currency, quantity=amount, price=price)
        return order

    def limit_sell(self, currency, amount, price):
        order = self.client.order_limit_sell(symbol=currency, quantity=amount, price=price)
        return order   


    def getBids(self, limit = 10):
        orders = self.client.get_order_book(symbol='BTCUSDT', limit= limit)
        return orders['bids']
        
    def getAsks(self, limit = 10):
        orders = self.client.get_order_book(symbol='BTCUSDT', limit= limit)
        return orders['asks']
    

    def getOrderStatus(self, sym, orderID):
        return self.client.get_order(symbol=sym, orderId=orderID)

    def allOrdersFilled(self, sym):
        orders = self.client.get_open_orders(symbol=sym)
        return order is None or len(orders) == 0 
    

    def cancelOrder(self, sym, orderID):
        result = client.cancel_order(symbol=sym, orderId=orderID)
        return result
    
'''
Binance Ticker Table:

0 {'symbol': 'ETHBTC', 'price': '0.03148300'}
1 {'symbol': 'LTCBTC', 'price': '0.00813500'}
2 {'symbol': 'BNBBTC', 'price': '0.00150060'}
3 {'symbol': 'NEOBTC', 'price': '0.00255000'}
4 {'symbol': 'QTUMETH', 'price': '0.02070400'}
5 {'symbol': 'EOSETH', 'price': '0.02656200'}
6 {'symbol': 'SNTETH', 'price': '0.00017550'}
7 {'symbol': 'BNTETH', 'price': '0.00632800'}
8 {'symbol': 'BCCBTC', 'price': '0.06915700'}
9 {'symbol': 'GASBTC', 'price': '0.00081400'}
10 {'symbol': 'BNBETH', 'price': '0.04768800'}
11 {'symbol': 'BTCUSDT', 'price': '6603.50000000'}
12 {'symbol': 'ETHUSDT', 'price': '207.85000000'}
13 {'symbol': 'OAXETH', 'price': '0.00122420'}
14 {'symbol': 'DNTETH', 'price': '0.00012293'}
15 {'symbol': 'MCOETH', 'price': '0.02229600'}
16 {'symbol': 'MCOBTC', 'price': '0.00069900'}
17 {'symbol': 'WTCBTC', 'price': '0.00043770'}
18 {'symbol': 'WTCETH', 'price': '0.01382400'}
19 {'symbol': 'LRCBTC', 'price': '0.00001707'}
20 {'symbol': 'LRCETH', 'price': '0.00054198'}
21 {'symbol': 'QTUMBTC', 'price': '0.00065000'}
22 {'symbol': 'YOYOBTC', 'price': '0.00000475'}
23 {'symbol': 'OMGBTC', 'price': '0.00051300'}
24 {'symbol': 'OMGETH', 'price': '0.01630300'}
25 {'symbol': 'ZRXBTC', 'price': '0.00013453'}
26 {'symbol': 'ZRXETH', 'price': '0.00427098'}
27 {'symbol': 'STRATBTC', 'price': '0.00021890'}
28 {'symbol': 'STRATETH', 'price': '0.00695300'}
29 {'symbol': 'SNGLSBTC', 'price': '0.00000400'}
30 {'symbol': 'SNGLSETH', 'price': '0.00012713'}
31 {'symbol': 'BQXBTC', 'price': '0.00006323'}
32 {'symbol': 'BQXETH', 'price': '0.00202240'}
33 {'symbol': 'KNCBTC', 'price': '0.00006400'}
34 {'symbol': 'KNCETH', 'price': '0.00204390'}
35 {'symbol': 'FUNBTC', 'price': '0.00000221'}
36 {'symbol': 'FUNETH', 'price': '0.00007044'}
37 {'symbol': 'SNMBTC', 'price': '0.00000856'}
38 {'symbol': 'SNMETH', 'price': '0.00027297'}
39 {'symbol': 'NEOETH', 'price': '0.08112000'}
40 {'symbol': 'IOTABTC', 'price': '0.00007556'}
41 {'symbol': 'IOTAETH', 'price': '0.00240294'}
42 {'symbol': 'LINKBTC', 'price': '0.00005733'}
43 {'symbol': 'LINKETH', 'price': '0.00183160'}
44 {'symbol': 'XVGBTC', 'price': '0.00000222'}
45 {'symbol': 'XVGETH', 'price': '0.00007054'}
46 {'symbol': 'SALTBTC', 'price': '0.00011560'}
47 {'symbol': 'SALTETH', 'price': '0.00366200'}
48 {'symbol': 'MDABTC', 'price': '0.00027364'}
49 {'symbol': 'MDAETH', 'price': '0.00870300'}
50 {'symbol': 'MTLBTC', 'price': '0.00010690'}
51 {'symbol': 'MTLETH', 'price': '0.00337400'}
52 {'symbol': 'SUBBTC', 'price': '0.00001709'}
53 {'symbol': 'SUBETH', 'price': '0.00054062'}
54 {'symbol': 'EOSBTC', 'price': '0.00083560'}
55 {'symbol': 'SNTBTC', 'price': '0.00000551'}
56 {'symbol': 'ETCETH', 'price': '0.04712000'}
57 {'symbol': 'ETCBTC', 'price': '0.00148300'}
58 {'symbol': 'MTHBTC', 'price': '0.00000575'}
59 {'symbol': 'MTHETH', 'price': '0.00018260'}
60 {'symbol': 'ENGBTC', 'price': '0.00009463'}
61 {'symbol': 'ENGETH', 'price': '0.00300480'}
62 {'symbol': 'DNTBTC', 'price': '0.00000387'}
63 {'symbol': 'ZECBTC', 'price': '0.01923000'}
64 {'symbol': 'ZECETH', 'price': '0.61045000'}
65 {'symbol': 'BNTBTC', 'price': '0.00019988'}
66 {'symbol': 'ASTBTC', 'price': '0.00001471'}
67 {'symbol': 'ASTETH', 'price': '0.00046560'}
68 {'symbol': 'DASHBTC', 'price': '0.02380500'}
69 {'symbol': 'DASHETH', 'price': '0.75567000'}
70 {'symbol': 'OAXBTC', 'price': '0.00003880'}
71 {'symbol': 'BTGBTC', 'price': '0.00404700'}
72 {'symbol': 'BTGETH', 'price': '0.12900000'}
73 {'symbol': 'EVXBTC', 'price': '0.00008366'}
74 {'symbol': 'EVXETH', 'price': '0.00265270'}
75 {'symbol': 'REQBTC', 'price': '0.00000937'}
76 {'symbol': 'REQETH', 'price': '0.00029735'}
77 {'symbol': 'VIBBTC', 'price': '0.00000721'}
78 {'symbol': 'VIBETH', 'price': '0.00022882'}
79 {'symbol': 'TRXBTC', 'price': '0.00000373'}
80 {'symbol': 'TRXETH', 'price': '0.00011828'}
81 {'symbol': 'POWRBTC', 'price': '0.00002775'}
82 {'symbol': 'POWRETH', 'price': '0.00088401'}
83 {'symbol': 'ARKBTC', 'price': '0.00011680'}
84 {'symbol': 'ARKETH', 'price': '0.00372500'}
85 {'symbol': 'YOYOETH', 'price': '0.00015005'}
86 {'symbol': 'XRPBTC', 'price': '0.00007052'}
87 {'symbol': 'XRPETH', 'price': '0.00223694'}
88 {'symbol': 'MODBTC', 'price': '0.00015250'}
89 {'symbol': 'MODETH', 'price': '0.00485100'}
90 {'symbol': 'ENJBTC', 'price': '0.00000764'}
91 {'symbol': 'ENJETH', 'price': '0.00024240'}
92 {'symbol': 'STORJBTC', 'price': '0.00005472'}
93 {'symbol': 'STORJETH', 'price': '0.00173880'}
94 {'symbol': 'BNBUSDT', 'price': '9.92000000'}
95 {'symbol': 'YOYOBNB', 'price': '0.00317500'}
96 {'symbol': 'POWRBNB', 'price': '0.01826000'}
97 {'symbol': 'KMDBTC', 'price': '0.00019510'}
98 {'symbol': 'KMDETH', 'price': '0.00617700'}
99 {'symbol': 'NULSBNB', 'price': '0.11541000'}
100 {'symbol': 'RCNBTC', 'price': '0.00000479'}
101 {'symbol': 'RCNETH', 'price': '0.00015234'}
102 {'symbol': 'RCNBNB', 'price': '0.00317500'}
103 {'symbol': 'NULSBTC', 'price': '0.00017438'}
104 {'symbol': 'NULSETH', 'price': '0.00555676'}
105 {'symbol': 'RDNBTC', 'price': '0.00009306'}
106 {'symbol': 'RDNETH', 'price': '0.00296900'}
107 {'symbol': 'RDNBNB', 'price': '0.06194000'}
108 {'symbol': 'XMRBTC', 'price': '0.01620200'}
109 {'symbol': 'XMRETH', 'price': '0.51591000'}
110 {'symbol': 'DLTBNB', 'price': '0.00940000'}
111 {'symbol': 'WTCBNB', 'price': '0.29110000'}
112 {'symbol': 'DLTBTC', 'price': '0.00001403'}
113 {'symbol': 'DLTETH', 'price': '0.00044934'}
114 {'symbol': 'AMBBTC', 'price': '0.00003038'}
115 {'symbol': 'AMBETH', 'price': '0.00096100'}
116 {'symbol': 'AMBBNB', 'price': '0.02012000'}
117 {'symbol': 'BCCETH', 'price': '2.20143000'}
118 {'symbol': 'BCCUSDT', 'price': '456.88000000'}
119 {'symbol': 'BCCBNB', 'price': '46.12000000'}
120 {'symbol': 'BATBTC', 'price': '0.00004119'}
121 {'symbol': 'BATETH', 'price': '0.00130590'}
122 {'symbol': 'BATBNB', 'price': '0.02740000'}
123 {'symbol': 'BCPTBTC', 'price': '0.00001647'}
124 {'symbol': 'BCPTETH', 'price': '0.00052260'}
125 {'symbol': 'BCPTBNB', 'price': '0.01100000'}
126 {'symbol': 'ARNBTC', 'price': '0.00012498'}
127 {'symbol': 'ARNETH', 'price': '0.00396516'}
128 {'symbol': 'GVTBTC', 'price': '0.00214860'}
129 {'symbol': 'GVTETH', 'price': '0.06845200'}
130 {'symbol': 'CDTBTC', 'price': '0.00000273'}
131 {'symbol': 'CDTETH', 'price': '0.00008694'}
132 {'symbol': 'GXSBTC', 'price': '0.00021680'}
133 {'symbol': 'GXSETH', 'price': '0.00689000'}
134 {'symbol': 'NEOUSDT', 'price': '16.82400000'}
135 {'symbol': 'NEOBNB', 'price': '1.70500000'}
136 {'symbol': 'POEBTC', 'price': '0.00000181'}
137 {'symbol': 'POEETH', 'price': '0.00005743'}
138 {'symbol': 'QSPBTC', 'price': '0.00000637'}
139 {'symbol': 'QSPETH', 'price': '0.00020160'}
140 {'symbol': 'QSPBNB', 'price': '0.00426400'}
141 {'symbol': 'BTSBTC', 'price': '0.00001595'}
142 {'symbol': 'BTSETH', 'price': '0.00050508'}
143 {'symbol': 'BTSBNB', 'price': '0.01059000'}
144 {'symbol': 'XZCBTC', 'price': '0.00152700'}
145 {'symbol': 'XZCETH', 'price': '0.04869800'}
146 {'symbol': 'XZCBNB', 'price': '1.02200000'}
147 {'symbol': 'LSKBTC', 'price': '0.00043830'}
148 {'symbol': 'LSKETH', 'price': '0.01386300'}
149 {'symbol': 'LSKBNB', 'price': '0.29330000'}
150 {'symbol': 'TNTBTC', 'price': '0.00000476'}
151 {'symbol': 'TNTETH', 'price': '0.00015289'}
152 {'symbol': 'FUELBTC', 'price': '0.00000312'}
153 {'symbol': 'FUELETH', 'price': '0.00009968'}
154 {'symbol': 'MANABTC', 'price': '0.00001109'}
155 {'symbol': 'MANAETH', 'price': '0.00035177'}
156 {'symbol': 'BCDBTC', 'price': '0.00026700'}
157 {'symbol': 'BCDETH', 'price': '0.00848000'}
158 {'symbol': 'DGDBTC', 'price': '0.00694500'}
159 {'symbol': 'DGDETH', 'price': '0.22132000'}
160 {'symbol': 'IOTABNB', 'price': '0.05034000'}
161 {'symbol': 'ADXBTC', 'price': '0.00003760'}
162 {'symbol': 'ADXETH', 'price': '0.00119610'}
163 {'symbol': 'ADXBNB', 'price': '0.02502000'}
164 {'symbol': 'ADABTC', 'price': '0.00001172'}
165 {'symbol': 'ADAETH', 'price': '0.00037211'}
166 {'symbol': 'PPTBTC', 'price': '0.00052660'}
167 {'symbol': 'PPTETH', 'price': '0.01665100'}
168 {'symbol': 'CMTBTC', 'price': '0.00001766'}
169 {'symbol': 'CMTETH', 'price': '0.00056163'}
170 {'symbol': 'CMTBNB', 'price': '0.01190000'}
171 {'symbol': 'XLMBTC', 'price': '0.00003749'}
172 {'symbol': 'XLMETH', 'price': '0.00119144'}
173 {'symbol': 'XLMBNB', 'price': '0.02497000'}
174 {'symbol': 'CNDBTC', 'price': '0.00000402'}
175 {'symbol': 'CNDETH', 'price': '0.00012741'}
176 {'symbol': 'CNDBNB', 'price': '0.00269100'}
177 {'symbol': 'LENDBTC', 'price': '0.00000288'}
178 {'symbol': 'LENDETH', 'price': '0.00009219'}
179 {'symbol': 'WABIBTC', 'price': '0.00003891'}
180 {'symbol': 'WABIETH', 'price': '0.00123428'}
181 {'symbol': 'WABIBNB', 'price': '0.02585000'}
182 {'symbol': 'LTCETH', 'price': '0.25781000'}
183 {'symbol': 'LTCUSDT', 'price': '53.71000000'}
184 {'symbol': 'LTCBNB', 'price': '5.42000000'}
185 {'symbol': 'TNBBTC', 'price': '0.00000154'}
186 {'symbol': 'TNBETH', 'price': '0.00004892'}
187 {'symbol': 'WAVESBTC', 'price': '0.00030420'}
188 {'symbol': 'WAVESETH', 'price': '0.00965900'}
189 {'symbol': 'WAVESBNB', 'price': '0.20200000'}
190 {'symbol': 'GTOBTC', 'price': '0.00001126'}
191 {'symbol': 'GTOETH', 'price': '0.00035908'}
192 {'symbol': 'GTOBNB', 'price': '0.00750000'}
193 {'symbol': 'ICXBTC', 'price': '0.00010760'}
194 {'symbol': 'ICXETH', 'price': '0.00342800'}
195 {'symbol': 'ICXBNB', 'price': '0.07155000'}
196 {'symbol': 'OSTBTC', 'price': '0.00000716'}
197 {'symbol': 'OSTETH', 'price': '0.00022695'}
198 {'symbol': 'OSTBNB', 'price': '0.00479400'}
199 {'symbol': 'ELFBTC', 'price': '0.00005117'}
200 {'symbol': 'ELFETH', 'price': '0.00162669'}
201 {'symbol': 'AIONBTC', 'price': '0.00006550'}
202 {'symbol': 'AIONETH', 'price': '0.00207700'}
203 {'symbol': 'AIONBNB', 'price': '0.04354000'}
204 {'symbol': 'NEBLBTC', 'price': '0.00031370'}
205 {'symbol': 'NEBLETH', 'price': '0.00991800'}
206 {'symbol': 'NEBLBNB', 'price': '0.20887000'}
207 {'symbol': 'BRDBTC', 'price': '0.00006026'}
208 {'symbol': 'BRDETH', 'price': '0.00191450'}
209 {'symbol': 'BRDBNB', 'price': '0.04027000'}
210 {'symbol': 'MCOBNB', 'price': '0.46658000'}
211 {'symbol': 'EDOBTC', 'price': '0.00018130'}
212 {'symbol': 'EDOETH', 'price': '0.00577600'}
213 {'symbol': 'WINGSBTC', 'price': '0.00002566'}
214 {'symbol': 'WINGSETH', 'price': '0.00082420'}
215 {'symbol': 'NAVBTC', 'price': '0.00005590'}
216 {'symbol': 'NAVETH', 'price': '0.00176600'}
217 {'symbol': 'NAVBNB', 'price': '0.03737000'}
218 {'symbol': 'LUNBTC', 'price': '0.00073550'}
219 {'symbol': 'LUNETH', 'price': '0.02330400'}
220 {'symbol': 'APPCBTC', 'price': '0.00001610'}
221 {'symbol': 'APPCETH', 'price': '0.00051070'}
222 {'symbol': 'APPCBNB', 'price': '0.01088000'}
223 {'symbol': 'VIBEBTC', 'price': '0.00001127'}
224 {'symbol': 'VIBEETH', 'price': '0.00035680'}
225 {'symbol': 'RLCBTC', 'price': '0.00007310'}
226 {'symbol': 'RLCETH', 'price': '0.00230700'}
227 {'symbol': 'RLCBNB', 'price': '0.04862000'}
228 {'symbol': 'INSBTC', 'price': '0.00007590'}
229 {'symbol': 'INSETH', 'price': '0.00240200'}
230 {'symbol': 'PIVXBTC', 'price': '0.00020030'}
231 {'symbol': 'PIVXETH', 'price': '0.00634400'}
232 {'symbol': 'PIVXBNB', 'price': '0.13445000'}
233 {'symbol': 'IOSTBTC', 'price': '0.00000187'}
234 {'symbol': 'IOSTETH', 'price': '0.00005942'}
235 {'symbol': 'STEEMBTC', 'price': '0.00012540'}
236 {'symbol': 'STEEMETH', 'price': '0.00400200'}
237 {'symbol': 'STEEMBNB', 'price': '0.08344000'}
238 {'symbol': 'NANOBTC', 'price': '0.00031350'}
239 {'symbol': 'NANOETH', 'price': '0.00996700'}
240 {'symbol': 'NANOBNB', 'price': '0.20830000'}
241 {'symbol': 'VIABTC', 'price': '0.00010320'}
242 {'symbol': 'VIAETH', 'price': '0.00325200'}
243 {'symbol': 'VIABNB', 'price': '0.06889000'}
244 {'symbol': 'BLZBTC', 'price': '0.00002034'}
245 {'symbol': 'BLZETH', 'price': '0.00064607'}
246 {'symbol': 'BLZBNB', 'price': '0.01376000'}
247 {'symbol': 'AEBTC', 'price': '0.00021210'}
248 {'symbol': 'AEETH', 'price': '0.00674300'}
249 {'symbol': 'AEBNB', 'price': '0.14052000'}
250 {'symbol': 'NCASHBTC', 'price': '0.00000074'}
251 {'symbol': 'NCASHETH', 'price': '0.00002341'}
252 {'symbol': 'NCASHBNB', 'price': '0.00049400'}
253 {'symbol': 'POABTC', 'price': '0.00001585'}
254 {'symbol': 'POAETH', 'price': '0.00050569'}
255 {'symbol': 'POABNB', 'price': '0.01050000'}
256 {'symbol': 'ZILBTC', 'price': '0.00000528'}
257 {'symbol': 'ZILETH', 'price': '0.00016732'}
258 {'symbol': 'ZILBNB', 'price': '0.00350600'}
259 {'symbol': 'ONTBTC', 'price': '0.00027950'}
260 {'symbol': 'ONTETH', 'price': '0.00889400'}
261 {'symbol': 'ONTBNB', 'price': '0.18599000'}
262 {'symbol': 'STORMBTC', 'price': '0.00000129'}
263 {'symbol': 'STORMETH', 'price': '0.00004101'}
264 {'symbol': 'STORMBNB', 'price': '0.00086500'}
265 {'symbol': 'QTUMBNB', 'price': '0.43374000'}
266 {'symbol': 'QTUMUSDT', 'price': '4.30000000'}
267 {'symbol': 'XEMBTC', 'price': '0.00001539'}
268 {'symbol': 'XEMETH', 'price': '0.00048848'}
269 {'symbol': 'XEMBNB', 'price': '0.01026000'}
270 {'symbol': 'WANBTC', 'price': '0.00015330'}
271 {'symbol': 'WANETH', 'price': '0.00486300'}
272 {'symbol': 'WANBNB', 'price': '0.10181000'}
273 {'symbol': 'WPRBTC', 'price': '0.00000468'}
274 {'symbol': 'WPRETH', 'price': '0.00014819'}
275 {'symbol': 'QLCBTC', 'price': '0.00000774'}
276 {'symbol': 'QLCETH', 'price': '0.00024633'}
277 {'symbol': 'SYSBTC', 'price': '0.00001556'}
278 {'symbol': 'SYSETH', 'price': '0.00049196'}
279 {'symbol': 'SYSBNB', 'price': '0.01034000'}
280 {'symbol': 'QLCBNB', 'price': '0.00514500'}
281 {'symbol': 'GRSBTC', 'price': '0.00008368'}
282 {'symbol': 'GRSETH', 'price': '0.00265000'}
283 {'symbol': 'ADAUSDT', 'price': '0.07734000'}
284 {'symbol': 'ADABNB', 'price': '0.00780000'}
285 {'symbol': 'CLOAKBTC', 'price': '0.00039730'}
286 {'symbol': 'CLOAKETH', 'price': '0.01264500'}
287 {'symbol': 'GNTBTC', 'price': '0.00002535'}
288 {'symbol': 'GNTETH', 'price': '0.00080212'}
289 {'symbol': 'GNTBNB', 'price': '0.01681000'}
290 {'symbol': 'LOOMBTC', 'price': '0.00001948'}
291 {'symbol': 'LOOMETH', 'price': '0.00062045'}
292 {'symbol': 'LOOMBNB', 'price': '0.01296000'}
293 {'symbol': 'XRPUSDT', 'price': '0.46538000'}
294 {'symbol': 'REPBTC', 'price': '0.00202100'}
295 {'symbol': 'REPETH', 'price': '0.06410000'}
296 {'symbol': 'REPBNB', 'price': '1.34500000'}
297 {'symbol': 'TUSDBTC', 'price': '0.00015636'}
298 {'symbol': 'TUSDETH', 'price': '0.00496870'}
299 {'symbol': 'TUSDBNB', 'price': '0.10409000'}
300 {'symbol': 'ZENBTC', 'price': '0.00212500'}
301 {'symbol': 'ZENETH', 'price': '0.06775000'}
302 {'symbol': 'ZENBNB', 'price': '1.42200000'}
303 {'symbol': 'SKYBTC', 'price': '0.00056300'}
304 {'symbol': 'SKYETH', 'price': '0.01796000'}
305 {'symbol': 'SKYBNB', 'price': '0.37600000'}
306 {'symbol': 'EOSUSDT', 'price': '5.51590000'}
307 {'symbol': 'EOSBNB', 'price': '0.55570000'}
308 {'symbol': 'CVCBTC', 'price': '0.00002071'}
309 {'symbol': 'CVCETH', 'price': '0.00065790'}
310 {'symbol': 'CVCBNB', 'price': '0.01376000'}
311 {'symbol': 'THETABTC', 'price': '0.00001369'}
312 {'symbol': 'THETAETH', 'price': '0.00043338'}
313 {'symbol': 'THETABNB', 'price': '0.00922000'}
314 {'symbol': 'XRPBNB', 'price': '0.04701000'}
315 {'symbol': 'TUSDUSDT', 'price': '1.03210000'}
316 {'symbol': 'IOTAUSDT', 'price': '0.49850000'}
317 {'symbol': 'XLMUSDT', 'price': '0.24765000'}
318 {'symbol': 'IOTXBTC', 'price': '0.00000258'}
319 {'symbol': 'IOTXETH', 'price': '0.00008173'}
320 {'symbol': 'QKCBTC', 'price': '0.00000852'}
321 {'symbol': 'QKCETH', 'price': '0.00027084'}
322 {'symbol': 'AGIBTC', 'price': '0.00000794'}
323 {'symbol': 'AGIETH', 'price': '0.00025320'}
324 {'symbol': 'AGIBNB', 'price': '0.00531000'}
325 {'symbol': 'NXSBTC', 'price': '0.00010290'}
326 {'symbol': 'NXSETH', 'price': '0.00325700'}
327 {'symbol': 'NXSBNB', 'price': '0.06930000'}
328 {'symbol': 'ENJBNB', 'price': '0.00510200'}
329 {'symbol': 'DATABTC', 'price': '0.00000584'}
330 {'symbol': 'DATAETH', 'price': '0.00018545'}
331 {'symbol': 'ONTUSDT', 'price': '1.84900000'}
332 {'symbol': 'TRXBNB', 'price': '0.00248300'}
333 {'symbol': 'TRXUSDT', 'price': '0.02458000'}
334 {'symbol': 'ETCUSDT', 'price': '9.79640000'}
335 {'symbol': 'ETCBNB', 'price': '0.98670000'}
336 {'symbol': 'ICXUSDT', 'price': '0.71040000'}
337 {'symbol': 'SCBTC', 'price': '0.00000108'}
338 {'symbol': 'SCETH', 'price': '0.00003445'}
339 {'symbol': 'SCBNB', 'price': '0.00072600'}
340 {'symbol': 'NPXSBTC', 'price': '0.00000023'}
341 {'symbol': 'NPXSETH', 'price': '0.00000737'}
342 {'symbol': 'KEYBTC', 'price': '0.00000094'}
343 {'symbol': 'KEYETH', 'price': '0.00003000'}
344 {'symbol': 'NASBTC', 'price': '0.00025700'}
345 {'symbol': 'NASETH', 'price': '0.00816200'}
346 {'symbol': 'NASBNB', 'price': '0.17060000'}
347 {'symbol': 'MFTBTC', 'price': '0.00000117'}
348 {'symbol': 'MFTETH', 'price': '0.00003724'}
349 {'symbol': 'MFTBNB', 'price': '0.00078000'}
350 {'symbol': 'DENTBTC', 'price': '0.00000034'}
351 {'symbol': 'DENTETH', 'price': '0.00001071'}
352 {'symbol': 'ARDRBTC', 'price': '0.00001773'}
353 {'symbol': 'ARDRETH', 'price': '0.00056590'}
354 {'symbol': 'ARDRBNB', 'price': '0.01184000'}
355 {'symbol': 'NULSUSDT', 'price': '1.14600000'}
356 {'symbol': 'HOTBTC', 'price': '0.00000017'}
357 {'symbol': 'HOTETH', 'price': '0.00000540'}
358 {'symbol': 'VETBTC', 'price': '0.00000174'}
359 {'symbol': 'VETETH', 'price': '0.00005525'}
360 {'symbol': 'VETUSDT', 'price': '0.01151000'}
361 {'symbol': 'VETBNB', 'price': '0.00116000'}
362 {'symbol': 'DOCKBTC', 'price': '0.00000317'}
363 {'symbol': 'DOCKETH', 'price': '0.00010052'}
364 {'symbol': 'POLYBTC', 'price': '0.00003509'}
365 {'symbol': 'POLYBNB', 'price': '0.02343000'}
366 {'symbol': 'PHXBTC', 'price': '0.00000214'}
367 {'symbol': 'PHXETH', 'price': '0.00006783'}
368 {'symbol': 'PHXBNB', 'price': '0.00143600'}
369 {'symbol': 'HCBTC', 'price': '0.00029400'}
370 {'symbol': 'HCETH', 'price': '0.00941700'}
371 {'symbol': 'GOBTC', 'price': '0.00000744'}
372 {'symbol': 'GOBNB', 'price': '0.00492900'}
373 {'symbol': 'PAXBTC', 'price': '0.00015542'}
374 {'symbol': 'PAXBNB', 'price': '0.10360000'}
375 {'symbol': 'PAXUSDT', 'price': '1.02700000'}
376 {'symbol': 'PAXETH', 'price': '0.00492712'}
377 {'symbol': 'RVNBTC', 'price': '0.00000665'}
378 {'symbol': 'RVNBNB', 'price': '0.00442100'}



'''