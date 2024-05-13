from config import knnConfig, positionSimConfig

import numpy as np


def euclideanDistance(a: list, b: list) -> float:
    """
    Returns the Euclidean distance of the two given points.

    :param a:
    :param b:
    :return:
    """

    if len(a) != len(b):
        raise Exception("The two points must have the same length")

    dist = 0

    for i in range(len(a)):
        dist += (a[i] - b[i]) ** 2

    return np.sqrt(dist)


def euclideanSquaredDist(a: list, b: list) -> float:
    """
    Returns the squared Euclidean distance of the two given points.
    Faster than Euclidean
    works (a little) faster, but the dist threshold should be adjusted

    :param a:
    :param b:
    :return:
    """

    if len(a) != len(b):
        raise Exception("The two points must have the same length")

    dist = 0

    for i in range(len(a)):
        dist += (a[i] - b[i]) ** 2

    return dist


def getPriceDirection(klines: list[dict], index: int, interval: int = 3) -> float:
    """
    Returns the price direction
    Calculates using the difference of sma3close - sma3open (very similar to sma3 slope)

    :return:
    """

    sma3close = sum([kline["close"] for kline in klines[(index - interval + 1):(index + 1)]]) / interval
    sma3open = sum([kline["open"] for kline in klines[(index - interval + 1):(index + 1)]]) / interval

    if sma3close == [] or sma3open == []:
        raise Exception("something went wrong with sma calculation!")

    return sma3close - sma3open


def getXMinusY(klines: list[dict], index: int, x: int = 5, y: int = 10) -> float:
    """
    Returns the diff between x and y

    :param y:
    :param x:
    :param klines:
    :param index:
    :return:
    """

    smax = sum([kline["close"] for kline in klines[(index - x + 1):(index + 1)]]) / x
    smay = sum([kline["close"] for kline in klines[(index - y + 1):(index + 1)]]) / y

    return smax - smay


def getSR(threshold: float) -> float:
    """
    Returns how much close to a sr zone the price is

    :return:
    """


def getLastBigMove(threshold: float) -> int:
    """
    Returns how many candles ago the price skyrocketed
    if the value is negative, the value fell instead

    For this function to work, I need a function that remembers key levels throughout the simulation


    :param threshold:
    :return:
    """

    pass


def simulatePosition(testKlines: list[dict], entryIndex: int):
    """
    Simulates a position given the testKlines and entryIndex
    Returns 1 if the position should be long, 0 if hold, -1 if short

    :param testKlines:
    :param entryIndex:
    :return:
    """

    try:
        # we enter the position after candle close
        entryPrice = testKlines[entryIndex + 1]["open"]
    except IndexError:
        # end of testKlines
        return 0

    # long position params
    longTp = entryPrice + (entryPrice / 100) * positionSimConfig["tp"]
    longSl = entryPrice - (entryPrice / 100) * positionSimConfig["sl"]
    longSlTriggered = False

    # short position params
    shortTp = entryPrice - (entryPrice / 100) * positionSimConfig["tp"]
    shortSl = entryPrice + (entryPrice / 100) * positionSimConfig["sl"]
    shortSlTriggered = False

    # loop through every kline after the position opening and check if it hits the sl or tp
    for posCurrIndex in range(positionSimConfig["maxLength"]):
        klineIndex = posCurrIndex + entryIndex

        try:
            currentLow = testKlines[klineIndex]["low"]
            currentHigh = testKlines[klineIndex]["high"]
        except IndexError:
            # end of testKlines
            return 0

        # check stopLoss hits
        if currentLow < longSl:
            longSlTriggered = True

        if currentHigh > shortSl:
            shortSlTriggered = True

        # check if both sl hit
        if longSlTriggered and shortSlTriggered:
            # this handles also big candles that go from tp to sl
            return 0

        # return short position
        if currentLow < shortTp and not shortSlTriggered:
            return -1

        # return long position
        if currentHigh > longTp and not longSlTriggered:
            return 1

    # if nothing happens, the position is too long (inconclusive)
    return 0


class Knn:
    def __init__(self, trainKlines: list[dict], padding: int = 100, bufferLen: int = 1000) -> None:
        self.padding = padding

        self.trainKlines: list[dict] = trainKlines
        self.trainDataPoints: list[list] = self.extractDataPointsBulk(self.trainKlines)
        self.dataPointGrid: dict = self.distributeDataPoints(self.trainDataPoints)

        self.klineBufferLen: int = bufferLen
        self.klineBuffer: list = []

    @staticmethod
    def getDpKey(dataPoint: list or tuple) -> tuple:
        key = []

        for i in range(len(dataPoint)):
            try:
                key.append(int(dataPoint[i] // knnConfig["gridScale"]))
            except (ValueError, TypeError):
                # for NaN and None values
                key = ["Not calculated dataPoints"]
                break

        return tuple(key)

    def extractDataPointsBulk(self, klines: list[dict]) -> list[list[float]]:
        """
        Returns a 1:1 list of dataPoints
        EVERY DATAPOINT HAS ITS OWN KLINE (they are of the sem length)

        This is used to convert countless klines to dataPoints once, not a few klines countless times

        :param klines:
        :return:
        """

        print("Extracting dataPoints...")

        dataPoints = []

        for i in range(len(klines)):
            # pad the beginning with empty dataPoints
            if i < self.padding:
                dp = []

            else:
                # here a dataPoint could/should have many characterizations:
                # direction, support, consolidation, whatever

                dp = [
                    getXMinusY(klines, i, x=5, y=10),
                    getPriceDirection(klines, i, interval=10),
                ]

            dataPoints.append(dp)

        print("Done!\n")

        return dataPoints

    def extractDataPointSingle(self, kline: dict) -> list[float]:
        """
        This method relies on the fact that THE KLINES WILL BE GIVE IN THE CORRECT ORDER, WITHOUT GAPS

        :param kline:
        :return:
        """

        self.klineBuffer.append(kline)

        if len(self.klineBuffer) < self.padding:
            return []

        if len(self.klineBuffer) > self.klineBufferLen:
            self.klineBuffer.pop(0)

        dp = [
            getXMinusY(self.klineBuffer, -1, x=5, y=10),
            getPriceDirection(self.klineBuffer, -1, interval=10)
        ]

        return dp

    def distributeDataPoints(self, dataPoints: list[list]) -> dict:
        """
        Returns a dict that represents the buckets of data
        {(quadrant tuple): [points in quadrant]}

        the problem is that once in the quadrant, we do not have the dp index anymore, so we add it as a dict

        :return: {(quadrant tuple): [{"coords": dataPoint, "dpIndex": dataPointIndex}, ...]}
        """

        print("Distributing dataPoints...")

        gridDp = {}

        # place each dataPoint in its quadrant
        for dataPointIndex in range(len(dataPoints)):
            dataPoint = dataPoints[dataPointIndex]

            key = self.getDpKey(dataPoint)

            try:
                gridDp[key].append({"coords": dataPoint, "dpIndex": dataPointIndex})
            except KeyError:
                gridDp[key] = [{"coords": dataPoint, "dpIndex": dataPointIndex}]

        print("Done!\n")

        return gridDp

    @staticmethod
    def getAreaKeys(ringCount: int, originKey: list) -> list[tuple]:
        dimNum = len(originKey)
        keys = []

        nthOdd = ringCount * 2 + 1

        for i in range(nthOdd ** dimNum):
            newKey = []

            for j in range(dimNum):
                offset = (i // (nthOdd ** (dimNum - (j + 1)))) % nthOdd
                newKey.append(int(originKey[j] + offset))

            keys.append(tuple(newKey))

        return keys

    def getKnn(self, dataPoint: list or tuple) -> list:
        """
        Returns the k nearest neighbors of the given dataPoint
        It can return an empty list if there are no close neighbours

        THE GIVEN DATAPOINT MUST NOT INCLUDE NaN OR None VALUES
        IF THE DATAPOINT IS INVALID, THEN SET IT TO []

        :param dataPoint:
        :return:
        """

        dimNum = len(dataPoint)

        if dimNum == 0:
            return []

        # get the quadrant of the origin
        originKey = self.getDpKey(dataPoint)
        originKey = [x - 1 for x in originKey]

        closeNn = []
        ringCount = 0

        # IMPORTANT this is an approximation since we're taking squares and not circles
        while len(closeNn) < knnConfig["k"]:
            # reset closeNn because of +=
            closeNn = []

            # get the keys of the buckets (in a ring-like pattern)
            keys = self.getAreaKeys(ringCount, originKey)

            # get the nn from the buckets
            for key in keys:
                try:
                    closeNn += self.dataPointGrid[key]
                except KeyError:
                    # quadrant is empty (doesn't exist)
                    pass

            # check if it's past the threshold (if it is, search no more)
            if ringCount * knnConfig["gridScale"] > knnConfig["threshold"]:
                break

            ringCount += 1

        # get the knn
        knn = []

        for dp in closeNn:
            trainDp = dp["coords"]
            index = dp["dpIndex"]

            # distance = euclideanDistance(trainDp, dataPoint)
            distance = euclideanSquaredDist(trainDp, dataPoint)

            # if the distance is trash, just continue
            if distance > knnConfig["threshold"]:
                continue

            neighbour = {"distance": distance, "dpIndex": index}

            # if the list is still empty, just append the neighbour
            if len(knn) < knnConfig["k"]:
                knn.append(neighbour)
                continue

            # lower distance first, higher at the end
            knn = sorted(knn, key=lambda x: x["distance"])

            # replace the worst neighbour with the better one
            if distance < knn[-1]["distance"]:
                knn[-1] = neighbour

        return knn

    def getPositionDirection(self, dataPoint: list or tuple) -> int:
        """
        Returns 1 for long, 0 for hold and -1 for short positions

        :param dataPoint:
        :return:
        """

        knn = self.getKnn(dataPoint)

        if len(knn) < knnConfig["k"]:
            # not all neighbours were close enough
            return 0

        # simulate positions
        counter = 0
        for nn in knn:
            counter += simulatePosition(self.trainKlines, nn["dpIndex"])

        # check if [ratio] positions agree
        if counter >= len(knn) * knnConfig["sameDirectionRatio"]:
            return 1

        elif counter <= len(knn) * knnConfig["sameDirectionRatio"] * -1:
            return -1

        return 0
