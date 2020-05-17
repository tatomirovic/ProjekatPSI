# coding: utf-8
from sqlalchemy import CHAR, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.mysql import BIT, INTEGER
from sqlalchemy.orm import relationship

from . import db;
Base = db.Model;

class User(Base):
    __tablename__ = 'user'

    idUser = Column(INTEGER(11), primary_key=True)
    username = Column(String(30), nullable=False, unique=True)
    password = Column(String(10000), nullable=False)
    role = Column(String(1), nullable=False)
    caviar = Column(INTEGER(11), nullable=False)
    statusUpdate = Column(INTEGER(11), nullable=False)
    dateUnban = Column(DateTime)
    dateCharLift = Column(DateTime)


class Chatmsg(Base):
    __tablename__ = 'chatmsg'

    idChat = Column(INTEGER(11), primary_key=True)
    idSender = Column(ForeignKey(u'user.idUser'), nullable=False)
    time = Column(DateTime, nullable=False)
    content = Column(String(128), nullable=False)

    user = relationship(u'User')


class City(Base):
    __tablename__ = 'city'

    idCity = Column(INTEGER(11), primary_key=True)
    idOwner = Column(ForeignKey(u'user.idUser'), nullable=False, index=True)
    name = Column(String(30), nullable=False)
    xCoord = Column(INTEGER(11), nullable=False)
    yCoord = Column(INTEGER(11), nullable=False)
    population = Column(INTEGER(11), nullable=False)
    woodworkers = Column(INTEGER(11), nullable=False)
    stoneworkers = Column(INTEGER(11), nullable=False)
    civilians = Column(INTEGER(11), nullable=False)
    gold = Column(INTEGER(11), nullable=False)
    wood = Column(INTEGER(11), nullable=False)
    stone = Column(INTEGER(11), nullable=False)
    lastUpdate = Column(DateTime, nullable=False)
    
    user = relationship(u'User')


class Mailmsg(Base):
    __tablename__ = 'mailmsg'

    idMail = Column(INTEGER(11), primary_key=True)
    idFrom = Column(ForeignKey(u'user.idUser'), nullable=False, index=True)
    idTo = Column(ForeignKey(u'user.idUser'), nullable=False, index=True)
    time = Column(DateTime, nullable=False)
    content = Column(String(256), nullable=False)
    readFlag = Column(BIT(1), nullable=False)

    user = relationship(u'User', primaryjoin='Mailmsg.idFrom == User.idUser')
    user1 = relationship(u'User', primaryjoin='Mailmsg.idTo == User.idUser')


class Army(Base):
    __tablename__ = 'army'

    idArmy = Column(INTEGER(11), primary_key=True)
    idCityFrom = Column(ForeignKey(u'city.idCity'), nullable=False, index=True)
    idCityTo = Column(ForeignKey(u'city.idCity'), nullable=False, index=True)
    status = Column(CHAR(1), nullable=False)
    timeToArrival = Column(DateTime)
    lakaPesadija = Column(INTEGER(11))
    teskaPesadija = Column(INTEGER(11))
    lakaKonjica = Column(INTEGER(11))
    teskaKonjica = Column(INTEGER(11))
    strelci = Column(INTEGER(11))
    samostrelci = Column(INTEGER(11))
    katapult = Column(INTEGER(11))
    trebuset = Column(INTEGER(11))

    city = relationship(u'City', primaryjoin='Army.idCityFrom == City.idCity')
    city1 = relationship(u'City', primaryjoin='Army.idCityTo == City.idCity')


class Building(Base):
    __tablename__ = 'building'

    idCity = Column(ForeignKey(u'city.idCity'), primary_key=True, nullable=False)
    type = Column(CHAR(2), primary_key=True, nullable=False)
    status = Column(CHAR(1), nullable=False)
    level = Column(INTEGER(11), nullable=False)
    finishTime = Column(DateTime, nullable=False)

    city = relationship(u'City')


class Recruiting(Base):
    __tablename__ = 'recruiting'

    idRecruiting = Column(INTEGER(11), primary_key=True)
    idCity = Column(ForeignKey(u'city.idCity'), nullable=False, index=True)
    type = Column(CHAR(1), nullable=False)
    finishTime = Column(DateTime, nullable=False)
    lowTier = Column(INTEGER(11))
    highTier = Column(INTEGER(11))

    city = relationship(u'City')


class Trade(Base):
    __tablename__ = 'trade'

    idTrade = Column(INTEGER(11), primary_key=True)
    idCity1 = Column(ForeignKey(u'city.idCity'), nullable=False, index=True)
    idCity2 = Column(ForeignKey(u'city.idCity'), nullable=False, index=True)
    status = Column(CHAR(1), nullable=False)
    gold1 = Column(INTEGER(11), nullable=False)
    wood1 = Column(INTEGER(11), nullable=False)
    stone1 = Column(INTEGER(11), nullable=False)
    gold2 = Column(INTEGER(11), nullable=False)
    wood2 = Column(INTEGER(11), nullable=False)
    stone2 = Column(INTEGER(11), nullable=False)

    city = relationship(u'City', primaryjoin='Trade.idCity1 == City.idCity')
    city1 = relationship(u'City', primaryjoin='Trade.idCity2 == City.idCity')