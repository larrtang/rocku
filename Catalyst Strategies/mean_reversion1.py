import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#from logbook import Logger
import talib
from catalyst import run_algorithm
from catalyst.api import (record, symbol, order_target_percent,set_commission)
from catalyst.exchange.utils.stats_utils import extract_transactions

NAMESPACE = 'dual_moving_average'
#log = Logger(NAMESPACE)




###
###     catalyst run -f Catalyst.py -x binance -s 2019-6-16 --end 2019-6-17 -c usd --capital-base 10000 --data-frequency=minute
###     catalyst run -f Catalyst.py -x binance -s 2019-6-16 --end 2019-6-17 -c usd --capital-base 10000 --data-frequency=minute
###







def VWAP(prices, volumes):
    return (prices * volumes).sum() / volumes.sum()



def initialize(context):
    context.i = 0
    context.asset = symbol('btc_usdt')
    context.base_price = None
    context.trade_price = None
    context.adx_prev = 0
    context.adx_sell = True
    context.last_price = 0
    context.counter = 0
    context.timer = 0
    context.trade_timer = 100

    set_commission(maker=0, taker=0)

def handle_data(context, data):
    # define the windows for the moving averages
    short_window = 5
    mid_window = 70
    long_window = 150

    # Skip as many bars as long_window to properly compute the average
    context.i += 1
    if context.i < long_window:
        return
    
    
    
    price = data.current(context.asset, 'price')
    
    # Compute moving averages calling data.history() for each
    # moving average with the appropriate parameters. We choose to use
    # minute bars for this simulation -> freq="1m"
    # Returns a pandas dataframe.
    short_data = data.history(context.asset,
                              'price',
                              bar_count=short_window,
                              frequency="15m",
                              )
    short_mavg = short_data.mean()

    mid_data = data.history(context.asset,
                              'price',
                              bar_count=mid_window,
                              frequency="15m",
                              )
    mid_mavg = mid_data.mean()

    long_data = data.history(context.asset,
                             'price',
                             bar_count=long_window,
                             frequency="15m",
                             )
    candle_data = data.history(context.asset,
                             fields=['price', 'open', 'high', 'low', 'close'],
                             bar_count=120,
                             frequency="5m",
                             )                         
    long_mavg = long_data.mean()

    adx_len = 40
    adx_thresh = 20
    adx = talib.ADX(candle_data.high.as_matrix(), candle_data.low.as_matrix(), 
    candle_data.close.as_matrix(), timeperiod = adx_len)[-1]
    mDI = talib.MINUS_DI(candle_data.high.as_matrix(), candle_data.low.as_matrix(), 
    candle_data.close.as_matrix(), timeperiod = adx_len)[-1]
    pDI = talib.PLUS_DI(candle_data.high.as_matrix(), candle_data.low.as_matrix(), 
    candle_data.close.as_matrix(), timeperiod = adx_len)[-1]
    
    rsi = talib.RSI(candle_data.close.as_matrix(), timeperiod=14)[-1]
    long_mavg = talib.EMA(long_data, timeperiod=long_window)[-1]

    prices14 = data.history(context.asset,['price','volume'], 14 , "5m")
    vwap = VWAP(prices14["price"], prices14["volume"])
    
    # Let's keep the price of our asset in a more handy variable

    # If base_price is not set, we use the current value. This is the
    # price at the first bar which we reference to calculate price_change.
    if context.base_price is None:
        context.base_price = price
    price_change = (price - context.base_price) / context.base_price

    # Save values for later inspection
    record(price=price,
           cash=context.portfolio.cash,
           adx=adx,
           adx_prev=context.adx_prev,
           mDI=mDI,
           pDI=pDI,
           price_change=price_change,
           short_mavg=short_mavg,
           mid_mavg=mid_mavg,
           long_mavg=long_mavg,
           vwap = vwap)

    # Since we are using limit orders, some orders may not execute immediately
    # we wait until all orders are executed before considering more trades.
    orders = context.blotter.open_orders
    if len(orders) > 0:
        return

    # Exit if we cannot trade
    if not data.can_trade(context.asset):
        return

    # We check what's our position on our portfolio and trade accordingly
    pos_amount = context.portfolio.positions[context.asset].amount

    # Trading logic
    # if short_mavg > long_mavg and pos_amount == 0:
    #     # we buy 100% of our portfolio for this asset
    #     order_target_percent(context.asset, 1)
    # elif short_mavg < long_mavg and pos_amount > 0:
    #     # we sell all our positions for this asset
    #     order_target_percent(context.asset, 0)
    if context.trade_price != None:
        trade_change = (price - context.trade_price) / (context.trade_price)
    else:
        trade_change = 0
    if (short_mavg > long_mavg) and pDI > mDI and price >= long_mavg and pos_amount == 0 and context.adx_sell is True:
        if context.timer == 0:
            # we buy 100% of our portfolio for this asset
            order_target_percent(context.asset, 1)
            context.trade_price = price
            
            context.adx_sell = False

    elif (pDI < mDI):
        # we sell all our positions for this asset
        if pos_amount > 0:
            pass
            #order_target_percent(context.asset, 0)
        #else:
        context.adx_sell = True

    if pos_amount > 0 and ((trade_change > 0.01)):
        order_target_percent(context.asset, 0.5)
    if pos_amount > 0 and ((trade_change > 0.02 or trade_change < -0.01)):
        order_target_percent(context.asset, 0)
        context.timer = 1

    if context.timer > context.trade_timer:
        context.timer = 0
        context.adx_sell = True

    elif context.timer > 0:
        context.timer += 1
    context.last_price = price
    if context.counter < 5:
        context.counter += 1
    else:
        context.adx_prev = adx
        context.counter = 0


def analyze(context, perf):
    #print(perf)
    # Get the quote_currency that was passed as a parameter to the simulation
    exchange = list(context.exchanges.values())[0]
    quote_currency = exchange.quote_currency.upper()

    # First chart: Plot portfolio value using quote_currency
    ax1 = plt.subplot(511)
    perf.loc[:, ['portfolio_value']].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('Portfolio Value\n({})'.format(quote_currency))
    start, end = ax1.get_ylim()
    ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    # Second chart: Plot asset price, moving averages and buys/sells
    ax2 = plt.subplot(512, sharex=ax1)
    perf.loc[:, ['price','short_mavg','mid_mavg', 'long_mavg', 'vwap']].plot(
        ax=ax2,
        label='Price')
    ax2.legend_.remove()
    ax2.set_ylabel('{asset}\n({quote})'.format(
        asset=context.asset.symbol,
        quote=quote_currency
    ))
    start, end = ax2.get_ylim()
    ax2.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    transaction_df = extract_transactions(perf)
    if not transaction_df.empty:
        buy_df = transaction_df[transaction_df['amount'] > 0]
        sell_df = transaction_df[transaction_df['amount'] < 0]
        ax2.scatter(
            buy_df.index.to_pydatetime(),
            perf.loc[buy_df.index, 'price'],
            marker='^',
            s=100,
            c='green',
            label=''
        )
        ax2.scatter(
            sell_df.index.to_pydatetime(),
            perf.loc[sell_df.index, 'price'],
            marker='v',
            s=100,
            c='red',
            label=''
        )

    # Third chart: Compare percentage change between our portfolio
    # and the price of the asset
    ax3 = plt.subplot(513, sharex=ax1)
    perf.loc[:, ['algorithm_period_return', 'price_change']].plot(ax=ax3)
    ax3.legend_.remove()
    ax3.set_ylabel('Percent Change')
    start, end = ax3.get_ylim()
    ax3.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

   #Fourth chart: Plot our cash
    ax4 = plt.subplot(514, sharex=ax1)
    perf.cash.plot(ax=ax4)
    ax4.set_ylabel('Cash\n({})'.format(quote_currency))
    start, end = ax4.get_ylim()
    ax4.yaxis.set_ticks(np.arange(0, end, end / 5))

    ax5 = plt.subplot(515, sharex=ax1)
    perf.loc[:, ['adx', 'mDI', 'pDI', 'adx_prev']].plot(
        ax=ax5,
        label='Price')
    ax5.set_ylabel('ADX\n({})'.format(quote_currency))
    start, end = ax5.get_ylim()
    ax5.yaxis.set_ticks(np.arange(0, end, end / 5))


    plt.show()


if __name__ == '__main__':

    run_algorithm(
            capital_base=1000,
            data_frequency='minute',
            initialize=initialize,
            handle_data=handle_data,
            analyze=analyze,
            exchange_name='binance',
            algo_namespace=NAMESPACE,
            quote_currency='btc',
            start=pd.to_datetime('2018-11-1', utc=True),
            end=pd.to_datetime('2018-11-9', utc=True),
        )
