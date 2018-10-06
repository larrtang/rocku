from Coinbase import Coinbase
from Binance import Binance
from engine import Engine

def main():
    engine = Engine()
    print(engine.getTotalPortfolioValue())
    engine.run()

if __name__ == "__main__":
    main()
 