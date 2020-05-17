from flask import (
    g, redirect, url_for
)

from werkzeug.exceptions import abort

from . import db

from .models import City, Building
import functools, datetime
from . import game_rules as gr


##Obavezno koristiti ovaj dekorator pri svakoj modifikaciji tabela city, building, army, trade, recruiting
def update_resources(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        city = City.query.filter_by(idOwner=g.user.idUser).first()
        t0 = city.lastUpdate
        t1 = city.lastUpdate = datetime.datetime.now()
        dt = (t1 - t0).seconds / 3600
        lvl = Building.query.filter_by(idCity=city.idCity, type='TH').first().level
        # city.gold += gr.goldPerHour * city.civilians * dt
        # TODO obracunati upkeep
        # city.wood += gr.woodPerHour * city.woodworkers * dt
        # city.stone += gr.stonePerHour * city.stoneworkers * dt

        # city.population = gr.growth(city.population, dt, lvl)
        gr.adjust_resources(player=g.user,
                            gold=gr.goldPerHour * city.civilians * dt,
                            wood=gr.woodPerHour * city.woodworkers * dt,
                            stone=gr.stonePerHour * city.stoneworkers * dt,
                            pop=gr.growth(city.population, dt, lvl))
        city.civilians = city.population - city.woodworkers - city.stoneworkers

        db.session.commit()
        return view(**kwargs)

    return wrapped_view
