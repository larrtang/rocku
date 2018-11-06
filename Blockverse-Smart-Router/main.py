from Binance import Binance

from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource


parser = reqparse.RequestParser()
binance = Binance()




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
    def __order_syncDatabase(self, side, order, market, price, quantity):
        # TODO: 
        pass



    # Returns order status of orderID
    # Returns 0 if all orders filled
    def get(self):
        oid = request.args.get('id') # Trade's ID 
        market = request.args.get('market') # Trade's ID 
        if binance.allOrdersFilled(market):
            return 0
        
        return binance.getOrderStatus(market, oid)



    # Order is passed onto binance
    def post(self):
        side = request.args.get('side')     #buy/sell
        order = request.args.get('order')   #limit/market
        market = request.args.get('market')
        price = request.args.get('price')
        quantity = request.args.get('quantity')

        trade = None
        if order == 'limit':
            if side == 'buy':
                trade = binance.limit_buy(market, quantity, price)
            if side == 'sell':
                trade = binance.limit_sell(market, quantity, price)
        if order == 'market':
            if side == 'buy':
                trade = binance.market_buy(market, quantity)
            if side == 'sell':
                trade = binance.market_sell(market, quantity)

        
        return trade



def main():
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(OrderRouter, '/order')
    api.add_resource(MarketData, '/')
    app.run(debug=True)



if __name__ == '__main__':
    main()

