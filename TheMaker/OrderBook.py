import threading
import logging

BID = 'b'
ASK = 'a'

class Order:
    """MBP Price Level"""

    def __init__(self, price, quantity, pos_quantity=0.0, side='b'):
        assert type(price) is float
        assert type(quantity) is float
        self.price = price
        self.quantity = quantity
        self.position_quantity = pos_quantity
        self.side = side

    def getTotal(self):
        return self.price * self.quantity

    def getPositionTotal(self):
        return self.price * self.position_quantity

    def __repr__(self):
        return str(self.price) + " " + str(self.quantity) + " " + \
               str(self.position_quantity) + " " + str(self.side)

    def __str__(self):
        return "[{:5.4f}".format(self.price)+"] ["+str(self.quantity)+"] ["+\
               str(self.position_quantity)+"] ["+str(self.side)+"]"

class OrderBookSide:
    def __init__(self, side='b', depth=30, lock=threading.Lock()):
        self.side = side
        self.sortedOrderList = []
        self.depth = depth
        self._lock = lock

    def __len__(self):
        return len(self.sortedOrderList)


    def add_modify_delete(self, order : Order, my_order):
       # if not my_order and order.quantity == 0.0 and order.position_quantity == 0.0:
        #    print("order cancel coming in:", order)
        self._lock.acquire()
        if len(self.sortedOrderList) == 0:
            self.sortedOrderList.append(order)
        else:
            if self.side == BID:
                self.__add_modify_delete_bid(order, my_order)
            if self.side == ASK:
                self.__add_modify_delete_ask(order, my_order)
        if len(self.sortedOrderList) > self.depth:
            self.sortedOrderList = self.sortedOrderList[:self.depth]
        self._lock.release()

    def __add_modify_delete_bid(self, order: Order, my_order):
        if order.quantity > 0:
            if len(self.sortedOrderList) == 0:
                self.sortedOrderList.append(order)
                return
            for i in range(len(self.sortedOrderList)):
                [p,q] = [self.sortedOrderList[i].price, self.sortedOrderList[i].quantity]
                if order.price > p:
                    self.sortedOrderList.insert(i, order)
                    break
                elif order.price == p:
                    if not my_order:
                        self.sortedOrderList[i].quantity = order.quantity
                        self.sortedOrderList[i].position_quantity = order.position_quantity
                    else:  # is my_order
                        # going to be modify
                        self.sortedOrderList[i].quantity += order.quantity
                        self.sortedOrderList[i].position_quantity += order.position_quantity
                    break
                elif i == len(self.sortedOrderList) - 1:
                    #print('new BID order at end of book')
                    self.sortedOrderList.append(order)
                if i >= self.depth:
                    break
        # Cancel order coming in
        elif my_order and order.quantity == 0.0:
            for j in range(len(self.sortedOrderList)):
                [p, q] = [self.sortedOrderList[j].price, self.sortedOrderList[j].quantity]
                if order.price == p:
                    self.sortedOrderList.pop(j)
                    break
        elif order.quantity == 0.0:
            self._lock.release()
            self.update_delete(order)
            self._lock.acquire()



    def __add_modify_delete_ask(self, order: Order, my_order):
        if order.quantity > 0:
            if len(self.sortedOrderList) == 0:
                self.sortedOrderList.append(order)
                return
            for i in range(len(self.sortedOrderList)):
                [p, q] = [self.sortedOrderList[i].price, self.sortedOrderList[i].quantity]
                if order.price < p:
                    self.sortedOrderList.insert(i, order)
                    break
                elif order.price == p:
                    if not my_order:
                        self.sortedOrderList[i].quantity = order.quantity
                        self.sortedOrderList[i].position_quantity = order.position_quantity
                    else:  # is my_order
                        # going to be modify
                        self.sortedOrderList[i].quantity += order.quantity
                        self.sortedOrderList[i].position_quantity += order.position_quantity
                    break
                elif i == len(self.sortedOrderList) - 1:
                    # print('new BID order at end of book')
                    self.sortedOrderList.append(order)
                if i >= self.depth:
                    break
        # Cancel order coming in
        elif my_order and order.quantity == 0.0:
            for j in range(len(self.sortedOrderList)):
                [p, q] = [self.sortedOrderList[j].price, self.sortedOrderList[j].quantity]
                if order.price == p:
                    self.sortedOrderList.pop(j)
                    break
        elif order.quantity == 0.0:
            self._lock.release()
            self.update_delete(order)
            self._lock.acquire()

    def update_delete(self, order: Order):
        traded_order = None
        self._lock.acquire()

        for i in range(len(self.sortedOrderList)):
            if i < len(self.sortedOrderList) and order.price == self.sortedOrderList[i].price:
                self.sortedOrderList[i].quantity = order.quantity
                if order.quantity == 0:
                    traded_order = self.sortedOrderList.pop(i)

        self._lock.release()
        return traded_order


class OrderBook:
    def __init__(self, market, depth=30, display_depth=30):
        self.market = market
        self.lock = threading.Lock()
        self.bids = OrderBookSide(side=BID, depth=depth, lock=self.lock)
        self.asks = OrderBookSide(side=ASK, depth=depth, lock=self.lock)
        self.display_depth = display_depth
        self.depth = depth
        self.msg = {}
        self.mid = None


    def add_modify_delete(self, order : Order, side, my_order=False):
        order.side = side
        if side is BID:
            if len(self.asks) > 0 and order.price >= self.asks.sortedOrderList[0].price:
                # crossed
                return
            self.bids.add_modify_delete(order, my_order=my_order)
        else:
            if len(self.bids) > 0 and order.price <= self.bids.sortedOrderList[0].price:
                # crossed
                return
            self.asks.add_modify_delete(order, my_order=my_order)

    def update_delete(self, order : Order, side):
        traded_orders = []
        order.side = side
        while len(self.bids) > 0 and self.bids.sortedOrderList[0].price > order.price:
            traded_orders.append(self.bids.sortedOrderList.pop(0))
        while len(self.asks) > 0 and self.asks.sortedOrderList[0].price < order.price:
            traded_orders.append(self.asks.sortedOrderList.pop(0))

        if side is BID:
            traded_orders.append(self.bids.update_delete(order))
        else:
            traded_orders.append(self.asks.update_delete(order))
        return traded_orders

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


    def binance_incremental_trade_update_handler(self, msg):
        trade_price = float(msg['p'])
        mm_is_buying = bool(msg['m'])
        order = Order(trade_price, 0.0)
        if mm_is_buying:
            traded_order = self.update_delete(order, side='b')
        else:
            traded_order = self.update_delete(order, side='a')
        self.msg =msg
        self.msg = {}
        self.health_check()
        return traded_order

    def getSpread(self):
        ret = -1
        if len(self.bids) > 0 and len(self.asks) > 0:
            ret = float(self.asks.sortedOrderList[0].price - self.bids.sortedOrderList[0].price)
            if ret > 3.0:
                ret = C.FAIL + str(ret) + C.ENDC
            elif ret > 2.0:
                ret = C.WARNING + str(ret) + C.ENDC
            else:
                ret = str(ret)

        return str(ret)

    def getMidPrice(self) -> float:
        if len(self.bids) > 0 and len(self.asks) > 0:
            self.mid = self.bids.sortedOrderList[0].price + self.asks.sortedOrderList[0].price
            self.mid /= 2
        return self.mid


    def getDepthOfPrice(self, price, side='b'):
        if side == 'b':
            for i in range(len(self.bids.sortedOrderList)):
                if price >= self.bids.sortedOrderList[i].price:
                    return i
        else:
            for i in range(len(self.asks.sortedOrderList)):
                if price <= self.asks.sortedOrderList[i].price:
                    return i
        return self.depth


    def getTotalFromDepth(self, depth, side='b'):
        total = 0.0
        if side == 'b' and depth < len(self.bids):
            for i in range(depth):
                total += self.bids.sortedOrderList[i].quantity
        elif side == 'a' and depth < len(self.asks):
            for i in range(depth):
                total += self.asks.sortedOrderList[i].quantity
        return total

    def getTotalFromPrice(self, price, side='b'):
        return self.getTotalFromDepth(self.getDepthOfPrice(price, side), side)

    def get_total_order_count(self) -> int:
        return len(self.bids) + len(self.asks)

    def __str__(self):
        self.health_check()
        self.mid_str = None
        if len(self.bids) > 0 and len(self.asks) > 0:
            self.mid_str = self.bids.sortedOrderList[0].price + self.asks.sortedOrderList[0].price
            self.mid_str /= 2

        ret = "Mid\t\t= " + str(self.mid_str) + "\nSpread\t\t= " + self.getSpread() + "\n" \
              "________________________________________________________________\n"
        ret += "\t\tBID\t\t|\t\tASK\t\t\n"
        for i in range(max(len(self.bids), len(self.asks))):
            if i < len(self.bids):
                [p, q, pos] = [self.bids.sortedOrderList[i].price,
                               self.bids.sortedOrderList[i].quantity,
                               self.bids.sortedOrderList[i].position_quantity]
                if pos > 0:
                    ret += C.OKGREEN + " {:12.6f}".format(p) + '\t' + "{:12.6f}".format(q) + C.ENDC + '\t|'
                else:
                    ret += " {:12.6f}".format(p)+'\t'+"{:12.6f}".format(q)+'\t|'
            else:
                ret += "\t\t\t\t|"

            if i < len(self.asks):
                [p, q, pos] = [self.asks.sortedOrderList[i].price,
                               self.asks.sortedOrderList[i].quantity,
                               self.asks.sortedOrderList[i].position_quantity]
                if pos > 0:
                    ret += C.FAIL+" {:12.6f}".format(p)+'\t'+"{:12.6f}".format(q)+C.ENDC+'\n'
                else:
                    ret += " {:12.6f}".format(p) + '\t' + "{:12.6f}".format(q) + '\n'
            else:
                ret += "\n"

            if i >= self.display_depth:
                break

        return ret


    def health_check(self):
        if len(self.bids) > 0 and len(self.asks) > 0:
            # verify book is not crossed
            if self.bids.sortedOrderList[0].price > self.asks.sortedOrderList[0].price:
                raise Exception(str(self.bids.sortedOrderList[0]) +" BID -- CROSSED WITH -- ASK " +
                                str(self.asks.sortedOrderList[0]))

class C:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
