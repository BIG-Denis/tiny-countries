
from tasks import *
from functions import *
from random import randrange, choices


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

WAR TECHNICS:
    51 soldiers    | 1 peaple + 5 money OR 1 man + 1 glass
    52 force cars  | 40 money OR 10 money + 2 steel OR 3 steel + electronic
    53 tanks       | 65 money OR 30 money + 3 steel OR 5 steel + 2 electronic
    54 planes      | 85 money OR 40 money + 5 steel OR 7 steel + 3 electronic
    55 bomb planes | 110 money OR 50 money + 6 steel OR 8 steel + 4 electronic
    56 ships       | TEMPORARILY NOT IN USE

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
/buy - купить военных и военную технику
/swiss - положить деньги на счёт в Швейцарском банке
/corrupt - подкупить ЦИК (+3 репутации, -500 в Швейцарском банке)
/spy - отослать шпиона (узнать репутацию правительства, -300 в Швейцарском банке)
/craft - сделать сложные ресурсы
/war - начать войну с другой страной
/tasks - просмотреть цели на игру
"""
# /hide - разворовать страну и залечь на дно

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


war_buys = {
    51: "1: 1 человек + 5 монет\n2: 1 человек + 1 стекло",
    52: "1: 40 монет\n2: 10 монет + 2 стали\n3: 3 стали + 1 электроника",
    53: "1: 65 монет\n2: 30 монет + 3 стали\n3: 5 стали + 2 электроники",
    54: "1: 85 монет\n2: 40 монет + 5 стали\n3: 7 стали + 3 электроники",
    55: "1: 110 монет\n2: 50 монет + 6 стали\n3: 8 стали + 4 электроники"
}


class War(object):

    def __init__(self, atacking, defensive):
        self.attacking = atacking
        self.defensive = defensive
        self.army_ratio = self.attacking.war_power()[0] / self.defensive.war_power()[0]
        self.attacking.wars += 1
        self.defensive.wars += 1
        self.attacking.wars_started += 1
    
    def war_aftermath(self, country, minp, maxp):  # need to add temp soldiers
        if country.martial_law:
            temp_died = round(randrange(75, 85) / 100)
            country.population -= temp_died
            country.temp_soldiers -= temp_died
        country.soldiers = max(0, round(country.soldiers - country.soldiers * (randrange(minp, maxp)) / 100))
        country.force_cars = max(0, round(country.soldiers - country.soldiers * (randrange(minp, maxp)) / 100))
        country.tanks = max(0, round(country.soldiers - country.soldiers * (randrange(minp, maxp)) / 100))
        country.planes = max(0, round(country.soldiers - country.soldiers * (randrange(minp, maxp)) / 100))
        country.bomb_planes = max(0, round(country.soldiers - country.soldiers * (randrange(minp, maxp)) / 100))
    
    def check_full_def(self):
        if self.attacking.war_power()[0] >= self.defensive.war_power()[0]:
            return choices((True, False), weights=(self.attacking.war_power()[0]**3, self.defensive.war_power()[0]**3), k=1)[0]
        else:
            return choices((True, False), weights=(self.attacking.war_power()[0]**5, self.defensive.war_power()[0]**5), k=1)[0]

    def attack(self):  # add taivan opinion change
        if self.check_full_def():
            self.war_aftermath(self.attacking, 10, 15)
            self.war_aftermath(self.defensive, int(5 * self.army_ratio), int(20 * self.army_ratio))
            self.attacking.gov_reputatuin = max(self.attacking.gov_reputation - 5, -5)
            self.defensive.gov_reputation += 5
            self.attacking.fatigue += 2
            self.defensive.fatigue += 1
            return (False, False, False)  # war take place, full conquere, lucky war
        lucky_war = randrange(0, 100+1) > war_lucky_chances(self.army_ratio) * 100
        lucky_k = 1 + lucky_war * war_normalize(self.army_ratio)  # float 1 - 1.3  # used to calculate poteri
        conquest_k = war_conquest(self.army_ratio * lucky_k)  # float 0 - 0.5  # used to calculate zaxvat
        print(f"lucky war : {True}, lucky_k = {lucky_k}, conquest_k = {conquest_k}")
        self.war_aftermath(self.attacking, round(15 / lucky_k), round(50 / lucky_k))
        self.war_aftermath(self.defensive, round(10 * lucky_k), round(35 * lucky_k))
        if self.defensive.area < 100 and lucky_war or self.defensive.area < 75:
            full = True
        self.defensive.population *= round(1 / lucky_k)
        self.defensive.infrastructure *= round(1 / lucky_k + 4)
        self.defensive.infrastructure = max(0, self.defensive.infrastructure)
        if not full:
            area = round(self.defensive.area * conquest_k)
            self.defensive.area -= area
            self.attacking.area += area
            population = round(self.defensive.population * conquest_k)
            self.defensive.population -= population
            self.attacking.population += population
            infrastructure = round(self.defensive.infrastructure * conquest_k)
            self.defensive.infrastructure -= infrastructure
            self.attacking.infrastructure += infrastructure
            for res_id in (list(range(11, 20)) + list(range(21, 24))):
                count = round(self.defensive.resources[res_id] * conquest_k)
                self.defensive.resources[res_id] -= count
                self.attacking.resources[res_id] += count
            for res_id in range(11, 20):
                count = round(self.defensive.income_res[res_id] * conquest_k)
                self.defensive.income_res[res_id] -= count
                self.attacking.income_res[res_id] += count
        else:
            self.attacking.area += self.defensive.area
            self.attacking.population += self.defensive.population
            for res_id in (list(range(11, 20)) + list(range(21, 24))):
                self.attacking.resources[res_id] += self.defensive.resources[res_id]
            for res_id in range(11, 20):
                self.attacking.income_res[res_id] += self.defensive.income_res[res_id]
            self.attacking.fatigue += 1
        if self.defensive.gov_reputation < 0:
                self.attacking.gov_reputatuin += round(- self.defensive.gov_reputation / 1.55)
        else:
            self.attacking.gov_reputation -= round(self.defensive.gov_reputation * 1.5 + 1)
        self.defensive.gov_reputauin = max(-5, self.defensive.gov_reputation - 5)
        return (True, full, lucky_war) # war take place, full conquere, lucky war


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
            self.sender.traded += 1
            self.to.traded += 1
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
        self.area: int = area  # done
        self.population: int = population  # done
        self.swiss_bank: int = 0  # done
        self.martial_law: bool = False
        self.offered_trade: Trade = None  # done
        shuffle(beta_tasks)
        self.tasks = beta_tasks[:3]
        # politics
        self.gov_reputation: int = 0  # done
        self.taivan_opinion: tuple = (31, 0)  # opinion and popularity  # LATER
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
        self.resources: dict = {**{i : 0 for i in range(11, 20)}, **{i : 0 for i in range(21, 24)}}  # done
        self.income_res: dict = income_res  # done
        self.sold_costs: dict = sold_costs  # done
        self.infrastructure: int = (self.area + self.population) // 2 // 10 + 3   # done
        # industry
        self.steel: tuple = (11, big_res_money[0])       # (iron_id, money need)
        self.electronic: tuple = (17, big_res_money[1])  # (copper_id, money need)
        self.glass: tuple = (18, big_res_money[2])       # (quartz_id, money need)
        # achievements stats
        self.crafted = 0
        self.wars = 0
        self.wars_started = 0
        self.traded = 0
        self.corrupted = 0
        self.spys = 0


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
        self.crafted += res_count
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
        self.corrupted += 1
        return True

    def set_tax_perc(self, tax: int):
        if tax < 0:
            return False
        if tax > 100:
            return False
        self.tax_perc = tax
        return True

    def build_infr(self, count: int):
        infr_cost = 15
        if not self.money - count * infr_cost >= 0:
            return False
        self.money -= count * infr_cost
        self.infrastructure += count
        return True

    def war_power(self):
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
        land //= 1.5**self.fatigue
        if self.martial_law:
            land = round(land * 1.2)
        # sea power
        sea += self.soldiers
        sea += int(self.temp_soldiers * 0.5)
        sea += int(self.ships * 2.5)
        sea //= 1.5**self.fatigue
        if self.martial_law:
            sea = round(sea * 1.3)
        # war danger
        danger += self.planes
        danger += int(self.tanks * 1.5)
        danger += int(self.bomb_planes * 2.5)
        if self.martial_law:
            danger = round(danger * 1.35)
        # return tuple in len if 3
        return land, sea, danger
    
    def add(self, bid, cnt):
        if bid == 51:
            self.soldiers += cnt
        if bid == 52:
            self.force_cars += cnt
        if bid == 53:
            self.tanks += cnt
        if bid == 54:
            self.planes += cnt
        if bid == 55:
            self.bomb_planes += cnt
    
    def buy(self, bid, opt, cnt):
        if bid == 51:  # soldiers
            if opt == 1:
                if self.money - 5 * cnt < 0 or self.population - cnt < 0:
                    return False
                else:
                    self.money -= 5 * cnt
                    self.population -= cnt
                    self.soldiers += cnt
            if opt == 2:
                if self.resources[23] - cnt < 0 or self.population - cnt < 0:
                    return False
                else:
                    self.resources[23] -= cnt
                    self.population -= cnt
                    self.soldiers += cnt
            return True
        elif bid in list(range(52, 56)):
            if opt == 1:
                moneys = {52: 40, 53: 65, 54: 85, 55: 110}
                if self.money - moneys[bid] * cnt < 0:
                    return False
                self.money -= moneys[bid] * cnt
                self.add(bid, cnt)
                return True
            if opt == 2:
                moneys = {52: 10, 53: 30, 54: 40, 55: 50}
                steels = {52: 2, 53: 3, 54: 5, 55: 6}
                if self.money - moneys[bid] * cnt < 0 or self.resources[21] - steels[bid] * cnt < 0:
                    return False
                self.money -= moneys[bid] * cnt
                self.resources[21] -= steels[bid] * cnt
                self.add(bid, cnt)
                return True
            if opt == 3:
                steels = {52: 3, 53: 5, 54: 7, 55: 8}
                electronics = {52: 1, 53: 2, 54: 3, 55: 4}
                if self.resources[21] - steels[bid] * cnt < 0 or self.resources[22] - steels[bid] * cnt < 0:
                    return False
                self.resources[21] -= steels[bid] * cnt
                self.resources[22] -= electronics[bid] * cnt
                self.add(bid, cnt)
                return True


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
    
    def calculate_final_points(self):
        ret = 0
        ret += max(25, self.area / 8)
        ret += max(20, self.population / 12)
        ret += max(15, self.money / 15)
        ret += max(25, self.swiss_bank / 8)
        ret -= 30 * self.martial_law
        ret += max(55, self.gov_reputation * 7.5)
        ret += max(60, sum([self.war_power()[i] for i in range(2)]) / 85)
        ret += max(35, sum(list(self.resources.values())) / 25)
        ret += max(50, self.infrastructure / 1.5)
        ret += sum([task.weight for task in self.tasks if task.check_func(self)])
        return round(ret)

    def __eq__(self, other):
        return self.name == other.name
