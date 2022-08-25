
class Wonder(object):

    def __init__(self, name: str, cost_money: int, cost_res: dict):
        self.name = name
        self.cost_money = cost_money
        self.cost_res = cost_res
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False


all_wonders = [
    Wonder("Эйфелева башня", 2500, {11 : 25, 21: 35}),
    Wonder("Лувр", 2000, {21: 15, 23: 50}),
    Wonder("Мировой склад", 6000, {12: 50}),
    Wonder("Золотой пенис", 6000, {13: 50}),
    Wonder("Колосс Родосский", 1500, {21: 20, 15: 50}),
    Wonder("Енисейский дворец", 5000, {16: 50}),
    Wonder("Всемирный аэропорт", 2500, {11: 25, 23: 35}),
    Wonder("Нефтяные консервы", 2500, {12: 25, 14: 25}),
    Wonder("Сплав будущего", 1000, {11: 20, 15: 20, 21: 20})
]
