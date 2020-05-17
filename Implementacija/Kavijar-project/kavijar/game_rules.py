import math, datetime
from .models import City, Building
from . import db

goldPerHour = 3
woodPerHour = 1
stonePerHour = 1

startingPopulation=40
startingGold=0
startingWood=400
startingStone=400

def createTownHall(idCity):
    db.session.add(Building(idCity=idCity, type="TH", status="A", level=0, finishTime=datetime.datetime.now()))
    db.session.commit()

def createCity(idOwner, name):
    db.session.add(City(idOwner=idOwner, name=name, xCoord=69, yCoord=420, population=startingPopulation,
                woodworkers=0, stoneworkers=0, civilians=startingPopulation, gold=startingGold, wood=startingWood, stone=startingStone, lastUpdate=datetime.datetime.now()))
    db.session.commit()

    idCity = City.query.filter_by(idOwner=idOwner, name=name).first().idCity
    createTownHall(idCity)


carry_capacity = [80, 120, 180, 260, 360]
growth_rate = 0.1


def growth(p0, dt, townHallLevel):
    k = carry_capacity[townHallLevel]
    r = growth_rate
    return k / (1 + (k-p0)/p0 * math.exp(-r*dt))