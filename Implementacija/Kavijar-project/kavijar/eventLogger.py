from flask import g

import math, datetime

from .models import City, Army, Trade, User, Building
from . import db
from . import game_rules as gr


## TODO  svi eventovi koji uticu na dva igraca
#  morace da imaju dodatan status "obradio jedan"
#  ovi eventovi ce ostati na bazi da cekaju drugog igraca da ih obradi pre brisanja


## Preface za peru
## znam da je nepregledno za svakoga ko nije radio na projektu ali nasminkacu
## npr videces da statusi trgovine i armija nigde nisu dokumentovane, sve cu to dodati kad zapravo sve bude radilo
## verovatno cu premestiti vecinu konstanti u game_rules

unitUpkeep = {
    "LP" : 3,
    "TP" : 5,
    "ST" : 6,
    "SS" : 8,
    "LK" : 12,
    "TK" : 16,
    "KT" : 30,
    "TR" : 45
}

class cityEvent:
    def __init__(self, time):
        self.time = time
    def execute(self):
        pass

class battleEvent(cityEvent):
    
    unitWeight = {
        "LP" : 1,
        "TP" : 1.8,
        "ST" : 2.4,
        "SS" : 3,
        "LK" : 4,
        "TK" : 6,
        "KT" : 30,
        "TR" : 45
    }
    victoryRequirement = 0.7
    plunderCap = 0.8
    
    @staticmethod
    def armyPower(army):
        unitWeight = battleEvent.unitWeight
        return army.lakaPesadija * unitWeight["LP"] + army.teskaPesadija * unitWeight["TP"] +\
        army.lakaKonjica * unitWeight["LK"] + army.teskaKonjica * unitWeight["TK"] +\
        army.strelci * unitWeight["ST"] + army.samostrelci * unitWeight["SS"] +\
        army.katapult * unitWeight["KT"] + army.trebuset * unitWeight["TR"]
                        
    def __init__(self, time, attacker):
        cityEvent.__init__(self, time)
        self.attacker = attacker

    def execute(self):
        attacker = self.attacker
        ## pretpostavka je da je garnizovana vojska uvek jedna armija i uvek postoji makar sa 0 jedinica
        ## sto je podrzano spajanjem vojske na kraju ove funkcije
        defender = Army.query.filter((Army.idCityFrom==attacker.idCityTo) & (Army.status=="G")).first()
        
        APower = battleEvent.armyPower(attacker)
        DPower = battleEvent.armyPower(defender)

        ALoss = DPower / (APower + DPower)
        DLoss = 1 - ALoss

        attacker.lakaPesadija *= ALoss; attacker.teskaPesadija *= DLoss
        attacker.lakaKonjica *= ALoss; attacker.teskaKonjica *= DLoss
        attacker.strelci *= ALoss; attacker.samostrelci *= DLoss
        attacker.katapult *= ALoss; attacker.trebuset *= DLoss

        defender.lakaPesadija *= ALoss; defender.teskaPesadija *= DLoss
        defender.lakaKonjica *= ALoss; defender.teskaKonjica *= DLoss
        defender.strelci *= ALoss; defender.samostrelci *= DLoss
        defender.katapult *= ALoss; defender.trebuset *= DLoss

        if DLoss > battleEvent.victoryRequirement:
        
            ## !!PERO predlazem da adjust_resources prihvata grad umesto igraca
            ## da se ne bi drkao ovako svaki put, player argument koristimo samo za kavijar
            ## koji ne moze da se plunderuje niti da se tradeuje, tako da mislim
            ## da bi trebalo da napravimo funkciju samo za dodeljivanje kavijara
            ## pogotovo zato sto predstavlja v-bucks
            city1 = City.query.filter_by(idCity=attacker.idCityFrom).first()
            player1 = User.query.filter_by(idUser=city1.idOwner).first()
            
            city2 = City.query.filter_by(idCity=attacker.idCityTo).first()
            player2 = User.query.filter_by(idUser=city2.idOwner).first()
            
            plunderCap = battleEvent.plunderCap
            gr.adjust_resources(player1, gold=city2.gold*plunderCap, wood=city2.wood*plunderCap, stone=city2.stone*plunderCap)
            gr.adjust_resources(player2, gold=-city2.gold*plunderCap, wood=-city2.wood*plunderCap, stone=-city2.stone*plunderCap)
            ## velicina plena i victoryRequirement bi mogli da zavise od drugih faktora
            ## mogla bi i populacija neuspesno odbranjenog grada da se umanji
            ## obavestiti igrace

        ## spajanje vojske

        garnizovanaVojskaNapadaca = Army.query.filter((Army.idCityFrom == attacker.idCityFrom) & (Army.status == "G")).first()
        garnizovanaVojskaNapadaca.lakaPesadija += attacker.lakaPesadija
        garnizovanaVojskaNapadaca.teskaPesadija += attacker.teskaPesadija
        garnizovanaVojskaNapadaca.lakaKonjica += attacker.lakaKonjica
        garnizovanaVojskaNapadaca.teskaKonjica += attacker.teskaKonjica
        garnizovanaVojskaNapadaca.strelci += attacker.strelci
        garnizovanaVojskaNapadaca.samostrelci += attacker.samostrelci
        garnizovanaVojskaNapadaca.katapult += attacker.katapult
        garnizovanaVojskaNapadaca.trebuset += attacker.trebuset

        ## izbaciti attacker armiju iz baze, valjda ovako
        db.session.delete(attacker)

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

        gr.adjust_resources(player1, gold=trade.gold2, wood=trade.wood2, stone=trade.stone2)
        gr.adjust_resources(player2, gold=trade.gold1, wood=trade.wood1, stone=trade.stone1)

        trade.status = "S" ## success
        ## obavestiti igrace
        db.session.delete(trade)

# returns upkeep of all armies 
def armyUpkeepPH(army):
    return  army.lakaPesadija * unitUpkeep["LP"] + army.teskaPesadija * unitUpkeep["TP"] +\
            army.strelci * unitUpkeep["ST"] + army.samostrelci * unitUpkeep["SS"] +\
            army.lakaKonjica * unitUpkeep["LK"] + army.teskaKonjica * unitUpkeep["TK"] +\
            army.katapult * unitUpkeep["KT"] + army.trebuset * unitUpkeep["TR"]


def logEvents(player):
    city = City.query.filter_by(idOwner=player.idUser).first()
    if city is None:
        return
    
    eventList = []

    armies = Army.query.filter((Army.idCityFrom==city.idCity) | (Army.idCityTo==city.idCity)).all()
    for army in armies:
        if army.status == "A" and army.timeToArrival > datetime.datetime.now(): ## A : attacking
            eventList.append(battleEvent(army.timeToArrival, army))
    
    trades = Trade.query.filter((Trade.idCity1==city.idCity) | (Trade.idCity2==city.idCity)).all()
    for trade in trades:
        if trade.status == "A" and trade.timeToArrival > datetime.datetime.now(): ## A : accepted
            eventList.append(tradeEvent(trade.timeToArrival, trade))

    
    lvl = Building.query.filter_by(idCity=city.idCity, type='TH').first().level

    eventList.sort(key = lambda event: event.time)
    for event in eventList:
        t0 = city.lastUpdate
        t1 = city.lastUpdate = event.time
        dt = (t1 - t0).seconds / 3600

        totalUpkeep = 0
        for army in armies:
            totalUpkeep += armyUpkeepPH(army)

        gr.adjust_resources(player=g.user,
                            gold=(gr.goldPerHour * city.civilians - totalUpkeep)* dt,
                            wood=gr.woodPerHour * city.woodworkers * dt,
                            stone=gr.stonePerHour * city.stoneworkers * dt,
                            pop=gr.growth(city.population, dt, lvl) - city.population)
        city.civilians = city.population - city.woodworkers - city.stoneworkers
        event.execute()

    t0 = city.lastUpdate
    t1 = city.lastUpdate = datetime.datetime.now()
    dt = (t1 - t0).seconds / 3600

    totalUpkeep = 0
    for army in armies:
        totalUpkeep += armyUpkeepPH(army)

    gr.adjust_resources(player=g.user,
                        gold=(gr.goldPerHour * city.civilians - totalUpkeep)* dt,
                        wood=gr.woodPerHour * city.woodworkers * dt,
                        stone=gr.stonePerHour * city.stoneworkers * dt,
                        pop=gr.growth(city.population, dt, lvl) - city.population)
    city.civilians = city.population - city.woodworkers - city.stoneworkers
    db.session.commit()