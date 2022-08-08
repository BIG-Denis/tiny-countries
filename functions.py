
from random import shuffle, randrange


def make_dict3(res, minx, maxx):
    def splitter9(res: list):
        shuffle(res)
        return (res[0:3], res[3:6], res[6:9])
    res = splitter9(res)
    return ({res[0][i] : randrange(minx, maxx) for i in range(3)},
            {res[1][i] : randrange(minx, maxx) for i in range(3)},
            {res[2][i] : randrange(minx, maxx) for i in range(3)})


def make_dict4(res, minx, maxx):
    def splitter12(res: list):
        shuffle(res)
        return (res[0:3], res[3:6], res[6:9], res[9:12])
    res = splitter12(res)
    return ({res[0][i] : randrange(minx, maxx) for i in range(3)},
            {res[1][i] : randrange(minx, maxx) for i in range(3)},
            {res[2][i] : randrange(minx, maxx) for i in range(3)},
            {res[3][i] : randrange(minx, maxx) for i in range(3)})


def make_dict4x2(res, minx, maxx):
    def splitter12(res: list):
        shuffle(res)
        return (res[0:3], res[3:6], res[6:9], res[9:12])
    res = splitter12(res)
    return ({res[0][i] : randrange(minx, maxx) for i in range(3)},
            {res[1][i] : randrange(minx, maxx) for i in range(3)},
            {res[2][i] : randrange(minx, maxx) for i in range(3)},
            {res[3][i] : round(randrange(minx, maxx) * 4) for i in range(3)})
