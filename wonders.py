
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
    Wonder("Эйфелева башня", 5000, {11 : 25, 21: 35}),
    Wonder("Лувр", 4000, {21: 15, 23: 50}),
    Wonder("Мировой склад", 10000, {12: 50}),
    Wonder("Золотой пенис", 10000, {13: 50}),
    Wonder("Колосс Родосский", 3500, {21: 20, 15: 50}),
    Wonder("Енисейский дворец", 10000, {16: 50}),
    Wonder("Всемирный аэропорт", 5000, {11: 25, 23: 35}),
    Wonder("Нефтяные консервы", 5000, {12: 25, 14: 25}),
    Wonder("Сплав будущего", 3500, {11: 20, 15: 20, 21: 20})
]
