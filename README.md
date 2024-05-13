> THIS IS JUST A DUMMY REPO, THE ORIGINAL IS PRIVATE SINCE SOME PASSWORDS ARE NEEDED TO WORK WITH DATABASES


# Trading bot

This is my attempt at making a trading bot from scratch. 

From a macro perspective, we give to the bot a decision maker and some new candles, and it will use the given decision
maker to place an order or do nothing. The hard part here is the decision maker.

## KNN - the decision maker

This class is based on the KNN approach. It places the historical data in a space, and it then compares the new entry to
the existing candles. The only difference that I have with a "normal" approach is that the data is not labeled, but
rather simulated afterward.

The function that we care about is `getPositionDirection()`. It returns the side on which we will take the position
given the most recent data point.

> Data point: a point in the n-dimensional space from where the class gets the neighbours

We can convert our OHLC candle data to data points using the class's functions `extractDataPointsBulk()` or
`extractDataPointSingle()`. The first one is used on a larger set of candles, the second one for a single candle at a
time. Once we have our latest data point, we can feed it to the `getPositionDirection()` function.

The function will then find the nearest k neighbours. I sped up this process by subdividing the space into a grid, that
acts like a hashMap. Once the neighbours are found, we simulate an open position for each nearest neighbour. If all the
simulated positions "agree" that the price will go in some direction, we return the said direction.


## Backtest - the backtester

This class is used to test the effectiveness of the given decision maker. It simulates a live marked based on the given
historical data and simulates the positions using the given parameters. At the end of the simulation, it plots the
k-line and all the placed positions. It also prints some statistical data and evaluation factors like profit factor or
the maximum draw-down.