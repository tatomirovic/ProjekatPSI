from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kavijar.auth import login_required, player_required, check_ban
from . import db

from .models import City, Building, Army
import functools, datetime
from . import updateWrappers

bp = Blueprint('playercity', __name__, url_prefix='/playercity')


@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/', methods=('GET', 'POST'))
def player_city():
    buildings = []
    armies = []
    city = City.query.filter_by(idOwner=g.user.idUser).first()
    if city is not None:
        buildings = Building.query.filter_by(idCity=city.idCity).all()
        armies = Army.query.filter_by(idCityFrom=city.idCity).all()
    return render_template('playercity/city.html', city=city, buildings=buildings, armies=armies)


@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/create_building', methods=('GET', 'POST'))
def player_city():
    return redirect(url_for('playercity.player_city'))
