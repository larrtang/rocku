#!/usr/bin/python

from binance.client import Client
from binance.websockets import BinanceSocketManager
import os
import sys
import traceback
import logging
import queue
import threading
import time

from OrderBook import OrderBook, Order
from MarketState import MarketState
from TestTrader import TestTrader
from Grapher import Grapher
import Playbook


logging.basicConfig(filename="TheMaker.log", filemode='w', level=logging.DEBUG)
logger = logging.getLogger("BinanceEngine")

class EventType:
    DEPTH = "depth_event"
    TRADE = "trade_event"


class BinanceTradeEngine:
    def __init__(self, market='BTCUSDT'):
        self.api_key = os.getenv("binance_api_key")
        self.api_secret = os.getenv("binance_api_secret")
        self.client = Client(self.api_key, self.api_secret)
        logger.info("Starting Binance Trading Engine.")
        self.market = market
        self.__process_initial_book_state()
        logger.info("Book state initialized.")
        self.trader = TestTrader()
        #self.trader = Playbook.OGTrader_BTC()
        self.event_buffer = queue.Queue()
        self.event_thread = threading.Thread(target=self.event_loop)

        self.socketManager = BinanceSocketManager(self.client, user_timeout=60)
        self.book_diff = self.socketManager.start_depth_socket(market, self.on_depth_message)
        self.trade_stream = self.socketManager.start_trade_socket(market, self.on_trade_message)
        self.PRINT_BOOK = True
        self.grapher = Grapher()
        self.graphing = False
        self.tradingOn = True
        self.alive = True

    def start(self):
        self.socketManager.start()
        logger.info("Socket Manager started.")
        self.event_thread.start()
        logger.info("Event thread started.")

    def stop(self):
        self.socketManager.close()
        logger.info("Socket Manager closed.")
        self.alive = False
        self.event_thread.join()
        logger.info("Event thread killed.")

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

    def event_loop(self):
        global done
        while self.alive:
            if not self.event_buffer.empty():
                (event_type, msg) = self.event_buffer.get()
                if event_type == EventType.DEPTH:
                    self.depthUpdateHandler(msg)
                elif event_type == EventType.TRADE:
                    self.tradeUpdateHandler(msg)

    def on_depth_message(self, msg):
        self.event_buffer.put((EventType.DEPTH, msg))

    def on_trade_message(self, msg):
        self.event_buffer.put((EventType.TRADE, msg))

    def depthUpdateHandler(self, msg):
        try:
            self.order_book.binance_incremental_book_update_handler(msg)
            self.market_state.binance_incremental_depth_update_handler(msg)

            print(self.trader)
            if self.PRINT_BOOK:
                print(self.market_state)
            if self.tradingOn:
                self.trader.on_depth_update(self.market_state)
        except Exception as e:
            print("Exception caught in depth update")
            print(e)
            print(e.args)
            print("LAST TRADE: " + str(self.market_state.last_trade))
            print()
            print(self.market_state)
            logger.critical("Exception caught in depth update")
            logger.critical(msg=e)
            logger.critical(msg="LAST TRADE: "+str(self.market_state.last_trade))
            logger.critical(msg=self.market_state)
            self.socketManager.close()
            traceback.print_exc()
    done = False

    def tradeUpdateHandler(self, msg):
        try:
            self.market_state.binance_incremental_trade_update_handler(msg)
            if self.graphing:
                self.grapher.update_graph(float(msg['p']), msg['m'])
            if self.tradingOn:
                self.trader.on_trade_update(self.market_state)

            #self.done = True
            print(self.trader)
            if self.PRINT_BOOK:
                print(self.market_state)
        except Exception as e:
            print("Exception caught in trade update")
            print(e)
            print(e.args)
            print("LAST TRADE: " + str(self.market_state.last_trade))
            print()
            print(self.market_state)
            logger.critical("Exception caught in trade update")
            logger.critical(msg=e)
            logger.critical(msg="LAST TRADE: " + str(self.market_state.last_trade))
            logger.critical(msg=self.market_state)
            self.socketManager.close()
            traceback.print_exc()


if __name__ == "__main__":
    engine = BinanceTradeEngine()
    engine.start()

