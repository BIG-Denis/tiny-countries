
import re
import dill
import json
import pickle
import telebot

from preset import *
from patterns import *
from random import randrange, shuffle


def main():

    move = 1
    skips = set()
    players: dict[int, Country] = {}
    taivan_phase = False
    free_wonders = set()

    with open("token.json", 'r') as file:
        json_file = json.load(file)
        token = json_file["token"]

    bot = telebot.TeleBot(token, parse_mode=False)

    # if len(players.items()) == 3 if not TESTING else TESTING_PLAYERS:
    countrys = []
    names = country_names.copy()
    shuffle(names)
    names = names[:3]
    areas = [randrange(100, 400) for _ in range(3)]
    populations = [randrange(150, 500) for _ in range(3)]
    moneys = [randrange(100, 250) for _ in range(3)]
    income_ress, sold_costss = gen_income_ress(minr=8, maxr=14, mins=5, maxs=14, big_field_k=7, big_sell_k=6, hard_res_k=1.75)
    big_res_moneys = [[randrange(5, 13) for _ in range(3)] for _ in range(3)]
    for i in range(3):
        countrys.append(Country(names[i], areas[i], populations[i], moneys[i], income_ress[i], sold_costss[i], big_res_moneys[i]))
    shuffle(countrys)
    for _ in range(2):
        tmp = choices(all_wonders, k=1)[0]
        free_wonders.add(tmp)
        all_wonders.remove(tmp)


    def get_country_by_name(name: str):
        for country in players.values():
            if country.name == name:
                return country
        return None
    

    @bot.message_handler(commands=['start', 'joingame'])
    def joingame(message):
        nonlocal countrys
        if players.get(message.chat.id) is None:
            players[message.chat.id] = 1
            bot.send_message(message.chat.id, "Вы зарестрированы на игру.")
        else:
            bot.send_message(message.chat.id, "Вы уже зарестрированы на игру!")
            return
        if len(players) == 3 if not TESTING else 1:
            for i, key in enumerate(players.keys()):
                players[key] = countrys[i]
                players[key].give_start_res()
            for key in players.keys():
                bot.send_message(key, "Игра началась!")


    @bot.message_handler(commands=['help', 'h'])
    def help_msg(message):
        # players[message.chat.id].chat_id = message.chat.id
        # msg = help_text if players.get(message.chat.id) is not None else "Давайте сначала дождёмся начала игры."
        msg = help_text
        bot.send_message(message.chat.id, msg)


    @bot.message_handler(commands=['infomain', 'info'])
    def info_msg(message):
        players[message.chat.id].chat_id = message.chat.id
        bot.send_message(message.chat.id, players[message.chat.id].get_info_main())


    @bot.message_handler(commands=['infoarmy', 'army'])
    def info_msg(message):
        bot.send_message(message.chat.id, players[message.chat.id].get_info_army())


    @bot.message_handler(commands=['infores', 'res'])
    def info_msg(message):
        players[message.chat.id].chat_id = message.chat.id
        bot.send_message(message.chat.id, players[message.chat.id].get_info_res())


    @bot.message_handler(commands=['money', 'balance'])
    def info_msg(message):
        bot.send_message(message.chat.id, players[message.chat.id].get_info_money())
    
    
    @bot.message_handler(commands=['countrys'])
    def countrys_msg(message):
        bot.send_message(message.chat.id, 'Все страны в игре:\n' + "\n".join([val.name for val in players.values()]))


    @bot.message_handler(commands=['skip', 'next'])
    def skip_msg(message):
        skips.add(message.chat.id)
        if len(skips) < len(players):
            bot.send_message(message.chat.id, f"Ваш голос учтён! За скип голосует уже {len(skips)} / {len(players)} игроков.")
        else:
            next_move()


    @bot.message_handler(commands=['handover'])
    def handover_1(message):
        bot.send_message(message.chat.id, "Введите название страны...")
        bot.register_next_step_handler(message, handover_2)

    def handover_2(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        name = message.text
        for country in players.values():
            if country.name.lower() == name.lower():
                bot.send_message(message.chat.id, "Введите название ресурса...")
                bot.register_next_step_handler(message, handover_3, country)
                return
        else:
            bot.send_message(message.chat.id, "Кажется, такой страны нет\nВведите название страны ещё раз...")
            bot.register_next_step_handler(message, handover_2)
            return

    def handover_3(message, country):
        if message.text.lower() in ("отмена", "cancel"):
            return
        res_id = resources_dict.get(message.text.lower())
        if res_id is not None:
            bot.send_message(message.chat.id, f"Введите количество ресурса...\n(Всего у вас: {players[message.chat.id].resources[res_id]})")
            bot.register_next_step_handler(message, handover_4, country, res_id)
            return
        else:
            bot.send_message(message.chat.id, "Кажется, нет такого ресурса\nВведите его название ещё раз...")
            bot.register_next_step_handler(message, handover_3, country)
            return

    def handover_4(message, country, res_id):
        if message.text.lower() in ("отмена", "cancel"):
            return
        try:
            res_count = eval(message.text)
            if not players[message.chat.id].resources[res_id] >= res_count:
                bot.send_message(message.chat.id, "Недостаточно ресурса! Введите число поменьше...")
                bot.register_next_step_handler(message, handover_4, country, res_id)
                return
            elif not res_count > 0:
                bot.send_message(message.chat.id, "Положительные числа only! Мразь!")
                bot.register_next_step_handler(message, handover_4, country, res_id)
                return
            else:
                bot.send_message(message.chat.id, "Назначьте цену за сделку (для передачи введите 0)...")
                bot.register_next_step_handler(message, handover_5, country, res_id, res_count)
                return
        except:
            bot.send_message(message.chat.id, "Некорректный ввод, попробуйте ещё раз...")
            bot.register_next_step_handler(message, handover_4, country, res_id)
            return

    def handover_5(message, country, res_id, res_count):
        if message.text.lower() in ("отмена", "cancel"):
            return
        try:
            price = eval(message.text)
            if price < 0:
                bot.send_message(message.chat.id, "Положительные числа only!")
                bot.register_next_step_handler(message, handover_5, country, res_id, res_count)
                return
            else:
                msg = "Передача успешна!" if price == 0 else "Ваш запрос успешно отправлен!"
                bot.send_message(message.chat.id, msg)
                if price > 0:
                    bot.send_message(country.chat_id,
                    f"Страна {players[message.chat.id].name} предложила вам купить {get_resname_by_id(res_id)} в количестве {res_count} по цене {price}\nПринять /accept")
                country.offered_trade = Trade(players[message.chat.id], message.chat.id, country, country.chat_id, res_id, res_count, price)
                if price == 0:
                    country.offered_trade.accept()
                    bot.send_message(country.chat_id,
                        f"Страна {players[message.chat.id].name} передала вам {get_resname_by_id(res_id)} в количестве {res_count} штук\nТеперь этого ресурса у вас: {country.resources[res_id]}")
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, "Некорректный ввод, попробуйте ещё раз...")
            bot.register_next_step_handler(message, handover_5, country, res_id, res_count)
            return
    

    @bot.message_handler(commands=['sell'])
    def sell_1(message):
        bot.send_message(message.chat.id, "Введите название ресурса для продажи...")
        bot.register_next_step_handler(message, sell_2)
    
    def sell_2(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        if resources_dict.get(message.text.lower()) is not None:
            res_id = resources_dict[message.text.lower()]
            bot.send_message(message.chat.id,
                f"Введите количество ресурса для продажи...\n(0 чтобы продать весь, всего {players[message.chat.id].resources[res_id]})")
            bot.register_next_step_handler(message, sell_3, res_id)
        else:
            bot.send_message(message.chat.id, "Не удачно! Попробуйте снова...")
            bot.register_next_step_handler(message, sell_2)
    
    def sell_3(message, res_id):
        if message.text.lower() in ("отмена", "cancel"):
            return
        try:
            cnt = eval(message.text)
            tmp = players[message.chat.id].money
            if cnt < 0:
                raise Exception()
            status = players[message.chat.id].sell(res_id, cnt)
            msg = f"Успешно!\nОстататки {get_resname_by_id(res_id)} на складах: {players[message.chat.id].resources[res_id]}.\nВыручка: {players[message.chat.id].money - tmp}\nБаланс: {players[message.chat.id].money}" if status else "Не успешно!"
            bot.send_message(message.chat.id, msg)
        except Exception as e:
            bot.send_message(message.chat.id, "Попробуй снова...")
            bot.register_next_step_handler(message, sell_3, res_id)
    

    @bot.message_handler(commands=['sellall'])
    def sellall_1(message):
        bot.send_message(message.chat.id, "Вы ТОЧНО хотите продать весь свой склад?\nЕсли вы уверены напишите <точно>.")
        bot.register_next_step_handler(message, sellall_2)
    
    def sellall_2(message):
        if message.text.lower() != "точно":
            bot.send_message(message.chat.id, "Продажа всех запасов отменена.")
            return
        tmp = players[message.chat.id].money
        for sid in list(range(11, 16+1)) + list(range(21, 23+1)):
            players[message.chat.id].sell(sid, 0)
        bot.send_message(message.chat.id, f"Вы успешно заработали {players[message.chat.id].money - tmp} денег!\nБаланс: {players[message.chat.id].money}")


    @bot.message_handler(commands=['accept'])
    def accept_trade(message):
        if players[message.chat.id].offered_trade is not None:
            from_chat_id = players[message.chat.id].offered_trade.from_chat_id
            res_id = players[message.chat.id].offered_trade.res_id
            to = players[message.chat.id].offered_trade.to
            status = players[message.chat.id].offered_trade.accept()
            if status:
                bot.send_message(message.chat.id, f"Предложение принято успешно!\nТеперь у вас {to.resources[res_id]}")
                bot.send_message(from_chat_id, f"Ваше предложение продажи ресурса {players[message.chat.id].name} принято!\nВаш баланс: {players[from_chat_id].money}")
            else:
                bot.send_message(message.chat.id, "Не удалось принять предложение продажи! Скорее всего вам не хватает денег.")
        else:
            bot.send_message(message.chat.id, "У вас нет актуальных предложений продажи!")


    @bot.message_handler(commands=['sweden'])
    def swiss(message):
        bot.send_message(message.chat.id, "Введите желаемую сумму...")
        bot.register_next_step_handler(message, swiss_final)

    def swiss_final(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        try:
            ammount = eval(message.text)
            status = players[message.chat.id].fund_swiss_bank(ammount)
            if status:
                bot.send_message(message.chat.id, players[message.chat.id].get_info_money())
            else:
                raise Exception()
        except:
            bot.send_message(message.chat.id, "Не удалось положить деньги!")


    @bot.message_handler(commands=['corrupt'])
    def corrupt(message):
        status = players[message.chat.id].corrupt()
        msg = f"Успешно!\nСчёт на Швецком банке: {players[message.chat.id].swiss_bank}" if status else "Не успешно!"
        bot.send_message(message.chat.id, msg)


    @bot.message_handler(commands=['spy'])
    def spy(message):
        bot.send_message(message.chat.id, "Введите название страны...")
        bot.register_next_step_handler(message, spy_final)

    def spy_final(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        arg = message.text
        if not players[message.chat.id].swiss_bank - spy_cost >= 0:
            bot.send_message(message.chat.id, "Не хватает денег на счету Швецкого банка!")
            return
        for country in players.values():
            if country.name.lower() == arg.lower():
                players[message.chat.id].spys += 1
                bot.send_message(message.chat.id,
                    f"Репутация правительства в Стране {country.name}: {country.gov_reputation}\nСчёт в Швецком Банке: {players[message.chat.id].swiss_bank}")
                players[message.chat.id].swiss_bank -= spy_cost
                if randrange(0, 100+1) <= 40:
                    bot.send_message(country.chat_id, f"В вашей стране был обнаружен Шпион из страны {players[message.chat.id].name}")
                break
        else:
            bot.send_message(message.chat.id, "Такой страны не нашлось!")


    @bot.message_handler(commands=['settax'])
    def set_tax(message):
        bot.send_message(message.chat.id, "Введите желаемый процент налога...")
        bot.register_next_step_handler(message, set_tax_final)

    def set_tax_final(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        try:
            tax = eval(message.text)
            status = players[message.chat.id].set_tax_perc(tax)
            msg = "Успешно!" if status else "Нет, такой налог мы не поставим."
            bot.send_message(message.chat.id, msg)
        except:
            bot.send_message(message.chat.id, "Не удалось установить налог!")


    @bot.message_handler(commands=['build'])
    def build(message):
        bot.send_message(message.chat.id, "Введите количество новой инфраструктуры для постройки...")
        bot.register_next_step_handler(message, build_final)

    def build_final(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        try:
            arg = eval(message.text)
            status = players[message.chat.id].build_infr(arg)
            msg = "Успешно!" if status else "Не успешно!"
            bot.send_message(message.chat.id, msg)
        except:
            bot.send_message(message.chat.id, "Не удалось!")


    @bot.message_handler(commands=['craft'])
    def craft_1(message):
        bot.send_message(message.chat.id, "Какой ресурс вы хотите сделать?\n(Сталь, электроника, стекло)")
        bot.register_next_step_handler(message, craft_2)

    def craft_2(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        arg = message.text.lower()
        res_id = resources_dict.get(arg)
        if res_id is not None and res_id in list(range(20, 24)):
            bot.send_message(message.chat.id, "Сколько ресурса вы хотите скрафтить?")
            bot.register_next_step_handler(message, craft_3, res_id)
        else:
            bot.send_message(message.chat.id, "Некорректный ввод! Попробуйте ещё раз...")
            bot.register_next_step_handler(message, craft_2)

    def craft_3(message, res_id):
        if message.text.lower() in ("отмена", "cancel"):
            return
        try:
            res_count = eval(message.text)
        except:
            bot.send_message(message.chat.id, "Некорректный ввод! Попробуй ещё раз...")
            bot.register_next_step_handler(message, craft_3, res_id)
            return
        status = players[message.chat.id].craft(res_id, res_count)
        if status:
            if res_id == 21:
                tmp = 11
            elif res_id == 22:
                tmp = 15
            elif res_id == 23:
                tmp = 16
            else:
                raise Exception("craft_3 function res_id exception")
            bot.send_message(message.chat.id, f"""
Успешно!
Баланс: {players[message.chat.id].money}
Теперь {get_resname_by_id(res_id)} на складе: {players[message.chat.id].resources[res_id]}
Остатки {get_resname_by_id(tmp)} на складе: {players[message.chat.id].resources[tmp]}
""")
# f"Успешно!\nТеперь у вас {get_resname_by_id(res_id)} в количестве {players[message.chat.id].resources[res_id]}\nБаланс: {players[message.chat.id].money}")
        else:
            bot.send_message(message.chat.id, "Не получилось сделать ресурсы!")
    

    @bot.message_handler(commands=['war'])
    def war_1(message):
        bot.send_message(message.chat.id, "Введите название страны на которую хотите напасть")
        bot.register_next_step_handler(message, war_2)
    
    def war_2(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        country = get_country_by_name(message.text)
        if country is None:
            bot.send_message(message.chat.id, "Нет такой страны, попробуйте ещё раз...")
            bot.register_next_step_handler(message, war_2)
            return
        if country == players[message.chat.id]:
            bot.send_message(message.chat.id, "Нет, на самого себя напасть нельзя!")
            return
        war = War(players[message.chat.id], country)
        status = war.attack()
        if status[0] is False:
            bot.send_message(country.chat_id, f"Ваша страна успешно отразила нападение {players[message.chat.id].name}!")
            bot.send_message(message.chat.id, f"Страна {country.name} полностью отразила ваше нападение!")
        else:
            if status[1] is True:
                bot.send_message(country.chat_id, f"Страна {players[message.chat.id].name} полность завоевала вас, вы выбываете из игры!")
                bot.send_message(message.chat.id, f"Страна {country.name} была полность завоёвана!")
                del players[country]
            else:
                bot.send_message(country.chat_id,
                f"Страна {players[message.chat.id].name} напала на вас и причинила серьёзный урон, аннексировав часть территорий!")
                bot.send_message(message.chat.id,
                f"Вы аннексировали часть территорий страны {country.name} и получили другие плюшки в результате войны!")
    

    @bot.message_handler(commands=['tasks'])
    def tasks_msg(message):
        bot.send_message(message.chat.id,
            "\n\n".join([f"{task.text} [{'ГОТОВО' if task.check_func(players[message.chat.id]) else 'не готово'}]" for task in players[message.chat.id].tasks]))
    

    @bot.message_handler(commands=['buy'])
    def buy_1(message):
        bot.send_message(message.chat.id, 
        "Введите id покупаемого объекта..\n51 - солдаты\n52 - БТРы\n53 - танки\n54 - самолёты\n55 - бомбардировщики")
        bot.register_next_step_handler(message, buy_2)
    
    def buy_2(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        if message.text in list(map(str, list(range(51, 56)))):
            bid = eval(message.text)
            bot.send_message(message.chat.id, f"Выберите опцию покупки...\n{war_buys[bid]}")
            bot.register_next_step_handler(message, buy_3, bid)
        else:
            bot.send_message(message.chat.id, "Некорректный id, попробуйте снова...")
            bot.register_next_step_handler(message, buy_2)
    
    def buy_3(message, bid):
        if message.text.lower() in ("отмена", "cancel"):
            return
        if message.text in list(map(str, list(range(1, 4)))):
            opt = eval(message.text)
            bot.send_message(message.chat.id, "Введите количество...")
            bot.register_next_step_handler(message, buy_4, bid, opt)
        else:
            bot.send_message(message.chat.id, "Некорректный ввод, попробуйте снова...")
            bot.register_next_step_handler(message, buy_3, bid)
    
    def buy_4(message, bid, opt):
        if message.text.lower() in ("отмена", "cancel"):
            return
        try:
            cnt = eval(message.text)
            status = players[message.chat.id].buy(bid, opt, cnt)
            msg = f"Успешно!\nБаланс: {players[message.chat.id].money}" if status else "Не успешно!"
            bot.send_message(message.chat.id, msg)
        except Exception as e:
            print(f"При покупке войны произошла ошибка {e}\n(функция buy_4)")
            bot.send_message(message.chat.id, "Некорректный ввод, попробуйте снова...")
            bot.register_next_step_handler(message, buy_4, bid, opt)
    

    @bot.message_handler(commands=['wonders'])
    def wonders(message):
        res = ""
        for elem in free_wonders:
            res += elem.name + '\n'
            res += f"Стоимость: {elem.cost_money}" + '\n'
            res += "Необходимые ресурсы: " + ', '.join([f"{get_resname_by_id(k)}: {v}" for k, v in elem.cost_res.items()]) + '\n' * 2
        if len(players[message.chat.id].wonders) > 0:
            res += "\nВаши построенные чудеса света:\n\n"
            res += '\n'.join(elem.name for elem in players[message.chat.id].wonders)
        bot.send_message(message.chat.id, f"Доступные чудеса:\n\n{res}")
    
    
    @bot.message_handler(commands=['make'])
    def make_wonder_1(message):
        bot.send_message(message.chat.id, "Введите название желаемого чуда света...")
        bot.register_next_step_handler(message, make_wonder_2)
    
    def make_wonder_2(message):
        if message.text.lower() in ("отмена", "cancel"):
            return
        for elem in free_wonders:
            if elem.name.lower() == message.text.lower():
                status = players[message.chat.id].make_wonder(elem)
                if status:
                    bot.send_message(message.chat.id, "Вы успешно построили чудо света!")
                    free_wonders.remove(elem)
                    break
                else:
                    bot.send_message(message.chat.id, "Не удалось построить чудо света :(")
                    break
        else:
            bot.send_message(message.chat.id, "Такого чуда света не нашлось!\nПопробуйте снова...")
            bot.register_next_step_handler(message, make_wonder_2)
    

    @bot.message_handler(commands=['factory'])
    def factory(message):
        plr = players[message.chat.id]
        bot.send_message(message.chat.id,
            f"Для строительства вашей уникальной фабрики вам требуется {get_resname_by_id(plr.create_res[0])} в количестве {plr.create_res[1]}.\n" + \
            f"В этом ходу вы {'можете' if plr.able_create_factory else 'НЕ МОЖЕТЕ'} создать уникальную фабрику.\n" + 
            "Для её создания напишите /create")


    @bot.message_handler(commands=['create'])
    def create(message):
        status = players[message.chat.id].create_factory()
        if status[0]:
            if status[1]:
                bot.send_message(message.chat.id, f"Вы успешно создали уникальную фабрику!\nПроизводство улучшено на {round((factory_growup - 1) * 100)}%!")
            else:
                bot.send_message(message.chat.id, f"Вы успешно создали уникальную фабрику!")
        else:
            bot.send_message(message.chat.id, "Не удалось создать уникальную фабрику!")
    
    
    @bot.message_handler(commands=['change'])
    def change(message):
        status = players[message.chat.id].change_factory_res()
        msg = "Успешно!" if status else "Не успешно!"
        bot.send_message(message.chat.id, msg)
    

    @bot.message_handler(commands=['give'])
    def give(message):
        if not TESTING:
            return
        players[message.chat.id].money += 10_000
        bot.send_message(message.chat.id, "Вам начислено 10_000 монет!!!\nНИФИГА СЕБЕ!!!!!!!!")
    
    # @bot.message_handler(commands=['hide'])
    # def hide(message):
    #     bot.send_message(message.chat.id, "Вы точно уверены, что хотите пойти на такой отчаяный шаг? Введите <ТОЧНО>, чтобы подтвердить действие")


    def next_move():
        nonlocal move, skips
        move += 1
        skips = set()
        if move == moves + 2:
            final = {country.name : country.calculate_final_points() for country in players.values()}
            final = {k : v for k, v in sorted(final.items(), key=lambda x: -x[1])}
            final = list(final.items())
            for plr in players.keys():
                bot.send_message(plr,
                f"1ое место: {final[0][0]} : {final[0][1]}" if len(players) == 1 else
                f"1ое место: {final[0][0]} : {final[0][1]} баллов\n2ое место: {final[1][0]} : {final[1][1]}" if len(players) == 2 else
                f"1ое место: {final[0][0]} : {final[0][1]} баллов\n2ое место: {final[1][0]} : {final[1][1]} баллов\n3eе место: {final[2][0]} : {final[2][1]} баллов")
                bot.send_message(plr, f"Игра закончена, всем спасибо!")
                exit()
        for chat_id in players.keys():
            bot.send_message(chat_id, f"Ход {move - 1} / {moves} первой главы!")
        if not (move - 1) % wonder_per_moves:
            if not len(all_wonders) > 0:
                return
            tmp = choices(all_wonders, k=1)[0]
            free_wonders.add(tmp)
            all_wonders.remove(tmp)
            for chat_id in players.keys():
                bot.send_message(chat_id, "Новое чудо света может быть построено!")
        for country in players.values():
            country.move()
    

    # @bot.message_handler(commands=['dump'])
    # def save(message):
    #     file = open("data.pickle", "wb")
    #     pickle.dump((move, free_wonders, players), file, fix_imports=True)
    #     file.close()
    #     print("dumped!")
    
    # @bot.message_handler(commands=['load'])
    # def load(message):
    #     nonlocal move, free_wonders ,players
    #     file = open("data.pickle", "rb")
    #     move, free_wonders, players = pickle.load(file, fix_imports=True)
    #     file.close()
    #     print("loaded!")
    

    @bot.message_handler(content_types=['text'])
    def calc(message):
        try:
            if len(list(re.findall('[0-9]+', message.text))) < 2:
                raise Exception()
            bot.send_message(message.chat.id, eval(message.text.replace("^", "**")))
        except Exception as e:
            pass


    bot.infinity_polling()


if __name__ == "__main__":
    main()
