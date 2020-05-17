from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kavijar.auth import login_required, player_required
from . import db

from .models import City, Building
import functools, datetime
from . import updateWrappers

bp = Blueprint('game', __name__)


@bp.route('/')
@player_required
@updateWrappers.update_resources
def index():
    city_list = City.query.all()
    return render_template('game/main_map.html', city_list=city_list)


