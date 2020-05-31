from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kavijar.auth import login_required, player_required, check_ban
from . import db, game_rules as gr

from .models import City, Building, Army
import functools, datetime
from . import updateWrappers

bp = Blueprint('building', __name__, url_prefix='/building')


@bp.route('/<b_type>')
@player_required
@check_ban
@updateWrappers.update_resources
def building_main(b_type):
    if b_type == 'TS':
        return redirect(url_for('tradingpost.trading_post'))
    elif b_type not in gr.building_types:
        return redirect(url_for('index'))
    city = City.query.filter_by(idOwner=g.user.idUser).first()
    building = Building.query.filter_by(idCity=city.idCity, type=b_type).first()
    error = None
    building_info = None
    upgrade_cost = None
    armies_sent = []
    garrison = None
    recruit_costs = []
    if building is None:
        error = 'Nemate tu gradjevinu!'
    elif building.level == 0:
        error = 'Nemate tu gradjevinu!'
    if error is None:
        upgrade_level = min(building.level + 1, gr.building_max_level)
        upgrade_cost = gr.build_cost(b_type, upgrade_level)
        building_info = building.serialize()
        for k, v in gr.barracks_allocation:
            if k == b_type:
                recruit_costs.append(gr.recruit_cost(v, 1))
        if b_type == 'ZD':
            armies_sent = Army.query.filter_by(idCityFrom=city.idCity, status='A').all()
            garrison = Army.query.filter_by(idCityFrom=city.idCity, status='G').first()
    else:
        flash(error)
    return render_template(f'building/building{b_type}.html', building_info=building_info,
                           upgrade_cost=upgrade_cost, recruit_costs=recruit_costs,
                           city=city, armies_sent=armies_sent, garrison=garrison)
