
from tasks import *
from random import randrange


"""
RESOUSES:
    RAW:
        11 iron    (raw)
        12 food    (raw)
        13 gold    (raw)
        14 oil     (raw)
        15 stone   (raw)
        16 animals (raw)
        17 copper  (raw)
        18 quartz  (raw)
        19 wood    (raw)
    TO_MAKE:
        21 steel (iron + money)
        22 electronic (copper + money)
        23 glass (quartz + money)

TAIVAN OPINION:
    31 neutral
    32 need to be free
    33 need to be annexated to our country
    34 need to be annexated to another country
    35 need to destroy the Taivan

HELP FOR ME:
    a few phases for main game and some for war for the Taivan
    soldiers is making automatic with population in every phase and manual with money
    winning is a counting a final points from every country attribute
    if govrep was negative after winning war it gets positive
    occupation territiries with negative govrep gives positive govrep and backwards
    more ships - army gets on taivan faster
    import product makes +1 to govrep (fix dupe)
    after war need to pay reparations for a few phases
"""


resources_dict = {
    "железо" : 11,
    "еда" : 12,
    "золото" : 13,
    "нефть" : 14,
    "камень" : 15,
    "скот" : 16,
    "медь" : 17,
    "кварц" : 18,
    "дерево" : 19,
    "сталь" : 21,
    "электроника" : 22,
    "стекло" : 23,
    }


def get_resname_by_id(fid: int):
    for name, id in resources_dict.items():
        if id == fid:
            return name
    return None


help_text = """
/help - показать список команд
/infomain - основная информация о стране
/infoarmy - информация об армии
/infores - информация о ресурсах
/money - показать баланс
/countrys - показать список всех стран в игре
/settax - установить налоговый процент
/build - построить инфраструктуру
/skip - проголосовать за скип фазы
/handover - Предложение продажи / передачи ресурсов
/accept - принять торг / передачу ресурсов
/swiss - положить деньги на счёт в Швейцарском банке
/corrupt - подкупить ЦИК (+3 репутации, -500 в Швейцарском банке)
/spy - отослать шпиона (узнать репутацию правительства, -300 в Швейцарском банке)
/craft - сделать сложные ресурсы
"""

country_names = [
    "Гвидония",
    "Бруния",
    "Павия",
    "Камарак",
    "Лания",
    "Румак",
    "ХЗЧП",
    "ГРПД",
    "Косторма",
    "Сорбия",
    "Итеририум",
    "Светлогория",
    "Нефитрон",
    "Ежиния",
    "Корь",
    "Ромия",
    "Зерния",
    "ШУЭ"]


class Trade(object):

    def __init__(self, sender, from_chat_id, to, to_chat_id, res_id, count, cost):
        self.sender = sender
        self.from_chat_id = from_chat_id
        self.to = to
        self.to_chat_id = to_chat_id
        self.res_id = res_id
        self.count = count
        self.cost = cost

    def accept(self):
        status = self.sender.hand_over(self.to, self.res_id, self.count, self.cost)
        if status:
            self.to.offered_trade = None
            return True
        return False


class Country(object):

    def __init__(self,
                 name: str,
                 area: int,
                 population: int,
                 money: int,
                 income_res: dict,
                 sold_costs: dict,
                 big_res_money: tuple):
        # main
        self.chat_id: int  # done
        self.name: str = name  # done
        self.real_name: str = None
        self.area: int = area  # done (war)
        self.population: int = population  # done (war)
        self.swiss_bank: int = 0  # done
        self.martial_law: bool = False
        self.offered_trade: Trade = None  # done
        # politics
        self.gov_reputation: int = 0  # done
        self.taivan_opinion: tuple = (31, 0)  # opinion and popularity  # LATER
        self.taivan_promoting: tuple = (31, 0)  # opinion and percent per phase  # LATER
        # army
        self.fatigue: int = 0
        self.soldiers: int = self.population // 10
        self.temp_soldiers: int = 0
        self.force_cars: int = 10
        self.tanks: int = 5
        self.planes: int = 1
        self.bomb_planes: int = 0
        self.ships: int = 1
        # economy
        self.money: int = money  # done
        self.tax_perc: int = 5  # done
        self.resources: dict = {**{i : 0 for i in range(11, 20)}, **{i : 0 for i in range(21, 24)}}  # done (war)
        self.income_res: dict = income_res  # done (war)
        self.sold_costs: dict = sold_costs  # done (war? govrep?)
        self.infrastructure: int = (self.area + self.population) // 2 // 10 + 3   # infrastructure count, not costs
        # industry
        self.steel: tuple = (11, big_res_money[0])       # (iron_id, money need)
        self.electronic: tuple = (17, big_res_money[1])  # (copper_id, money need)
        self.glass: tuple = (18, big_res_money[2])       # (quartz_id, money need)
        # achievements stats
        self.crafted: int = 0
        self.wars: int = 0

    def get_info_main(self):
        return f"""
Страна {self.name}
Площадь: {self.area}
Население: {self.population}
Военное положение: {"нет" if not self.martial_law else "ДА"}
Репутация правительства: {self.gov_reputation}
Казна страны: {self.money}
Счёт в Швейарском банке: {self.swiss_bank}
Налог: {self.tax_perc}%
Количество инфраструктуры: {self.infrastructure}
"""

    def get_info_money(self):
        return f"""
Казна страны: {self.money}
Счёт в Швейарском банке: {self.swiss_bank}
"""

    def get_info_army(self):
        return f"""
Военное положение: {"нет" if not self.martial_law else "ДА"}
Военнослужащие: {self.soldiers if self.temp_soldiers == 0 else f'{self.soldiers + self.temp_soldiers} ({self.soldiers} + {self.temp_soldiers})'}
Военные машины: {self.force_cars}
Танки: {self.tanks}
Самолёты: {self.planes}
Бомбардировщики: {self.bomb_planes}
Военные корабли: {self.ships}
"""

    def get_info_res(self):
        tmp1 = "\n".join([f'{get_resname_by_id(key)} : {value}' for key, value in sorted(list(self.resources.items()), key=lambda x: -x[1])])
        tmp2 = "\n".join([f'{get_resname_by_id(key)} : {value}' for key, value in sorted(list(self.income_res.items()), key=lambda x: -x[1])])
        tmp3 = "\n".join([f'{get_resname_by_id(key)} : {value}' for key, value in sorted(list(self.sold_costs.items()), key=lambda x: -x[1])])
        return f"""
Ресурсы на складах:
{tmp1}

Входящие ресурсы (каждая фаза):
{tmp2}

Цены для продажи:
{tmp3}

Возможности производства:
Сталь = железо + {self.steel[1]} монет
Электроника = медь + {self.electronic[1]} монет
Стекло = кварц + {self.glass[1]} монет
"""

    def hand_over(self, other, resource_id, count, cost):
        if not self.resources[resource_id] >= count or not other.money - cost >= 0:
            return False
        self.resources[resource_id] -= count
        self.money += cost
        other.resources[resource_id] += count
        other.money -= cost
        return True

    def craft(self, res_id, res_count):
        if res_id == 21:
            res = self.steel
        elif res_id == 22:
            res = self.electronic
        elif res_id == 23:
            res = self.glass
        else:
            raise Exception("no such res_id")
        if not self.resources[res[0]] - res_count >= 0:
            return False
        if not self.money - res[1] * res_count >= 0:
            return False
        self.resources[res_id] += res_count
        self.resources[res[0]] -= res_count
        self.money -= res[1]
        return True

    def fund_swiss_bank(self, ammount: int):
        if not self.money - ammount >= 0:
            return False
        if ammount < 0:
            return False
        self.money -= ammount
        self.swiss_bank += ammount
        return True

    def corrupt(self):
        if not self.swiss_bank- 500 >= 0:
            return False
        self.swiss_bank -= 500
        self.gov_reputation += 3
        return True

    def set_tax_perc(self, tax: int):
        if tax < 0:
            return False
        if tax > 100:
            return False
        self.tax_perc = tax
        return True

    def build_infr(self, count: int):
        infr_cost = 4
        if not self.money - count * infr_cost >= 0:
            return False
        self.money -= count * infr_cost
        self.infrastructure += count
        return True

    def calculate_war_power(self):
        land = 0
        sea = 0
        danger = 0
        # land power
        land += self.soldiers
        land += int(self.temp_soldiers * 0.5)
        land += self.force_cars * 2
        land += self.tanks * 3
        land += self.planes * 4
        land += self.bomb_planes * 5
        land //= 2**self.fatigue
        # sea power
        sea += self.soldiers
        sea += int(self.temp_soldiers * 0.5)
        sea += int(self.ships * 2.5)
        sea //= 2**self.fatigue
        # war danger
        danger += self.planes
        danger += int(self.tanks * 1.5)
        danger += int(self.bomb_planes * 2.5)
        # return tuple in len if 3
        return land, sea, danger

    def move(self):
        # money
        self.swiss_bank += round(self.swiss_bank * 0.05)
        self.money += round(self.population * self.tax_perc // 35)
        # population and govrep
        self.population += round(self.population * (randrange(80, 120) / 100) / 15) + randrange(0, self.infrastructure)
        self.gov_reputation += 1 if self.area * 1.4 >= self.population else -1
        self.gov_reputation += 5 - self.tax_perc
        if self.tax_perc >= 10:
            self.gov_reputation -= self.tax_perc
        self.money -= round(self.infrastructure)
        if self.infrastructure >= (self.area + self.population) // 2 // 10:
            self.gov_reputation += 1
        else:
            self.gov_reputation -= 3
        # resources
        for id, count in self.income_res.items():
            self.resources[id] += count
        # army
        if self.fatigue:
            self.fatigue -= 1

    def __eq__(self, other):
        return self.name == other.name
