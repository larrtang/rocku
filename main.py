from Coinbase import Coinbase
from Binance import Binance

def main():
    coinbase = Coinbase()
    binance = Binance()
    while 1 == 1:
        print(coinbase.getLastTradedPrice('ETH-USD'))
        print(binance.getLastTradedPrice('ETHUSDT'))


if __name__ == "__main__":
    main()
