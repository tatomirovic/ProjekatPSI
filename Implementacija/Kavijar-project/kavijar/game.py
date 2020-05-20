from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, json
)
from werkzeug.exceptions import abort

from kavijar.auth import login_required, player_required, check_ban
from kavijar.auth import login_required
from . import db

from .models import City, Building
import functools, datetime
from . import updateWrappers

bp = Blueprint('game', __name__)


@bp.route('/')
@player_required
@check_ban
@updateWrappers.update_resources
def index():
    city_list = City.query.all()
    return render_template('game/main_map.html', city_list=map(json.dumps, city_list))


@bp.route('/get_tile/<x:int>/<y:int>')
@player_required
@check_ban
@updateWrappers.update_resources
def get_tile(x, y):
    city_list = City.query.filter(City.xCoord == x, City.yCoord == y).first()
    return city_list
