from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kavijar.auth import login_required, player_required, check_ban
from . import db, game_rules as gr

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
    building_costs = {}
    city = City.query.filter_by(idOwner=g.user.idUser).first()
    if city is not None:
        buildings = Building.query.filter_by(idCity=city.idCity).all()
        armies = Army.query.filter_by(idCityFrom=city.idCity).all()
        for bt in gr.building_types.keys():
            building_costs[bt] = gr.build_cost(bt, 1)
        for b in buildings:
            building_costs[b.type] = gr.build_cost(b.type, b.level+1)
    return render_template('playercity/city.html', city=city, buildings=buildings,
                           armies=armies, building_costs=building_costs)


@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/create_building/<string:type>', methods=('GET', 'POST'))
def create_building(b_type):
    if request.method == 'POST':
        city = City.query.filter_by(idOwner=g.user.idUser).first()
        existing_building = Building.query.filter_by(idCity=city.idCity, type=request.json.type).first()
        error = None
        if city is None:
            error = 'Grad ne postoji!'
        elif existing_building is not None:
            error = 'Gradjevina već postoji!'
        costs = gr.build_cost(b_type, 1)
        gold = costs['gold']
        wood = costs['wood']
        stone = costs['stone']
        if error is None and (gold > city.gold or wood > city.wood or stone > city.stone):
            error = 'Nedovoljno resursa!'
        if error is None:
            finishTime = datetime.datetime.now() + datetime.timedelta(minutes=gr.build_time(1, b_type))
            new_building = Building(idOwner=city.idCity, type=b_type, level=0, finishTime=finishTime, status='A')
            gr.adjust_resources(player=g.user, gold=gold, wood=wood, stone=stone)
            db.session.add(new_building)
            db.session.commit()
            flash(f"Uspešno je pokrenuta konstrukcija zgrade : {gr.building_types[b_type]}")
        else:
            flash(error)

    return redirect(url_for('playercity.player_city'))


@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/halt_building/<string:type>', methods=('GET', 'POST'))
def halt_building(b_type):
    if request.method == 'POST':
        city = City.query.filter_by(idOwner=g.user.idUser).first()
        existing_building = Building.query.filter_by(idCity=city.idCity, type=request.json.type).first()
        error = None
        if city is None:
            error = 'Grad ne postoji!'
        elif existing_building is None:
            error = 'Gradjevina ne postoji!'
        elif existing_building.finishTime is None:
            error = 'Ne možete obustaviti izgradnju koja se ne dešava!'
        costs = gr.build_cost(b_type, 1)
        gold = costs['gold'] * gr.refund_mult
        wood = costs['wood'] * gr.refund_mult
        stone = costs['stone'] * gr.refund_mult
        if error is None:
            if existing_building.level == 0:
                db.session.delete(existing_building)
            gr.adjust_resources(player=g.user, gold=gold, wood=wood, stone=stone)
            db.session.commit()
            flash(f"Uspešno ste obustavili rad na zgradi : {gr.building_types[b_type]}")
        else:
            flash(error)

    return redirect(url_for('playercity.player_city'))


@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/upgrade_building/<string:type>', methods=('GET', 'POST'))
def upgrade_building(b_type):
    if request.method == 'POST':
        city = City.query.filter_by(idOwner=g.user.idUser).first()
        existing_building = Building.query.filter_by(idCity=city.idCity, type=request.json.type).first()
        error = None
        if city is None:
            error = 'Grad ne postoji!'
        elif existing_building is None:
            error = 'Gradjevina ne postoji!'
        elif existing_building.finishTime is not None:
            error = 'Već ste pokrenuli izgradnju!'
        elif existing_building.level >= gr.building_max_level:
            error = 'Gradjevina je maksimalnog nivoa!'
        costs = gr.build_cost(b_type, existing_building.level+1)
        gold = costs['gold']
        wood = costs['wood']
        stone = costs['stone']
        if error is None and (gold > city.gold or wood > city.wood or stone > city.stone):
            error = 'Nedovoljno resursa!'
        if error is None:
            finishTime = datetime.datetime.now() \
                         + datetime.timedelta(minutes=gr.build_time(existing_building.level+1, b_type))
            #existing_building.level += 1
            existing_building.finishTime = finishTime
            gr.adjust_resources(player=g.user, gold=gold, wood=wood, stone=stone)
            db.session.commit()
            flash(f"Uspešno je pokrenuto unapredjenje zgrade : {gr.building_types[b_type]}")
        else:
            flash(error)

    return redirect(url_for('playercity.player_city'))
