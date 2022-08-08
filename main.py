
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
            income_ress, sold_costss = gen_income_ress(minr=5, maxr=10, mins=3, maxs=12, big_field_k=5, hard_res_k=5)
            big_res_moneys = [[randrange(3, 10) for _ in range(3)] for _ in range(3)]  # rebalance?
            print(names, areas, populations, moneys, income_ress, sold_costss, big_res_moneys, sep='\n')
            print(sold_costss)
            for i in range(3):
                countrys.append(Country(names[i], areas[i], populations[i], moneys[i], income_ress[i], sold_costss[i], big_res_moneys[i]))
            shuffle(countrys)
            for i, key in enumerate(players.keys()):
                players[key] = countrys[i]
                countrys[i].chat_id = key
            for chat_id in players.keys():
                bot.send_message(chat_id, "Игра началась!")


    @bot.message_handler(commands=['help', 'h'])
    def help_msg(message):
        bot.send_message(message.chat.id, help_text)


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


    @bot.message_handler(commands=['skip', 'next'])
    def skip_msg(message):
        skips.add(message.chat.id)
        if len(skips) < len(players):
            bot.send_message(message.chat.id, f"Ваш голос учтён! За скип голосует уже {len(skips)} / {players_count} игроков.")
        else:
            next_phase()


    @bot.message_handler(commands=['handover'])
    def handover_1(message):
        bot.send_message(message.chat.id, "Введите название страны...")
        bot.register_next_step_handler(message, handover_2)

    def handover_2(message):
        if message.text.lower() == "отмена":
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
        if message.text.lower() == "отмена":
            return
        res_id = resources_dict.get(message.text.lower())
        if res_id is not None:
            bot.send_message(message.chat.id, "Введите количество ресурса...")
            bot.register_next_step_handler(message, handover_4, country, res_id)
            return
        else:
            bot.send_message(message.chat.id, "Кажется, нет такого ресурса\nВведите его название ещё раз...")
            bot.register_next_step_handler(message, handover_3, country)
            return

    def handover_4(message, country, res_id):
        if message.text.lower() == "отмена":
            return
        try:
            res_count = int(message.text)
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
        if message.text.lower() == "отмена":
            return
        try:
            price = int(message.text)
            if price < 0:
                bot.send_message(message.chat.id, "Положительные числа only!")
                bot.register_next_step_handler(message, handover_5, country, res_id, res_count)
                return
            else:
                msg = "Передача успешна!" if price == 0 else "Ваш запрос успешно отправлен!"
                bot.send_message(message.chat.id, msg)
                if price > 0:
                    bot.send_message(country.chat_id, f"Вам поступило предложение покупки {get_resname_by_id(res_id)} в количестве {res_count} по цене {price}\nПринять /accept")
                country.offered_trade = Trade(players[message.chat.id], message.chat.id, country, country.chat_id, res_id, res_count, price)
                if price == 0:
                    country.offered_trade.accept()
                    bot.send_message(country.chat_id, f"Страна {players[message.chat.id].name} передала вам {get_resname_by_id(res_id)} в количестве {res_count} штук")
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, "Некорректный ввод, попробуйте ещё раз...")
            bot.register_next_step_handler(message, handover_5, country, res_id, res_count)
            return


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
        bot.send_message(message.chat.id, "Введите желаемую сумму...")
        bot.register_next_step_handler(message, swiss_final)

    def swiss_final(message):
        if message.text.lower() == "отмена":
            return
        try:
            ammount = int(message.text)
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
        msg = "Успешно!" if status else "Не успешно!"
        bot.send_message(message.chat.id, msg)


    @bot.message_handler(commands=['spy'])
    def spy(message):
        bot.send_message(message.chat.id, "Введите название страны...")
        bot.register_next_step_handler(message, spy_final)

    def spy_final(message):
        if message.text.lower() == "отмена":
            return
        arg = message.text
        if not players[message.chat.id].swiss_bank - 300 >= 0:
            bot.send_message(message.chat.id, "Не хватает денег на счету Швейцарского банка!")
            return
        for country in players.values():
            if country.name.lower() == arg.lower():
                bot.send_message(message.chat.id, f"Репутация правительства в Стране {country.name}: {country.gov_reputation}")
                if random.randrange(0, 100+1) <= 40:
                    bot.send_message(country.chat_id, f"В вашей стране был обнаружен Шпион из страны {players[message.chat.id].name}")
        else:
            bot.send_message(message.chat.id, "Такой страны не нашлось!")


    @bot.message_handler(commands=['settax'])
    def set_tax(message):
        bot.send_message(message.chat.id, "Введите желаемый процент налога...")
        bot.register_next_step_handler(message, set_tax_final)

    def set_tax_final(message):
        if message.text.lower() == "отмена":
            return
        try:
            tax = int(message.text)
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
        if message.text.lower() == "отмена":
            return
        try:
            arg = int(message.text)
            status = players[message.chat.id].build_infr(arg)
            msg = "Успешно!" if status else "Не успешно!"
            bot.send_message(message.chat.id, msg)
        except:
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
