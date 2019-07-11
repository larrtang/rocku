#!/usr/bin/python3

from Binance import Binance
import sys
from math import floor
'''

{u'orderId': 24688812, u'clientOrderId': u'Tp2Jet3Enn61PWapPJtSUT', u'origQty': u'10.00000000', u'fills': [{u'commission': u'0.01000000', u'price': u'0.00029804', u'commissionAsset': u'MDA', 
u'tradeId': 3083289, u'qty': u'10.00000000'}], u'symbol': u'MDABTC', u'side': u'BUY', u'timeInForce': u'GTC', u'status': u'FILLED', u'transactTime': 1539802261763, u'type': u'LIMIT', u'price': u'0.00029804',
 u'executedQty': u'10.00000000', u'cummulativeQuoteQty': u'0.00298040'}

{'e': 'depthUpdate', 'E': 1539966957141, 's': 'MDABTC', 'U': 46466480, 'u': 46466501, 'b': [['0.00030024', '66.00000000', []], ['0.00030023', '131.00000000', []], ['0.00030022', '0.00000000', []], ['0.00030021', '171.00000000', []], ['0.00030020', '0.00000000', []], ['0.00030019', '0.00000000', []], ['0.00030017', '0.00000000', []], ['0.00029997', '0.00000000', []], ['0.00029965', '0.00000000', []], ['0.00029833', '150.00000000', []], ['0.00029678', '53.00000000', []], ['0.00029480', '20.00000000', []], ['0.00028733', '163.00000000', []]], 'a': [['0.00030150', '2061.00000000', []], ['0.00030336', '0.00000000', []], ['0.00030395', '0.00000000', []], ['0.00030487', '0.00000000', []]]}


'''
class C:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


market = str(sys.argv[1])
print(market)



indices = [0,2,5,8,11]
buy_threadshold = 3
sell_threadshold = 0.8


def buy(client, price, vol):
    order = None
    try:
        order = client.order_market_buy(
        symbol=market,
        quantity=vol)
    except Exception as e:
        print(e)
    # order_status = client.get_order(
    # symbol='MDABTC',
    # orderId='orderId')

    print(order)


    return order
def sell(client, price, vol):
    order = None
    try:
        order = client.order_market_sell(
        symbol=market,
        quantity=vol)
    except Exception as e:
        print(e)
    print(order)

    return order

def main():
    btc = float(10000)
    mda = float(0)
    amount = 0
    binance = Binance(market)
    last_feat = [0,0,0,0,0]
    last_state = [0,0,0,0,0]
    last_depth = None
    up_count = 0
    down_count = 0
    direction = ''
    bought = False
    bid_list = []
    ask_list = []
    ma = 100
    fixed_quant = 0
    btc_start = float(binance.client.get_asset_balance(asset=market[-3:])['free'])
    other_start = float(binance.client.get_asset_balance(asset=market[:-3])['free'])
    # for i in  range(len(binance.client.get_all_tickers())):
    #     print( i, binance.client.get_all_tickers()[i])
    print_quant_once = False
    avg_bid = 0
    avg_ask = 0
    lavg_bid = 0
    lavg_ask = 0
    while True:
        feat = [0,0,0,0,0]
        state = [[0,0,0,0,0],[0,0,0,0,0]]
        depth = binance.getMarketDepth(market)
        depth_of_market = depth
        try:
            for i in range(40):
                depth_of_market['bids'][i][1] = float(depth_of_market['bids'][max(0,i-1)][1]) + float(depth_of_market['bids'][i][1])
                depth_of_market['asks'][i][1] = float(depth_of_market['asks'][max(0,i-1)][1]) + float(depth_of_market['asks'][i][1])
                #print depth_of_market['bids']
                

                
                if i in indices:
                    t = depth_of_market['bids'][i][1]/depth_of_market['asks'][i][1]

                 #   if last_depth == None: print('penis')
                    if last_depth != None:
                        #print(depth_of_market['bids'][i][1] ,last_depth['bids'][i][1])
                        if depth_of_market['bids'][i][1] > last_depth['bids'][i][1]:
                        
                            if i == indices[0]:
                                state[0][0] = 1
                            elif i == indices[1]:
                                state[0][1] = 1
                            elif i == indices[2]:
                                state[0][2] = 1
                            elif i == indices[3]:
                                state[0][3] = 1
                            elif i == indices[4]:
                                state[0][4] = 1
                        elif depth_of_market['bids'][i][1] < last_depth['bids'][i][1]:
                            if i == indices[0]:
                                state[0][0] = -1
                            elif i == indices[1]:
                                state[0][1] = -1
                            elif i == indices[2]:
                                state[0][2] = -1
                            elif i == indices[3]:
                                state[0][3] = -1
                            elif i == indices[4]:
                                state[0][4] = -1

                        if depth_of_market['asks'][i][1] > last_depth['asks'][i][1]:
                            if i == indices[0]:
                                state[1][0] = 1
                            elif i == indices[1]:
                                state[1][1] = 1
                            elif i == indices[2]:
                                state[1][2] = 1
                            elif i == indices[3]:
                                state[1][3] = 1
                            elif i == indices[4]:
                                state[1][4] = 1
                        elif depth_of_market['asks'][i][1] < last_depth['asks'][i][1]:
                            if i == indices[0]:
                                state[1][0] = -1
                            elif i == indices[1]:
                                state[1][1] = -1
                            elif i == indices[2]:
                                state[1][2] = -1
                            elif i == indices[3]:
                                state[1][3] = -1
                            elif i == indices[4]:
                                state[1][4] = -1


                    if t >= buy_threadshold:
                        if i == indices[0]:
                            feat[0] = 1
                        elif i == indices[1]:
                            feat[1] = 1
                        elif i == indices[2]:
                            feat[2] = 1
                        elif i == indices[3]:
                            feat[3] = 1
                        elif i == indices[4]:
                            feat[4] = 1
                    elif t <= sell_threadshold:
                        if i == indices[0]:
                            feat[0] = -1
                        elif i == indices[1]:
                            feat[1] = -1
                        elif i == indices[2]:
                            feat[2] = -1
                        elif i == indices[3]:
                            feat[3] = -1
                        elif i == indices[4]:
                            feat[4] = -1
                    else:
                        if i == indices[0]:
                            feat[0] = 0
                        elif i == indices[1]:
                            feat[1] = 0
                        elif i == indices[2]:
                            feat[2] = 0
                        elif i == indices[3]:
                            feat[3] = 0
                        elif i == indices[4]:
                            feat[4] = 0

            bid_list.append(depth_of_market['bids'][indices[2]][1])
            ask_list.append(depth_of_market['asks'][indices[2]][1])
            if len(bid_list) > ma: bid_list.pop(0)
            if len(ask_list) > ma: ask_list.pop(0)

            avg_bid = float(sum(bid_list) / float(len(bid_list)))
            avg_ask = float(sum(ask_list) / float(len(ask_list)))

        except Exception as e:
            print('Exception caught in depth loop.')
            print(e) 
        price =  binance.getLastTradedPrice(market)
        try:
            btc_all = binance.client.get_asset_balance(asset=market[-3:])
            mda_all = binance.client.get_asset_balance(asset=market[:-3])
            mda = float(mda_all['free'])
            btc = float(btc_all['free'])
        except Exception as e:
            print("Exception caught in get asset balance")
            print(e)
        quantity = round((btc_start/2)/price,3) # btc/binance.getLastTradedPrice('MDABTC')
        #check if only trades integer quantities
        if quantity > 1:
            quantity = floor(quantity)
        if print_quant_once == False:
            print(quantity)
            print_quant_once = True
        if (state[0][3] == 1 and state[0][2] == 1 and state[0][1] == 1)  and( state[1][1] == -1 or state[1][2] == -1 or state[1][3] == -1 or state[1][4] == -1) and feat[0] == 1 and feat[1] == 1 and feat[2] == 1 and feat[3] == 1 and feat[4] == 1:
            print('^^^')
            up_count += 1
            if down_count > 0: down_count -= 1 
            else: down_count = 0
            if up_count > 5 and direction !=  C.OKGREEN + '^^^ Bullish ^^^' + C.ENDC and depth_of_market['bids'][indices[2]][1]/avg_bid >1.2:
                direction = C.OKGREEN + '^^^ Bullish ^^^' + C.ENDC
                # buy
                #mda = btc/binance.getLastTradedPrice('MDABTC')
                #btc = 0

                buy(binance.client, binance.getLastTradedPrice(market), 
                quantity)
                fixed_quant = quantity
                bought = True
                up_count = 0
                down_count = 0

        elif (state[1][3] == 1 or state[0][3] == -1) and (feat[0] == -1 and feat[1] == -1 and feat[2] == -1 ) and ( feat[3] == -1 and feat[4] == -1):
            print('!!!')
            down_count += 1
            if up_count > 0: up_count -= 1 
            else: up_count = 0
            if down_count > 3 and direction !=  C.FAIL + '!!! Bearish !!!' + C.ENDC:
                direction = C.FAIL + '!!! Bearish !!!' + C.ENDC
                if btc == 0 or bought == True:
                    #btc = mda * binance.getLastTradedPrice('MDABTC')
                    #mda = 0

                    sell(binance.client, binance.getLastTradedPrice(market), 
                    fixed_quant)
                    print(C.OKBLUE + 'Bitcoin:\t'+str(btc) + C.ENDC)
                    bought = False
                down_count = 0
                up_count = 0
        else:
            print()

        
        percentchange = float(btc +float(mda*price) - (btc_start))/float(btc_start) * 100
        print(feat, end='\t')
        print('\tavg bid:', round(avg_bid,2), end=' ')
        if (avg_bid > lavg_bid): print('^', end=' ')
        else: print(' ', end=' ')
        print('\tavg ask:',round(avg_ask,2), end=' ')
        if (avg_ask > lavg_ask): print('!')
        else: print()
        print(state)
        print(C.OKBLUE + '--> '+str(btc_all) +'\n--> '+ str(mda_all) +C.ENDC + '\t\t\t\t\t\t\t\t', end=' ')
        if (percentchange >= 0): print(C.OKGREEN , '+' +str(percentchange) +'%'+ C.ENDC) 
        else: print(C.OKBLUE + "-"+ str(percentchange) +'%'+ C.ENDC) 
        print() 
        print(direction)
        lavg_bid = avg_bid
        lavg_ask = avg_ask
        last_feat = feat
        last_depth = depth_of_market
        last_state = state

if __name__ == '__main__':
    main()


