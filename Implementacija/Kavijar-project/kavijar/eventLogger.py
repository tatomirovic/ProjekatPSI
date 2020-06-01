from flask import g

import math, datetime, random

from .models import City, Army, Trade, User, Building
from . import db, mail
from . import game_rules as gr
from .auxfunction import upgrade_building_function

## Preface za peru
## znam da je nepregledno za svakoga ko nije radio na projektu ali nasminkacu
## npr videces da statusi trgovine i armija nigde nisu dokumentovane, sve cu to dodati kad zapravo sve bude radilo
## verovatno cu premestiti vecinu konstanti u game_rules

unitUpkeep = {
    "LP": 3,
    "TP": 5,
    "ST": 6,
    "SS": 8,
    "LK": 12,
    "TK": 16,
    "KT": 30,
    "TR": 45
}


# returns upkeep of all armies
def armyUpkeepPH(army):
    return army.lakaPesadija * unitUpkeep["LP"] + army.teskaPesadija * unitUpkeep["TP"] + \
           army.strelci * unitUpkeep["ST"] + army.samostrelci * unitUpkeep["SS"] + \
           army.lakaKonjica * unitUpkeep["LK"] + army.teskaKonjica * unitUpkeep["TK"] + \
           army.katapult * unitUpkeep["KT"] + army.trebuset * unitUpkeep["TR"]


def garrisonArmy(army):
    garrison = Army.query.filter((Army.idCityFrom == army.idCityFrom) & (Army.status == "G")).first()
    garrison.lakaPesadija += army.lakaPesadija
    garrison.teskaPesadija += army.teskaPesadija
    garrison.lakaKonjica += army.lakaKonjica
    garrison.teskaKonjica += army.teskaKonjica
    garrison.strelci += army.strelci
    garrison.samostrelci += army.samostrelci
    garrison.katapult += army.katapult
    garrison.trebuset += army.trebuset

    db.session.delete(army)
    # db.commit()


class cityEvent:
    def __init__(self, time):
        self.time = time

    def execute(self):
        pass


class recruitingEvent(cityEvent):
    def __init__(self, time, army):
        cityEvent.__init__(self, time)
        self.army = army

    def execute(self):
        garrisonArmy(self.army)


# Attacker i defender - objekti tipa User
# attacker_loss i defender_loss - dictovi sa gubicima na obe strane, gde se kljucevi LP, TP itd
# plunder - dict sa tri kljuca gold, wood i stone
# building_damage - lista sa spiskom svih zgrada koje su ostecene za jedan lvl, vrednosti su TH, BP itd
def battle_report(attacker, defender, attacker_loss, defender_loss, plunder=None, building_damage=None):
    body = f'Rezultat bitke izmedju napadača {attacker.username} i branioca {defender.username} je'
    for k in attacker_loss.keys():
        body += f'\n Igrač {attacker.username} je izgubio {attacker_loss[k]} jedinica tipa {gr.unit_types[k]}'
    body += '\n\n'
    for k in defender_loss.keys():
        body += f'\n Igrač {defender.username} je izgubio {defender_loss[k]} jedinica tipa {gr.unit_types[k]}'
    if plunder is not None:
        gold_p = plunder['gold']
        wood_p = plunder['wood']
        stone_p = plunder['stone']
        body += f'\n\n Igrač {attacker.username} je osvojio {gold_p} zlata, {wood_p} drva i {stone_p} kamena'
    if building_damage is not None:
        body += '\n\n'
        for k in building_damage:
            body += f'Zgrada {gr.building_types[k]} igrača {defender.username} je oštećena'
    mail.send_msg_function(attacker, defender, body, datetime.datetime.now())

##  snaga jedne jedinice protiv druge u slucaju pogodnih uslova za prvu jedinicu
##  primer: snaga lake pesadije protiv strelaca u slucaju melee distance je 2 (1v2 je fer odnos)
##  druga strana primera: snaga strelaca protiv lake pesadije u slucaju velike distance (1v2.4 je fer odnos)
unitPower = {
    "LP": {
        "LP": 1,
        "TP": 0.6,
        "ST": 2,
        "SS": 1.6,
        "LK": 0.3,
        "TK": 0.2,
        "KT": 0.2,
        "TR": 0.2
    },
    "TP": {
        "LP": 1.66,
        "TP": 1,
        "ST": 3,
        "SS": 2.2,
        "LK": 0.5,
        "TK": 0.3,
        "KT": 0.2,
        "TR": 0.2
    },
    "ST": {
        "LP": 2.4,
        "TP": 1.2,
        "ST": 1,
        "SS": 0.6,
        "LK": 1.4,
        "TK": 0.6,
        "KT": 0.1,
        "TR": 0.1
    },
    "SS": {
        "LP": 3,
        "TP": 2.2,
        "ST": 1.66,
        "SS": 1,
        "LK": 2,
        "TK": 1,
        "KT": 0.1,
        "TR": 0.1
    },
    "LK": {
        "LP": 3,
        "TP": 2,
        "ST": 4,
        "SS": 2.4,
        "LK": 1,
        "TK": 0.5,
        "KT": 0.3,
        "TR": 0.3
    },
    "TK": {
        "LP": 5,
        "TP": 3,
        "ST": 6,
        "SS": 3,
        "LK": 2,
        "TK": 1,
        "KT": 0.3,
        "TR": 0.3
    },
    "KT": {
        "LP": 40,
        "TP": 40,
        "ST": 40,
        "SS": 40,
        "LK": 10,
        "TK": 8,
        "KT": 1,
        "TR": 1
    },
    "TR": {
        "LP": 60,
        "TP": 60,
        "ST": 60,
        "SS": 60,
        "LK": 20,
        "TK": 16,
        "KT": 1,
        "TR": 1
    },
}
##  igrac koji se brani dobija procentualni bonus za snagu
defenceBonus = [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]

##  olaksava dohvatanje atributa armije
stringToAttr = {
    "LP": lambda army: army.lakaPesadija,
    "TP": lambda army: army.teskaPesadija,
    "ST": lambda army: army.strelci,
    "SS": lambda army: army.samostrelci,
    "LK": lambda army: army.lakaKonjica,
    "TK": lambda army: army.teskaKonjica,
    "KT": lambda army: army.katapult,
    "TR": lambda army: army.trebuset,
}


class battleEvent(cityEvent):
    victoryRequirement = 0.7
    plunderCap = 0.8
    buildingDestructionCap = 3

    @staticmethod
    def armyPower(a1, a2):
        ##  snaga vojske zavisi od kompozicije protivnicke vojske kao sto je odredjeno konstantama iz unitPower recnika
        a2Numbers = sum([value(a2) for value in stringToAttr.values()])
        if a2Numbers == 0:
            return 1

        power = 0
        for aType, aAttr in stringToAttr.items():
            for dType, dAttr in stringToAttr.items():
                power += unitPower[aType][dType] * aAttr(a1) * dAttr(a2)
        
        return power / a2Numbers
        

    def __init__(self, time, attacker):
        cityEvent.__init__(self, time)
        self.attacker = attacker

    def execute(self):
        attacker = self.attacker

        city1 = City.query.filter_by(idCity=attacker.idCityFrom).first()
        player1 = User.query.filter_by(idUser=city1.idOwner).first()

        city2 = City.query.filter_by(idCity=attacker.idCityTo).first()
        player2 = User.query.filter_by(idUser=city2.idOwner).first()

        logEvents(player1, self.time)
        logEvents(player2, self.time)

        wall = Building.query.filter((Building.idCity==city2.idCity) & (Building.type=="ZD")).first()
        wallLvl = 0
        if wall:
            wallLvl = wall.level

        buildings = Building.query.filter((Building.idCity==city2.idCity) & (Building.type != "ZD") & ((Building.type != "TH") | (Building.type == "TH") & (Building.level != 1))).all()
        ## pretpostavka je da je garnizovana vojska uvek jedna armija i uvek postoji makar sa 0 jedinica
        ## sto je podrzano spajanjem vojske na kraju ove funkcije
        defender = Army.query.filter((Army.idCityFrom == attacker.idCityTo) & (Army.status == "G")).first()

        APower = battleEvent.armyPower(attacker, defender)
        DPower = battleEvent.armyPower(defender, attacker) * defenceBonus[wallLvl]
        print(f'Power vals APOWER {APower} DPOWER {DPower}')
        ALoss = APower / (APower + DPower)
        DLoss = 1 - ALoss

        AUnitLoss = {}
        DUnitLoss = {}
        for key, value in stringToAttr.items():
            AUnitLoss[key] = value(attacker)
            DUnitLoss[key] = value(defender)

        attacker.lakaPesadija *= ALoss; attacker.lakaPesadija = int(attacker.lakaPesadija)
        attacker.teskaPesadija *= ALoss; attacker.teskaPesadija = int(attacker.teskaPesadija)
        attacker.lakaKonjica *= ALoss; attacker.lakaKonjica = int(attacker.lakaKonjica)
        attacker.teskaKonjica *= ALoss; attacker.teskaKonjica = int(attacker.teskaKonjica)
        attacker.strelci *= ALoss; attacker.strelci = int(attacker.strelci)
        attacker.samostrelci *= ALoss; attacker.samostrelci = int(attacker.samostrelci)
        attacker.katapult *= ALoss; attacker.katapult = int(attacker.katapult)
        attacker.trebuset *= ALoss; attacker.trebuset = int(attacker.trebuset)

        defender.lakaPesadija *= DLoss; defender.lakaPesadija = int(defender.lakaPesadija)
        defender.teskaPesadija *= DLoss; defender.teskaPesadija = int(defender.teskaPesadija)
        defender.lakaKonjica *= DLoss; defender.lakaKonjica = int(defender.lakaKonjica)
        defender.teskaKonjica *= DLoss; defender.teskaKonjica = int(defender.teskaKonjica)
        defender.strelci *= DLoss; defender.strelci = int(defender.strelci)
        defender.samostrelci *= DLoss; defender.samostrelci = int(defender.samostrelci)
        defender.katapult *= DLoss; defender.katapult = int(defender.katapult)
        defender.trebuset *= DLoss; defender.trebuset = int(defender.trebuset)

        for key, value in stringToAttr.items():
            AUnitLoss[key] -= value(attacker)
            DUnitLoss[key] -= value(defender)

        plunder = None
        damagedBuildings = None
        if ALoss > battleEvent.victoryRequirement:
            severity = (ALoss - battleEvent.victoryRequirement) / (1 - battleEvent.victoryRequirement)
            wall.level -= 1
            upgrade_building_function(wall, use_resources=False)
            if len(buildings):
                destroyed = int(severity * battleEvent.buildingDestructionCap)
                damagedBuildings = random.sample(buildings, destroyed)
                for damagedBuilding in damagedBuildings:
                    damagedBuilding.level -= 1
                    upgrade_building_function(damagedBuilding, use_resources=False)

            stolen = battleEvent.plunderCap * severity
            plunder = {
                "gold": int(city2.gold * stolen),
                "wood": int(city2.wood * stolen),
                "stone": int(city2.stone * stolen), 
            }
            gr.adjust_resources(player1, gold=plunder["gold"], wood=plunder["wood"],
                                stone=plunder["stone"], debug=True, context='eventlogger battle_p1')
            gr.adjust_resources(player2, gold=-plunder["gold"], wood=-plunder["wood"], stone=-plunder["stone"], debug=True,
                                context='eventlogger battle_p2')
        
        battle_report(player1, player2, AUnitLoss, DUnitLoss, plunder, damagedBuildings)

        garrisonArmy(attacker)


class tradeEvent(cityEvent):
    def __init__(self, time, trade):
        cityEvent.__init__(self, time)
        self.trade = trade

    def execute(self):
        trade = self.trade

        idPlayer1 = City.query.filter_by(idCity=trade.idCity1).first().idOwner
        player1 = User.query.filter_by(idUser=idPlayer1).first()

        idPlayer2 = City.query.filter_by(idCity=trade.idCity2).first().idOwner
        player2 = User.query.filter_by(idUser=idPlayer2).first()

        logEvents(player1, self.time)
        logEvents(player2, self.time)

        gr.adjust_resources(player1, gold=trade.gold2, wood=trade.wood2, stone=trade.stone2, debug=True,
                            context='eventlogger trade_p1')
        gr.adjust_resources(player2, gold=trade.gold1, wood=trade.wood1, stone=trade.stone1, debug=True,
                            context='eventlogger trade_p2')

        ## obavestiti igrace
        db.session.delete(trade)
        # db.session.commit()


class buildEvent(cityEvent):
    def __init__(self, time, building):
        cityEvent.__init__(self, time)
        self.building = building

    def execute(self):
        self.building.level += 1
        self.building.status = 'A'  # active
        # db.session.commit()


def logEvents(player, upTo):
    # print('Entering logevents')
    city = City.query.filter_by(idOwner=player.idUser).first()
    if city is None:
        return
    if city.lastUpdate >= upTo:
        return

    eventList = []

    recruitings = Army.query.filter(
        (Army.idCityFrom == city.idCity) & (Army.status == 'R') & (Army.timeToArrival <= upTo)
    ).all()
    for recruiting in recruitings:
        eventList.append(recruitingEvent(recruiting.timeToArrival, recruiting))

    battles = Army.query.filter(
        (Army.status == 'A') & (Army.timeToArrival <= upTo) &
        ((Army.idCityFrom == city.idCity) | (Army.idCityTo == city.idCity))
    ).all()
    for battle in battles:
        eventList.append(battleEvent(battle.timeToArrival, battle))

    trades = Trade.query.filter(
        (Trade.status == 'A') & (Trade.timeToArrival <= upTo) &
        ((Trade.idCity1 == city.idCity) | (Trade.idCity2 == city.idCity))
    ).all()
    for trade in trades:
        eventList.append(tradeEvent(trade.timeToArrival, trade))

    buildings = Building.query.filter(
        (Building.status == 'U') & (Building.finishTime <= upTo)
    )
    for building in buildings:
        eventList.append(buildEvent(building.finishTime, building))

    armies = Army.query.filter(Army.idCityFrom == city.idCity).all()

    lvl = Building.query.filter_by(idCity=city.idCity, type='TH').first().level

    eventList.sort(key=lambda event: event.time)
    for event in eventList:
        ## obradi dogadjaje do odredjenog trenutka
        if event.time >= upTo:
            break
        t0 = city.lastUpdate
        city.lastUpdate = event.time
        db.session.commit()
        t1 = city.lastUpdate
        dt = (t1 - t0).seconds / 3600

        totalUpkeep = 0
        if totalUpkeep < 0:
            totalUpkeep = 0
        for army in armies:
            totalUpkeep += armyUpkeepPH(army)
        print(
            f't0 is {t0} t1 is {t1} gr.goldPerHour is {gr.goldPerHour} city.civilians is {city.civilians} totalupkeep is {totalUpkeep} dt is {dt}')
        gr.adjust_resources(player=g.user,
                            gold=(gr.goldPerHour * city.civilians / gr.timescaler - totalUpkeep) * dt,
                            wood=gr.woodPerHour * city.woodworkers / gr.timescaler * dt,
                            stone=gr.stonePerHour * city.stoneworkers / gr.timescaler * dt,
                            pop=gr.growth(city.population, dt, lvl) - city.population, debug=True,
                            context='eventlogger maint 1')
        city.civilians = city.population - city.woodworkers - city.stoneworkers
        event.execute()

    t0 = city.lastUpdate
    city.lastUpdate = upTo
    db.session.commit()
    t1 = city.lastUpdate
    dt = (t1 - t0).seconds / 3600

    totalUpkeep = 0
    for army in armies:
        totalUpkeep += armyUpkeepPH(army)
    print(
        f't0 is {t0} t1 is {t1} gr.goldPerHour is {gr.goldPerHour} city.civilians is {city.civilians} totalupkeep is {totalUpkeep} dt is {dt}')
    gr.adjust_resources(player=g.user,
                        gold=(gr.goldPerHour * city.civilians / gr.timescaler - totalUpkeep) * dt,
                        wood=gr.woodPerHour * city.woodworkers / gr.timescaler * dt,
                        stone=gr.stonePerHour * city.stoneworkers / gr.timescaler * dt,
                        pop=gr.growth(city.population, dt, lvl) - city.population, debug=True,
                        context='eventlogger maint 2')
    city.civilians = city.population - city.woodworkers - city.stoneworkers
    db.session.commit()
