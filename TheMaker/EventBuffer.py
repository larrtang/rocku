import queue
import threading
import traceback
import logging
import sys

from MarketState import MarketState
logger = logging.getLogger(__name__)

class EventType:
    DEPTH = "depth_event"
    TRADE = "trade_event"

class EventBuffer:
    """
    Buffers order book depth updates and verifies validity
    """

    def __init__(self, market_state: MarketState):
        self.__buffer__ = queue.Queue()
        self.thread = threading.Thread(target=self.process)
        self.market_state = market_state
        self.order_book = self.market_state.order_book
        self.PRINT_BOOK = True
        self.graphing = False
        self.tradingOn = True
        self.alive = True
    def start(self):
        self.thread.start()

    def process(self):
        while self.alive:
            if not self.__buffer__.empty():
                (event_type, msg) = self.__buffer__.get()
                if event_type == EventType.DEPTH:
                    try:
                        self.order_book.binance_incremental_book_update_handler(msg)
                        self.market_state.binance_incremental_depth_update_handler(msg)
                        self.alive = False

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
                        logger.critical("Exception caught in depth update")
                        logger.critical(msg=e)
                        logger.critical(msg="LAST TRADE: " + str(self.market_state.last_trade))
                        self.socketManager.close()
                        traceback.print_exc()

                elif event_type == EventType.TRADE:
                    try:
                        self.market_state.binance_incremental_trade_update_handler(msg)
                        self.market_state.setLastTrade(msg)
                        if self.graphing:
                            self.grapher.update_graph(float(msg['p']), msg['m'])
                        if self.tradingOn:
                            self.trader.on_trade_update(self.market_state)

                        # self.done = True
                        print(self.trader)
                        if self.PRINT_BOOK:
                            print(self.market_state)

                    except Exception as e:
                        print("Exception caught in trade update")
                        print(e)
                        print(e.args)
                        print("LAST TRADE: " + str(self.market_state.last_trade))
                        logger.critical("Exception caught in trade update")
                        logger.critical(msg=e)
                        logger.critical(msg="LAST TRADE: " + str(self.market_state.last_trade))
                        self.socketManager.close()
                        traceback.print_exc()

            else:
                self.alive = False
                raise Exception()

    def put_message(self, msg, event_type):
        event = (event_type, msg)
        self.__buffer__.put(event)
