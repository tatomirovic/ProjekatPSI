import math, datetime

from .models import City, Building
from . import db



goldPerHour = 3
woodPerHour = 1
stonePerHour = 1

startingPopulation = 40
startingGold = 0
startingWood = 400
startingStone = 400

building_types = {
    'TH': 'Gradska uprava',
    'PI': 'Pilana',
    'KL': 'Kamenolom',
    'TS': 'Trgovinska stanica',
    'BP': 'Baraka za pešadiju',
    'BK': 'Baraka za konjicu',
    'BS': 'Baraka za strelce',
    'BO': 'Radionica opsadnog oružja',
}

building_costs = {
    'GU': {'gold': 500, 'wood': 300, 'stone': 600},
    'PI': {'gold': 130, 'wood': 0, 'stone': 250},
    'KL': {'gold': 30, 'wood': 100, 'stone': 250},
    'TS': {'gold': 200, 'wood': 200, 'stone': 200},
    'BP': {'gold': 70, 'wood': 100, 'stone': 150},
    'BK': {'gold': 150, 'wood': 100, 'stone': 150},
    'BS': {'gold': 100, 'wood': 100, 'stone': 150},
    'BI': {'gold': 300, 'wood': 500, 'stone': 150},
}

resource_caps = {
    0: 0,
    1: 1000,
    2: 3000,
    3: 10000,
    4: 50000,
    5: 150000
}

resource_allocation_limit = {
    0: 50,
    1: 1000,
    2: 10000,
    3: 50000,
    4: 250000,
    5: 1000000
}

building_costs_scaling = {
    0: 0,
    1: -1,
    2: -3,
    3: -10,
    4: -20,
    5: -100,
}
# Koristimo - jer se pri izgradnji GUBE resursi

refund_mult = -0.5
building_max_level = 5


def build_cost(type, level):
    return building_costs[type] * building_costs_scaling[level]


def build_time(level, b_type):
    buildTime = [5, 20, 60, 300, 1440]
    return buildTime[level]


# BITNO - POZVATI db.session.commit() POSLE OVE FUNKCIJE, NE POZIVA GA SAMA
# POZIVATI OVU F-JU PRE SVAKOG AZURIRANJA RESURSA
def adjust_resources(player, gold=0, wood=0, stone=0, pop=0, kavijar=0):
    city = City.query.filter_by(idOwner=player.idUser).first()
    if city is None:
        return
    city.gold += gold
    city.wood += wood
    city.stone += stone
    city.population += pop
    player.caviar += kavijar
    th_level = Building.query.filter_by(idCity=city.idCity, type="TH").first().level
    rcap = resource_caps[th_level]
    if city.gold > rcap:
        city.gold = rcap
    if city.wood > rcap:
        city.wood = rcap
    if city.stone > rcap:
        city.stone = rcap
    if city.gold < 0:
        city.gold = 0
    if city.wood < 0:
        city.wood < 0
    if city.stone < 0:
        city.stone < 0
    if city.population < startingPopulation:
        city.population = startingPopulation


def createTownHall(idCity):
    db.session.add(Building(idCity=idCity, type="TH", status="A", level=1, finishTime=datetime.datetime.now()))
    db.session.commit()


def createCity(idOwner, name):
    db.session.add(City(idOwner=idOwner, name=name, xCoord=69, yCoord=420, population=startingPopulation,
                        woodworkers=0, stoneworkers=0, civilians=startingPopulation, gold=startingGold,
                        wood=startingWood, stone=startingStone, lastUpdate=datetime.datetime.now()))
    db.session.commit()

    idCity = City.query.filter_by(idOwner=idOwner, name=name).first().idCity
    createTownHall(idCity)


carry_capacity = [80, 120, 180, 260, 360]
growth_rate = 0.1


def growth(p0, dt, townHallLevel):
    k = carry_capacity[townHallLevel]
    r = growth_rate
    return k / (1 + (k - p0) / p0 * math.exp(-r * dt))
