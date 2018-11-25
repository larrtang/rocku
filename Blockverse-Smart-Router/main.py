from Binance import Binance

from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource

import MySQLdb

parser = reqparse.RequestParser()
binance = Binance()

SQL_HOST = '127.0.0.1'
SQL_USER = 'root'
SQL_PASS = 'password'
SQL_DB = 'peatio_development'

db = MySQLdb.connect(host=SQL_HOST, user=SQL_USER, passwd=SQL_PASS, db=SQL_DB)
cur = db.cursor()

pending_orders = []


'''
Market Data Endpoint

Returns passive information such as market price or bid ask

'''
class MarketData(Resource):
    def get(self):
        market = request.args.get('market') 
        return binance.getMarketPrice(market)





'''
Order Routing Endpoint

Routes orders to Binance
'''
class OrderRouter(Resource):
    
    # takes care of peatio database values when trading 
    def __order_syncDatabase(self, member_id, trade, side, order, market, price, quantity):
        if type(trade) is not int and (order == 'market' or trade['status'] == 'FILLED'):
            base = market[3:].lower()
            coin = market[:3].lower()

            cur.execute("""SELECT `balance` FROM `accounts` WHERE `member_id` = %i AND `currency_id` = '%s';"""%(member_id, base))
            base_bal = cur.fetchone()
            cur.execute("""SELECT `balance` FROM `accounts` WHERE `member_id` = %i AND `currency_id` = '%s';"""%(member_id, coin))
            coin_bal = cur.fetchone()    

            new_base_bal = base_bal
            new_coin_bal = coin_bal

            if side == 'buy':
                new_base_bal = base_bal - price*quantity
                new_coin_bal = coin_bal + quantity 
            elif side == 'sell':
                new_base_bal = base_bal + price*quantity
                new_coin_bal = coin_bal - quantity

            cur.execute("""UPDATE `accounts` SET `balance` = %f WHERE `member_id` = %i AND `currency_id` = '%s';"""%(new_base_bal, member_id, base))
            cur.execute("""UPDATE `accounts` SET `balance` = %f WHERE `member_id` = %i AND `currency_id` = '%s';"""%(new_coin_bal, member_id, coin))

            if trade['orderId'] in pending_orders:
                cur.execute("""SELECT `locked` FROM `accounts` WHERE `member_id` = %i AND `currency_id` = '%s';"""%(member_id, base))
                base_bal_locked = cur.fetchone()
                cur.execute("""SELECT `locked` FROM `accounts` WHERE `member_id` = %i AND `currency_id` = '%s';"""%(member_id, coin))
                coin_bal_locked = cur.fetchone()

                new_base_bal_locked = base_bal_locked
                new_coin_bal_locked = coin_bal_locked

                if side == 'buy':
                    new_base_bal_locked -= price*quantity
                    cur.execute("""UPDATE `accounts` SET `locked` = %f WHERE `member_id` = %i AND `currency_id` = '%s';"""%(new_base_bal_locked, member_id, base))                
                elif side == 'sell':
                    new_coin_bal_locked -= quantity
                    cur.execute("""UPDATE `accounts` SET `locked` = %f WHERE `member_id` = %i AND `currency_id` = '%s';"""%(new_coin_bal_locked, member_id, coin))    

                pending_orders.remove(trade['orderId'])
        
        
        #this time, trade not filled
        elif trade['orderId'] not in pending_orders and trade['status'] == "NEW" and trade['isWorking'] == True:
            base = market[3:]
            coin = market[:3]

            cur.execute("""SELECT `balance` FROM `accounts` WHERE `member_id` = %i AND `currency_id` = '%s';"""%(member_id, base))
            base_bal = cur.fetchone()
            cur.execute("""SELECT `balance` FROM `accounts` WHERE `member_id` = %i AND `currency_id` = '%s';"""%(member_id, coin))
            coin_bal = cur.fetchone()    
            cur.execute("""SELECT `locked` FROM `accounts` WHERE `member_id` = %i AND `currency_id` = '%s';"""%(member_id, base))
            base_bal_locked = cur.fetchone()
            cur.execute("""SELECT `locked` FROM `accounts` WHERE `member_id` = %i AND `currency_id` = '%s';"""%(member_id, coin))
            coin_bal_locked = cur.fetchone()
            
            new_base_bal = base_bal
            new_coin_bal = coin_bal
            new_base_bal_locked = base_bal_locked
            new_coin_bal_locked = coin_bal_locked

            if side == 'buy':
                new_base_bal = base_bal - price*quantity
                new_base_bal_locked += price*quantity
                cur.execute("""UPDATE `accounts` SET `balance` = %f WHERE `member_id` = %i AND `currency_id` = '%s';"""%(new_base_bal, member_id, base))
                cur.execute("""UPDATE `accounts` SET `locked` = %f WHERE `member_id` = %i AND `currency_id` = '%s';"""%(new_base_bal_locked, member_id, base))                
            elif side == 'sell':
                new_coin_bal = coin_bal - quantity
                new_coin_bal_locked += quantity
                cur.execute("""UPDATE `accounts` SET `balance` = %f WHERE `member_id` = %i AND `currency_id` = '%s';"""%(new_coin_bal, member_id, coin))
                cur.execute("""UPDATE `accounts` SET `locked` = %f WHERE `member_id` = %i AND `currency_id` = '%s';"""%(new_coin_bal_locked, member_id, coin))                

            pending_orders.append(trade['orderId'])


            
    #ensures users can make a trade as long as they have the balance to buy/sell.
    def __check_balance(self, member_id, side, market, price, quantity):
        base = 'usdt'
        if side == 'buy':
            base = market[3:].lower()
        if side == 'sell':
            base = market[:3].lower()
        print base
        cur.execute("""SELECT `balance` FROM `accounts` WHERE `member_id` = %i AND `currency_id` = '%s';"""%(member_id, base))

        balance = cur.fetchone()
        print balance

        assert type(balance) is float
        assert type(price) is float
        assert type(quantity) is float
        balance_needed = price * quantity

        if balance >= balance_needed:
            return True
        
        return False


    # Returns order status of orderID
    # Returns 0 if all orders filled
    def get(self):
        oid = int(request.args.get('id')) # Trade's ID 
        market = request.args.get('market') # Trade's ID 
        member_id = int(request.args.get('member_id'))
        if binance.allOrdersFilled(market):
            return 0
        
        status = binance.getOrderStatus(market, oid)
        if status['status'] == "FILLED":
            self.__order_syncDatabase(member_id, status, status['side'].lower(), status['type'].lower(), 
            status['symbol'], status['price'], status['quantity'])




    # Order is passed onto binance
    def post(self):
        side = request.args.get('side')     #buy/sell
        order = request.args.get('order')   #limit/market
        market = request.args.get('market')
        price = 0.0
        try:
            price = float(request.args.get('price'))
        except:
            print "Price Omitted"
        quantity = float(request.args.get('quantity'))
        member_id = int(request.args.get('member_id'))

        market_price = binance.getMarketPrice(market)

        trade = None
        if order == 'limit':
            if side == 'buy':
                if self.__check_balance(member_id, side, market, price, quantity):
                    trade = binance.limit_buy(market, quantity, price)
            if side == 'sell':
                if self.__check_balance(member_id, side, market, price, quantity):
                    trade = binance.limit_sell(market, quantity, price)
        if order == 'market':
            if side == 'buy':
                if self.__check_balance(member_id, side, market, market_price, quantity):
                    trade = binance.market_buy(market, quantity)
            if side == 'sell':
                if self.__check_balance(member_id, side, market, market_price, quantity):
                    trade = binance.market_sell(market, quantity)

        self.__order_syncDatabase(member_id, trade, side, order, market, price, quantity)

        return trade
    
    #cancel orders
    def delete(self):
        market = request.args.get('market')
        oid = int(request.args.get('id'))

        binance.cancelOrder(market, oid)




def main():
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(OrderRouter, '/order')
    api.add_resource(MarketData, '/')
    app.run(debug=True, host='0.0.0.0')



if __name__ == '__main__':
    main()
    db.close()
