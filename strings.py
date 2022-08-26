
war_buys = {
    51: "1: 1 человек + 250 монет\n2: 1 человек + 1 стекло",
    52: "1: 750 монет\n2: 400 монет + 2 стали\n3: 3 стали + 1 электроника",
    53: "1: 1200 монет\n2: 750 монет + 3 стали\n3: 5 стали + 2 электроники",
    54: "1: 2000 монет\n2: 1200 монет + 5 стали\n3: 7 стали + 3 электроники",
    55: "1: 2500 монет\n2: 1500 монет + 6 стали\n3: 8 стали + 4 электроники"
}

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

help_text = """
/help - показать список команд
/infomain - основная информация о стране
/infoarmy - информация об армии
/infores - информация о ресурсах
/money - показать баланс
/countrys - показать список всех стран в игре
/settax - установить налоговый процент
/build - построить инфраструктуру
/sell - продать ресурсы
/sellall - продать все ресурсы на складе
/skip - проголосовать за скип фазы
/handover - Предложение продажи / передачи ресурсов
/accept - принять торг / передачу ресурсов
/buy - купить военных и военную технику
/sweden - положить деньги на счёт в Швецком банке
/corrupt - подкупить ЦИК (+3 репутации, -500 в Швецком банке)
/spy - отослать шпиона (узнать репутацию правительства, -300 в Швецском банке)
/craft - сделать сложные ресурсы
/war - начать войну с другой страной
/tasks - просмотреть цели на игру
/wonders - просмотреть доступные чудеса света
/make - построить чудеса света
/factory - узнать про уникальную фабрику
/create - построить уникальную фабрику
/change - изменить ресурсы для уникальной фабрики (10k денег)
"""
# /hide - разворовать страну и залечь на дно

resources_dict = {
    "железо" : 11,
    "еда" : 12,
    "золото" : 13,
    "нефть" : 14,
    "медь" : 15,
    "кварц" : 16,
    "сталь" : 21,
    "электроника" : 22,
    "стекло" : 23,
    }


def get_resname_by_id(fid: int):
    for name, id in resources_dict.items():
        if id == fid:
            return name
    return None


"""
RESOUSES:
    RAW:
        11 iron    (raw)
        12 food    (raw)
        13 gold    (raw)
        14 oil     (raw)
        15 copper  (raw)
        16 quartz  (raw)
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
