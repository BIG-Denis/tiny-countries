
from random import randrange


def fun(soldiers, minp, maxp):
    return max(0, round(soldiers - soldiers * (randrange(minp, maxp+1)) / 100))


print(fun(1, 10, 20))

