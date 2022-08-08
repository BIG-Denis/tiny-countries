
class Task(object):

    def __init__(self, text: str, check, weight: int = 100):
        self.text = text
        self.check = check
        self.weight = weight

    def check(self, check_object):
        return check(check_object)


all_tasks = [
Task("Имейте 500 монет на счёте в Швейарском банке", lambda x: x.swiss_bank >= 500),
Task("Имейте 75 инфраструктуры", lambda x: x.infrastructure >= 74),
Task("Имейте 100 инфраструктуры", lambda x: x.infrastructure >= 100),

]

unique_tasks = [
Task("В конце игры разниа между казной и Швейарским банком должна быть не больше 50", lambda x: abs(x.money - x.swiss_bank) <= 50),

]
