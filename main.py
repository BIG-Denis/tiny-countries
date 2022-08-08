
import json
import random
import telebot

from patterns import *
from functions import *
from random import randrange, choice, choices, shuffle


def main(maingame_phases_count, taivan_phases_count):

    TESTING = True
    phase = 1
    skips = set()
    countrys = []
    players = {}

    with open("token.json", 'r') as file:
        json_file = json.load(file)
        token = json_file["token"]

    bot = telebot.TeleBot(token, parse_mode=False)

    # game start
    @bot.message_handler(commands=['start'])
    def start(message):
        if players.get(message.chat.id) is None:
            players[message.chat.id] = -1
        if len(players.items()) == 3 if not TESTING else 1:
            names = country_names.copy()
            shuffle(names)
            names = names[:3]
            areas = [randrange(100, 400) for _ in range(3)]
            populations = [randrange(150, 500) for _ in range(3)]
            moneys = [randrange(100, 250) for _ in range(3)]
            resourcess = make_dict4(list(range(11, 20)) + list(range(21, 24)), 0, 25)
            income_ress = make_dict3(list(range(11, 20)), 35, 60)
            sold_costss = make_dict4x2(list(range(11, 20)) + list(range(21, 24)), 5, 25)
            big_res_moneys = [[randrange(2, 8) for _ in range(3)] for _ in range(3)]
            print(names, areas, populations, moneys, resourcess, income_ress, sold_costss, big_res_moneys, sep='\n')
            print(sold_costss)
            for i in range(3):
                countrys.append(Country(names[i], areas[i], populations[i], moneys[i], resourcess[i], income_ress[i], sold_costss[i], big_res_moneys[i]))
            shuffle(countrys)
            for i, key in enumerate(players.keys()):
                players[key] = countrys[i]
                countrys[i].chat_id = key
            for chat_id in players.keys():
                bot.send_message(chat_id, "Игра началась!")


    @bot.message_handler(commands=['help', 'h'])
    def help_msg(message):
        bot.send_message(message.chat.id, help_text)


    @bot.message_handler(commands=['skip'])
    def skip_msg(message):
        skips.add(message.chat.id)
        if len(skips) < len(players):
            bot.send_message(message.chat.id, f"Ваш голос учтён! За скип голосует уже {len(skips)} / {players_count} игроков.")
        else:
            next_phase()


    @bot.message_handler(commands=['infomain', 'info'])
    def info_msg(message):
        bot.send_message(message.chat.id, players[message.chat.id].get_info_main())


    @bot.message_handler(commands=['infoarmy', 'army'])
    def info_msg(message):
        bot.send_message(message.chat.id, players[message.chat.id].get_info_army())


    @bot.message_handler(commands=['infores', 'res'])
    def info_msg(message):
        bot.send_message(message.chat.id, players[message.chat.id].get_info_res())


    @bot.message_handler(commands=['money', 'balance'])
    def info_msg(message):
        bot.send_message(message.chat.id, players[message.chat.id].get_info_money())


    @bot.message_handler(commands=['handover'])  # MAYBE BUG IN HANDOVER
    def handover_msg_1(message):
        args = message.text.split()[1:]
        try:
            country_name, res_id, res_count, cost = args[0].lower(), resources_dict[args[1].lower()], int(args[2]), int(args[3])
            for country in players.values():
                if country.name == country_name:
                    from_chat_id = message.chat.id
                    for chat_id, _country in players.items():
                        if _country == country:
                            to_chat_id = chat_id
                            break
                    else:
                        bot.send_message(message.chat.id, "Ошибка, нет такой страны!")
                    players[to_chat_id].offered_trade = Trade(players[from_chat_id], from_chat_id, players[to_chat_id], to_chat_id, res_id, res_count, cost)
                    bot.send_message(to_chat_id, f"Вам поступило предложение покупки {get_resname_by_id(res_id)} в количестве {count} по цене {cost}\nПринять /accept")
                    break
        except Exception as e:
            bot.send_message(message.chat.id, f"В транзакции ошибка!\n{e}")


    @bot.message_handler(commands=['accept'])
    def accept_trade(message):
        if players[message.chat.id].offered_trade is not None:
            from_chat_id = players[message.chat.id].offered_trade.from_chat_id
            status = players[message.chat.id].offered_trade.accept()
            if status:
                bot.send_message(message.chat.id, "Предложение принято успешно!")
                bot.send_message(from_chat_id, f"Ваше предложение продажи ресурса {players[message.chat.id].name} принято!")
            else:
                bot.send_message(message.chat.id, "Не удалось принять предложение продажи!")
        else:
            bot.send_message(message.chat.id, "У вас нет актуальных предложений продажи!")


    @bot.message_handler(commands=['swiss'])
    def swiss(message):
        try:
            ammount = int(message.text.split()[1])
            players[message.chat.id].fund_swiss_bank(ammount)
            bot.send_message(message.chat.id, players[message.chat.id].get_info_money())
        except:
            bot.send_message(message.chat.id, "Не удалось положить деньги!")

    @bot.message_handler(commands=['corrupt'])
    def corrupt(message):
        status = players[message.chat.id].corrupt()
        msg = "Успешно!" if status else "Не успешно!"
        bot.send_message(message.chat.id, msg)

    @bot.message_handler(commands=['settax'])
    def set_tax(message):
        try:
            tax = int(message.text.split()[1])
            status = players[message.chat.id].set_tax_perc(tax)
            if status:
                bot.send_message(message.chat.id, "Успешно!")
            else:
                bot.send_message(message.chat.id, "нет, такой налог мы не поставим.")
        except:
            bot.send_message(message.chat.id, "Не удалось установить налог!")

    @bot.message_handler(commands=['build'])
    def build(message):
        try:
            arg = int(message.text.split()[1])
            status = players[message.chat.id].build_infr(arg)
            msg = "Успешно!" if status else "Не успешно!"
            bot.send_message(message.chat.id, msg)
        except Exception as e:
            bot.send_message(message.chat.id, "Не удалось!")

    def next_phase():
        nonlocal phase
        for chat_id in players.keys():
            bot.send_message(chat_id, f"Фаза {phase} / {maingame_phases_count} первой главы!")
        for country in players.values():
            country.phase_move()
        phase += 1

    bot.infinity_polling()


if __name__ == "__main__":
    main(16, 8)
