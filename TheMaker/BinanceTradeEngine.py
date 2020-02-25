#!/usr/bin/python

from binance.client import Client
from binance.websockets import BinanceSocketManager
import os
import sys
import traceback

from OrderBook import OrderBook, Order
from MarketState import MarketState
from TestTrader import TestTrader

# import Playbook


class BinanceTradeEngine:
    def __init__(self, market='BTCUSDT'):
        self.api_key = os.getenv("binance_api_key")
        self.api_secret = os.getenv("binance_api_secret")
        self.client = Client(self.api_key, self.api_secret)
        self.market = market
        self.__process_initial_book_state()
        self.trader = TestTrader()
        self.socketManager = BinanceSocketManager(self.client, user_timeout=60)
        self.book_diff = self.socketManager.start_depth_socket(market, self.depthUpdateHandler)
        self.trade_stream = self.socketManager.start_trade_socket(market, self.tradeUpdateHandler)
        self.PRINT_BOOK = True

        self.tradingOn = True

    def start(self):
        self.socketManager.start()

    def __process_initial_book_state(self):
        self.market_state = MarketState(self.market)

        book = self.client.get_order_book(symbol=self.market)
        # print(book, type(book))
        self.order_book = self.market_state.order_book

        for bid in book['bids']:
            self.order_book.add_modify_delete(Order(float(bid[0]), float(bid[1])),
                                              side='b')
        for ask in book['asks']:
            self.order_book.add_modify_delete(Order(float(ask[0]), float(ask[1])),
                                              side='a')
        print(self.order_book)


    def depthUpdateHandler(self, msg):
        try:
            self.order_book.binance_incremental_book_update_handler(msg)

            if self.PRINT_BOOK:
                print(self.market_state)
        except Exception as e:
            print(e)
            print(e.args)
            print("LAST TRADE: "+str(self.market_state.last_trade))
            self.socketManager.close()
            traceback.print_exc()
    done = False

    def tradeUpdateHandler(self, msg):
        try:

            self.market_state.binance_incremental_trade_update_handler(msg)
            self.market_state.setLastTrade(msg)
            if self.tradingOn:
                self.trader.on_trade_event(self.market_state)

            #self.done = True
            if self.PRINT_BOOK and False:
                print(self.market_state)
        except Exception as e:
            print(e)
            print(e.args)
            self.socketManager.close()
            traceback.print_exc()


if __name__ == "__main__":
    engine = BinanceTradeEngine()
    engine.start()

