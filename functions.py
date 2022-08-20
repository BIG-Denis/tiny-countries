
from math import tanh
from random import shuffle, randrange


class Player_retriever(object):

    def __init__(self):
        self.most_prod: list = []
        self.most_sell: list = []
        self.other: list = []
        self.production: dict = {i : False for i in range(11, 20)}
        self.sells: dict = {**{i : False for i in range(11, 20)}, **{i : False for i in range(21, 24)}}

    def __str__(self):
        return f"{self.production}\n{self.sells}\n"

    def __repr__(self):
        return str(self)

    def to_dicts(self):
        for id in self.most_prod:
            self.production[id] = True
        for id in self.most_sell:
            self.sells[id] = True


def gen_income_ress(minr, maxr, mins, maxs, big_field_k, big_sell_k, hard_res_k):

    def gen():
        nonlocal ids
        plrs = [Player_retriever(), Player_retriever(), Player_retriever()]
        for id in ids:
            shuffle(plrs)
            plrs[0].most_prod.append(id)
            plrs[1].most_sell.append(id)
            plrs[2].other.append(id)
        return plrs

    def check_all(_iterable):
        for elem in _iterable:
            if not check(elem):
                return False
        return True

    def check(plr: Player_retriever):
        if len(plr.most_prod) == len(plr.most_sell) == len(plr.other) == 3:
            return True
        return False

    ids = list(range(11, 20))
    ids_hard = list(range(21, 24))
    shuffle(ids_hard)
    hard_res_dict = {i : j for i, j in zip(range(3), ids_hard)}
    tmp = gen()
    while not check_all(tmp):
        tmp = gen()

    for plr in tmp:
        plr.to_dicts()

    for num, plr in enumerate(tmp):
        for key, value in plr.production.items():
            plr.production[key] = randrange(minr, maxr)
            if value:
                 plr.production[key] *= big_field_k
        for key, value in plr.sells.items():
            plr.sells[key] = randrange(mins, maxs)
            if value:
                plr.sells[key] *= big_sell_k

    for i, plr in zip(range(3), tmp):
        for key, value in plr.sells.items():
            if key in list(range(21, 24)):
                plr.sells[key] *= hard_res_k
        plr.sells[ids_hard[i]] *= big_sell_k

    # normalize dicts
    for plr in tmp:
        plr.sells = {k : int(v) for k, v in plr.sells.items()}

    tmp1 = [elem.production for elem in tmp]
    tmp2 = [elem.sells for elem in tmp]

    return (tmp1, tmp2)


def war_lucky_chances(x: float):
    return max(0, tanh(0.8 * x - 0.3))


def war_conquest(x: float):
    return 1 / (1 + 2.71**(-0.8 * x)) - 0.5


def war_normalize(x: float):
    return max(0, (tanh(x - 0.7)) / 2.5)
