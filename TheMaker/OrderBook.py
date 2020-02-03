import threading
import sys

BID = 'b'
ASK = 'a'

class Order:
    def __init__(self, price, quantity):
        assert type(price) is float
        assert type(quantity) is float
        self.price = price
        self.quantity = quantity

    # def __repr__(self):
    #     return [self.price, self.quantity]

    def __str__(self):
        return "Order[p:q]:"+str(self.price)+":"+str(self.quantity)

class OrderBookSide:
    def __init__(self, side='b', depth=50):
        self.side = side
        self.sortedOrderList = []
        self.depth = depth
        self.lock = threading.Lock()

    def __len__(self):
        return len(self.sortedOrderList)


    def add_modify_delete(self, order : Order):
        self.lock.acquire()
        if len(self.sortedOrderList) == 0:
            self.sortedOrderList.append(order)
        else:
            if self.side == BID:
                self.__add_modify_delete_bid(order)
            if self.side == ASK:
                self.__add_modify_delete_ask(order)
        if len(self.sortedOrderList) > self.depth:
            self.sortedOrderList = self.sortedOrderList[:self.depth]
        self.lock.release()

    def __add_modify_delete_bid(self, order: Order):
        for i in range(len(self.sortedOrderList)):
            if order.quantity != 0:
                [p,q] = [self.sortedOrderList[i].price, self.sortedOrderList[i].quantity]
                if order.price > p:
                    self.sortedOrderList.insert(i, order)
                    break
                elif order.price == p:
                    self.sortedOrderList[i].quantity = order.quantity
                    if order.quantity == 0:
                        #print('deleting '+ str(order))
                        # del self.sortedOrderList[i]
                        self.sortedOrderList.pop(i)
                    break
                elif i == len(self.sortedOrderList) - 1:
                    #print('new BID order at end of book')
                    self.sortedOrderList.append(order)

            if i >= self.depth:
                break

    def __add_modify_delete_ask(self, order: Order):
        for i in range(len(self.sortedOrderList)):
            if order.quantity != 0:
                [p, q] = [self.sortedOrderList[i].price, self.sortedOrderList[i].quantity]
                if order.price < p:
                    self.sortedOrderList.insert(i, order)
                    break
                elif order.price == p:
                    self.sortedOrderList[i].quantity = order.quantity
                    if order.quantity == 0:
                        # del self.sortedOrderList[i]
                        self.sortedOrderList.pop(i)
                    break
                elif i == len(self.sortedOrderList) - 1:
                    #print('new BID order at end of book')
                    self.sortedOrderList.append(order)


    def update_delete(self, order : Order):
        self.lock.acquire()
        for i in range(len(self.sortedOrderList)):
            if i < len(self.sortedOrderList) and order.price == self.sortedOrderList[i].price:
                self.sortedOrderList[i].quantity = order.quantity
                if order.quantity == 0:
                    self.sortedOrderList.pop(i)
        self.lock.release()


class OrderBook:
    def __init__(self, market, display_depth=30):
        self.market = market
        self.bids = OrderBookSide(side=BID)
        self.asks = OrderBookSide(side=ASK)
        self.display_depth = display_depth


    def add_modify_delete(self, order : Order, side):
        if side is BID:
            self.bids.add_modify_delete(order)
        else:
            self.asks.add_modify_delete(order)

    def update_delete(self, order : Order, side):
        while len(self.bids) > 0 and self.bids.sortedOrderList[0].price > order.price:
            self.bids.sortedOrderList.pop(0)
        while len(self.asks) > 0 and self.asks.sortedOrderList[0].price < order.price:
            self.asks.sortedOrderList.pop(0)

        if side is BID:
            self.bids.update_delete(order)
        else:
            self.asks.update_delete(order)


    def binance_incremental_book_update_handler(self, msg):
        # print("message type: {}".format(msg['e']))
        bidUpdates = msg['b']
        askUpdates = msg['a']

        for bid in bidUpdates:
            order = Order(float(bid[0]), float(bid[1]))
            #print("bid:", order, end='\t')
            self.add_modify_delete(order, side='b')
        for ask in askUpdates:
            order = Order(float(ask[0]), float(ask[1]))
            #print("ask:", order, end='\n')
            self.add_modify_delete(order, side='a')
        print(self)


    def binance_incremental_trade_update_handler(self, msg):
        trade_price = float(msg['p'])
        mm_is_buying = bool(msg['m'])
        order = Order(trade_price, 0.0)
        if mm_is_buying:
            self.update_delete(order, side='b')
        else:
            self.update_delete(order, side='a')
        print(self)
        print(msg)
        self.health_check()


    def __str__(self):
        #self.health_check()
        self.mid = None
        if len(self.bids) > 0 and len(self.asks) > 0:
            self.mid = self.bids.sortedOrderList[0].price + self.asks.sortedOrderList[0].price
            self.mid /= 2
            
        ret = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" \
              "_____________________________Mid="+str(self.mid)+"_______________________________________\n"
        ret += "\t\tBID\t\t|\t\tASK\t\t\n"
        for i in range(max(len(self.bids), len(self.asks))):
            if i < len(self.bids):
                [p, q] = [self.bids.sortedOrderList[i].price,
                          self.bids.sortedOrderList[i].quantity]
                ret += "{:12.6f}".format(p)+'\t'+"{:12.6f}".format(q)+'\t|'
            else:
                ret += "\t\t\t\t|"

            if i < len(self.asks):
                [p, q] = [self.asks.sortedOrderList[i].price,
                          self.asks.sortedOrderList[i].quantity]
                ret += "{:12.6f}".format(p)+'\t'+"{:12.6f}".format(q)+'\n'
            else:
                ret += "\n"

            if i >= self.display_depth:
                break

        return ret


    def health_check(self):
        assert(self.bids.sortedOrderList[0].price < self.asks.sortedOrderList[0].price)
