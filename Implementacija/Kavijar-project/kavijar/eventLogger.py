from flask import g

import math, datetime

from .models import City, Army, Trade, User, Building
from . import db
from . import game_rules as gr

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


class battleEvent(cityEvent):
    unitWeight = {
        "LP": 1,
        "TP": 1.8,
        "ST": 2.4,
        "SS": 3,
        "LK": 4,
        "TK": 6,
        "KT": 30,
        "TR": 45
    }
    victoryRequirement = 0.7
    plunderCap = 0.8

    @staticmethod
    def armyPower(army):
        unitWeight = battleEvent.unitWeight
        return army.lakaPesadija * unitWeight["LP"] + army.teskaPesadija * unitWeight["TP"] + \
               army.lakaKonjica * unitWeight["LK"] + army.teskaKonjica * unitWeight["TK"] + \
               army.strelci * unitWeight["ST"] + army.samostrelci * unitWeight["SS"] + \
               army.katapult * unitWeight["KT"] + army.trebuset * unitWeight["TR"]

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

        ## pretpostavka je da je garnizovana vojska uvek jedna armija i uvek postoji makar sa 0 jedinica
        ## sto je podrzano spajanjem vojske na kraju ove funkcije
        defender = Army.query.filter((Army.idCityFrom == attacker.idCityTo) & (Army.status == "G")).first()

        APower = battleEvent.armyPower(attacker)
        DPower = battleEvent.armyPower(defender)

        ALoss = DPower / (APower + DPower)
        DLoss = 1 - ALoss

        attacker.lakaPesadija *= ALoss;
        attacker.teskaPesadija *= DLoss
        attacker.lakaKonjica *= ALoss;
        attacker.teskaKonjica *= DLoss
        attacker.strelci *= ALoss;
        attacker.samostrelci *= DLoss
        attacker.katapult *= ALoss;
        attacker.trebuset *= DLoss

        defender.lakaPesadija *= ALoss;
        defender.teskaPesadija *= DLoss
        defender.lakaKonjica *= ALoss;
        defender.teskaKonjica *= DLoss
        defender.strelci *= ALoss;
        defender.samostrelci *= DLoss
        defender.katapult *= ALoss;
        defender.trebuset *= DLoss

        if DLoss > battleEvent.victoryRequirement:
            plunderCap = battleEvent.plunderCap
            gr.adjust_resources(player1, gold=city2.gold * plunderCap, wood=city2.wood * plunderCap,
                                stone=city2.stone * plunderCap, debug=True, context='eventlogger battle_p1')
            gr.adjust_resources(player2, gold=-city2.gold * plunderCap, wood=-city2.wood * plunderCap, debug=True, context='eventlogger battle_p2',
                                stone=-city2.stone * plunderCap)

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

        gr.adjust_resources(player1, gold=trade.gold2, wood=trade.wood2, stone=trade.stone2, debug=True, context='eventlogger trade_p1')
        gr.adjust_resources(player2, gold=trade.gold1, wood=trade.wood1, stone=trade.stone1, debug=True, context='eventlogger trade_p2')

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
    #print('Entering logevents')
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
        print(f't0 is {t0} t1 is {t1} gr.goldPerHour is {gr.goldPerHour} city.civilians is {city.civilians} totalupkeep is {totalUpkeep} dt is {dt}')
        gr.adjust_resources(player=g.user,
                            gold=(gr.goldPerHour * city.civilians / gr.timescaler - totalUpkeep) * dt,
                            wood=gr.woodPerHour * city.woodworkers / gr.timescaler * dt,
                            stone=gr.stonePerHour * city.stoneworkers / gr.timescaler * dt,
                            pop=gr.growth(city.population, dt, lvl) - city.population, debug=True, context='eventlogger maint 1')
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
    print(f't0 is {t0} t1 is {t1} gr.goldPerHour is {gr.goldPerHour} city.civilians is {city.civilians} totalupkeep is {totalUpkeep} dt is {dt}')
    gr.adjust_resources(player=g.user,
                        gold=(gr.goldPerHour * city.civilians / gr.timescaler - totalUpkeep) * dt,
                        wood=gr.woodPerHour * city.woodworkers / gr.timescaler * dt,
                        stone=gr.stonePerHour * city.stoneworkers / gr.timescaler * dt,
                        pop=gr.growth(city.population, dt, lvl) - city.population, debug=True, context='eventlogger maint 2')
    city.civilians = city.population - city.woodworkers - city.stoneworkers
    db.session.commit()

