"""
The main body of the bot, where everything will be run from
"""

import config
from dataGetter import getCryptoDataBinance
from Knn import Knn
from backtest import Backtest

import pickle


def runBacktest(decisionMaker, simKlines, maxOpenPos):
    backtest = Backtest(simKlines, decisionMaker, maxOpenPos)

    with open("backtest.pickle", "wb") as f:
        pickle.dump(backtest, f)

    print()
    print(config.knnConfig)
    print(config.positionSimConfig)
    print(config.actualPositionConfig)
    print(backtest)
    backtest.plot()


if __name__ == '__main__':
    # load the klines for training
    trainKlines = getCryptoDataBinance("./klineData/binanceData/BTCUSDT-1m-2023.csv")
    simKlines = getCryptoDataBinance("./klineData/binanceData/BTCUSDT-1m-2024/BTCUSDT-1m-2024-01.csv")

    # initialise a decisionMaker given the train klines
    brain = Knn(trainKlines, padding=100, bufferLen=100)

    # run the backtest
    runBacktest(brain, simKlines, 100)
