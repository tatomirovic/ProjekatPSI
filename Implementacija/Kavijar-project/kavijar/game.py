from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kavijar.auth import login_required
from . import db;

from .models import City
import functools, datetime
from .game_constants import *

bp = Blueprint('game', __name__)


##Obavezno koristiti ovaj dekorator pre svake promene ulaza tabele city 
def update_resources(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        city = City.query.filter_by(idOwner=34).first()
        t0 = city.lastUpdate
        t1 = city.lastUpdate = datetime.datetime.now()
        dt = (t1 - t0).seconds

        city.gold += goldPerHour * city.civilians * dt / 3600
        city.wood += woodPerHour * city.woodworkers * dt / 3600
        city.stone += stonePerHour * city.stoneworkers * dt / 3600
        #city.civilians += logistic function tbi
        
        db.session.commit()
        return view(**kwargs)

    return wrapped_view


@bp.route('/')
@update_resources
def index():
    return render_template('game/main_map.html')


