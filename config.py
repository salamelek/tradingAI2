positionSimConfig = {
    "sl": 0.2,     # in PERCENTS
    "tp": 0.35,
    "maxLength": 50,
}

# this is to allow more flexibility
actualPositionConfig = {
    "sl": 0.2,     # in PERCENTS
    "tp": 0.3
}

# the parameters for the knn algo
knnConfig = {
    "k": 5,
    "gridScale": 0.5,       # play with this for optimal speed but be warned about varying results
    "threshold": 2,
    "sameDirectionRatio": 1
}
