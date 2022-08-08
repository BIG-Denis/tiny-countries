
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


help_text = """
/help - показать список команд
/infomain - основная информация о стране
/infoarmy - информация об армии
/infores - информация о ресурсах
/money - показать баланс
/settax <число> - установить налоговый процент
/build <кол-во> - построить инфраструктуру
/skip - проголосовать за скип фазы
/handover <страна> <ресурс> <количество> <цена> - Предложение продажи / передачи ресурсов
/accept - принять торг / передачу ресурсов
/swiss <сумма> - положить деньги на счёт в Швейцарском банке
/corrupt - подкупить ЦИК (+3 репутации, -500 в Швейцарском банке)
"""

country_names = [
    "Гвидония",
    "Бруния",
    "Павия",
    "Камарак",
    "Лания",
    "Румак",
    "Нидерланды",
    "Россия",
    "ХЗЧП",
    "ГРПД",
    "Кострома",
    "Сорбия",
    "Итеририум",
    "Светлогория",
    "Нефитрон"]


class Trade(object):

    def __init__(self, sender, from_chat_id, to, to_chat_id, res_id, count, cost):
        self.sender = sender
        self.from_chat_id = from_chat_id
        self.to = to
        self.to_chat_id = to_chat_id
        self.res_id = res_id
        self.count = count
        self.cost = cost

    def accept():
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
                 resources: dict,
                 income_res: dict,
                 sold_costs: dict,
                 big_res_money: tuple):
        # main
        self.chat_id: int  # done
        self.name: str = name  # done
        self.area: int = area  # done (war)
        self.population: int = population  # done
        self.swiss_bank: int = 0  # done
        self.martial_law: bool = False
        self.offered_trade: Trade = None  # done
        # politics
        self.gov_reputation: int = 0  # done
        self.taivan_opinion: tuple = (31, 0)  # opinion and popularity  # LATER
        self.taivan_promoting: tuple = (31, 0)  # opinion and percent per phase  # LATER
        # army
        self.soldiers: int = self.population // 10
        self.temp_soldiers: int = 0
        self.force_cars: int = 10
        self.tanks: int = 5
        self.small_planes: int = 3
        self.big_planes: int = 0
        self.bomb_planes: int = 0
        self.small_ships: int = 1
        self.big_ships: int = 0
        # economy
        self.money: int = money  # done
        self.tax_perc: int = 5  # done
        self.resources: dict = resources  # done (war)
        self.income_res: dict = income_res  # done (war)
        self.sold_costs: dict = sold_costs  # done (war? govrep?)
        self.infrastructure: int = (self.area + self.population) // 2 // 10 + 3   # infrastructure count, not costs
        # industry
        self.steel: tuple = (0, 11, big_res_money[0])       # (count per phase, iron_id, money need)
        self.electronic: tuple = (0, 17, big_res_money[1])  # (count per phase, copper_id, money need)
        self.glass: tuple = (0, 18, big_res_money[2])       # (count per phase, quartz_id, money need)

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
Малые самолёты: {self.small_planes}
Большие самолёты: {self.big_planes}
Бомбардировщики: {self.bomb_planes}
Малые военные корабли: {self.small_ships}
Большие военные корабли: {self.big_ships}
"""

    def get_info_res(self):
        tmp1 = "\n".join([f'{get_resname_by_id(key)} : {value}' for key, value in self.resources.items()])
        tmp2 = "\n".join([f'{get_resname_by_id(key)} : {value}' for key, value in self.income_res.items()])
        tmp3 = "\n".join([f'{get_resname_by_id(key)} : {value}' for key, value in self.sold_costs.items()])
        return f"""
Ресурсы на складах:
{tmp1}

Входящие ресурсы (каждая фаза):
{tmp2}

Цены для продажи:
{tmp3}
"""

    def hand_over(self, other, resource_id, count, cost):
        if not cost >= 0:
            return False
        if not self.resources[resource_id] >= count or not other.money - cost >= 0:
            return False
        self.resources[resource_id] -= count
        self.money += cost
        other.resources[resource_id] += count
        other.money -= cost
        return True

    def craft(self, resource_id, count):
        if resource_id == 21:
            res = (11, self.steel)
        elif resource_id == 22:
            res = (17, self.electronic)
        elif resource_id == 23:
            res = (18, self.glass)
        else:
            raise Exception("resourse_id exception")
        if not self.resources[res[1][1]] >= count or not self.money >= res[1][2]:
            return False
        self.resources[res[1][1]] -= count
        self.resources[res[0]] += count
        return True

    def fund_swiss_bank(self, ammount: int):
        if not self.money - ammount >= 0:
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
        if tax >= 0:
            self.tax_perc = tax
            return True
        else:
            return False

    def build_infr(self, count: int):
        infr_cost = 4
        if not self.money - count * infr_cost >= 0:
            return False
        self.money -= count * infr_cost
        self.infrastructure += count
        return True

    def phase_move(self):
        self.swiss_bank += round(self.swiss_bank * 0.05)
        self.money += round(self.population * self.tax_perc // 35)
        self.population += round(self.population * (randrange(80, 120) / 100) / 15) + randrange(0, self.infrastructure)
        self.gov_reputation += 1 if self.area * 1.4 >= self.population else -1
        self.gov_reputation += 5 - self.tax_perc
        if self.tax_perc >= 10:
            self.gov_reputation -= tax_perc
        self.money -= round(self.infrastructure)
        if self.infrastructure >= (self.area + self.population) // 2 // 10:
            self.gov_reputation += 1
        else:
            self.gov_reputation -= 2

    def __eq__(self, other):
        return self.name == other.name
