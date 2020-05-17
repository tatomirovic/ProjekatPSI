from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kavijar.auth import login_required
from . import db;

from .models import City, Building
import functools, datetime
from . import updateWrappers

bp = Blueprint('game', __name__)


@bp.route('/')
@updateWrappers.update_resources
def index():
    return render_template('game/main_map.html')


