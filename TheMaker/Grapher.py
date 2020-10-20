import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np

plt.style.use('ggplot')


def live_plotter(x_vec, y1_data, y2_data, y3_data, line1, line2, line3, identifier='', pause_time=0.1):
    if line1 == []:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig = plt.figure(figsize=(13, 6))
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line1, = ax.plot(x_vec, y1_data, '-o', color="green",alpha=0.8)
        line2, = ax.plot(x_vec, y2_data, '-o', color='red', alpha=0.8)
        line3, = ax.plot(x_vec, y3_data, '-o', color='skyblue', alpha=0.5)
        # update plot label/title
        plt.ylabel('Price')
        plt.title("time and sales plot")
        plt.show()

    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    line2.set_ydata(y2_data)
    line3.set_ydata(y3_data)
    # adjust limits if new data goes beyond bounds
    if np.min(y3_data) <= line3.axes.get_ylim()[0] or np.max(y3_data) >= line3.axes.get_ylim()[1]:
        plt.ylim([np.min(y3_data) - np.std(y3_data), np.max(y3_data) + np.std(y3_data)])
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    # return line so we can update it again in the next iteration
    return line1, line2, line3



class Grapher:
    size = 120
    x_vec = np.linspace(0, 1, size + 1)[0:-1]
    bid = None
    ask = None
    last = None
    line1 = []
    line2 = []
    line3 = []

    def update_graph(self, last_trade_price: float, side: bool):
        # initialize the line lists
        if self.bid is None:
            self.bid = np.linspace(last_trade_price - 1, last_trade_price + 1, self.size + 1)[0:-1]
        if self.ask is None:
            self.ask = np.linspace(last_trade_price - 1, last_trade_price + 1, self.size + 1)[0:-1]
        if self.last is None:
            self.last = np.linspace(last_trade_price - 1, last_trade_price + 1, self.size + 1)[0:-1]

        if side:
            self.bid[-1] = last_trade_price
            self.ask[-1] = self.ask[-2]
        else:
            self.bid[-1] = self.bid[-2]
            self.ask[-1] = last_trade_price

        self.last[-1] = last_trade_price
        self.line1, self.line2, self.line3 = live_plotter(self.x_vec, self.bid, self.ask, self.last, self.line1, self.line2, self.line3)
        self.bid = np.append(self.bid[1:], 0.0)
        self.ask = np.append(self.ask[1:], 0.0)
        self.last = np.append(self.last[1:], 0.0)