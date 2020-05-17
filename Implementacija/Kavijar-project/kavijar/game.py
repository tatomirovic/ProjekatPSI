from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kavijar.auth import login_required
from . import db;

bp = Blueprint('game', __name__)


@bp.route('/')
def index():
    return render_template('game/main_map.html')