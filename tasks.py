
class Task(object):

    def __init__(self, text: str, check_func, weight: int = 75):
        self.text = text
        self.check_func = check_func
        self.weight = weight

    def check(self, check_object):
        return self.check_func(check_object)


beta_tasks = [
Task("В конце игры разниа между казной и Швейарским банком должна быть не больше 250", lambda x: abs(x.money - x.swiss_bank) <= 250),
Task("Имейте 500 монет на счёте в Швейарском банке", lambda x: x.swiss_bank >= 500),
Task("Имейте 100 инфраструктуры", lambda x: x.infrastructure >= 100),
Task("В конце имейте 10000 денег", lambda x: x.money >= 10000),
Task("Поучавствуйте в 3 войнах", lambda x: x.wars >= 3),
Task("Начните 2 войны", lambda x: x.wars_started >= 2),
Task("Имейте население больше 500", lambda x: x.population > 500),
Task("Совершите 50 крафтов", lambda x: x.crafted >= 50),
Task("Поторгуйтесь 20 раз", lambda x: x.traded >= 20),
Task("Отправтие шпиона минимум два раза", lambda x: x.spys >= 2),
Task("Подкупите ЦИК шесть раз", lambda x: x.corrupted >= 6),
Task("Имейте 20 танков", lambda x: x.tanks >= 20),
Task("Имейте 5 бомбардировщиков", lambda x: x.bomb_planes >= 5),
Task("Добейтесь того, чтобы на вас напала другая страна", lambda x: x.wars > x.wars_started),
Task("Сделайте так, чтобы в конце у вас был непринятый торг", lambda x: x.offered_trade is not None),
Task("Постройте три чуда света", lambda x: len(x.wonders) >= 3),
Task("Оставьте у себя на складах в конце игры не менее 150 ресурсов", lambda x: sum(list(x.resources.values())) > 150),
Task("Оставьте у себя на складах хотя бы по еденице КАЖДОГО ресурса", lambda x: len(list(x.resources.values())) == 9)
]


all_tasks = [
Task("Имейте 500 монет на счёте в Швейарском банке", lambda x: x.swiss_bank >= 500),
Task("Имейте 75 инфраструктуры", lambda x: x.infrastructure >= 74),


]

unique_tasks = [
Task("В конце игры разниа между казной и Швейарским банком должна быть не больше 250", lambda x: abs(x.money - x.swiss_bank) <= 250),

]
