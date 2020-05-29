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


def sanitycheck(val):
    try:
        return int(val) >= 0
    except ValueError:
        return False

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
            building_costs[b.type] = gr.build_cost(b.type, b.level + 1)
    return render_template('playercity/city.html', city=city, buildings=buildings,
                           armies=armies, building_costs=building_costs, buildingnames=gr.building_types)


# @player_required
# @check_ban
# @updateWrappers.update_resources
# @bp.route('/create_building/<b_type>', methods=('GET', 'POST'))
# def create_building(b_type):
#    if request.method == 'POST':
#        city = City.query.filter_by(idOwner=g.user.idUser).first()
#        existing_building = Building.query.filter_by(idCity=city.idCity, type=b_type).first()
#        error = None
#        if city is None:
#            error = 'Grad ne postoji!'
#        elif existing_building is not None:
#            error = 'Gradjevina već postoji!'
#        costs = gr.build_cost(b_type, 1)
#        gold = costs['gold']
#        wood = costs['wood']
#        stone = costs['stone']
#        if error is None and (-gold > city.gold or -wood > city.wood or -stone > city.stone):
#            error = 'Nedovoljno resursa!'
#        if error is None:
#            finishTime = datetime.datetime.now() + datetime.timedelta(minutes=gr.build_time(1, b_type))
#            new_building = Building(idOwner=city.idCity, type=b_type, level=0, finishTime=finishTime, status='U')
#            gr.adjust_resources(player=g.user, gold=gold, wood=wood, stone=stone)
#            db.session.add(new_building)
#            db.session.commit()
#            flash(f"Uspešno je pokrenuta konstrukcija zgrade : {gr.building_types[b_type]}")
#        else:
#            flash(error)

    #return redirect(url_for('playercity.player_city'))


@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/halt_building/<b_type>', methods=('GET', 'POST'))
def halt_building(b_type):
    if request.method == 'POST':
        city = City.query.filter_by(idOwner=g.user.idUser).first()
        existing_building = Building.query.filter_by(idCity=city.idCity, type=b_type).first()
        error = None
        if city is None:
            error = 'Grad ne postoji!'
        elif existing_building is None:
            error = 'Gradjevina ne postoji!'
        elif existing_building.status != 'U':
            error = 'Ne možete obustaviti izgradnju koja se ne dešava!'
        costs = gr.build_cost(b_type, 1)
        gold = costs['gold'] * gr.refund_mult
        wood = costs['wood'] * gr.refund_mult
        stone = costs['stone'] * gr.refund_mult
        if error is None:
            # if existing_building.level == 0:
            # db.session.delete(existing_building)
            gr.adjust_resources(player=g.user, gold=gold, wood=wood, stone=stone)
            existing_building.status = 'A'
            existing_building.finishTime = None
            db.session.commit()
            flash(f"Uspešno ste obustavili rad na zgradi : {gr.building_types[b_type]}")
        else:
            flash(error)

    return redirect(url_for('playercity.player_city'))


@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/upgrade_building/<b_type>', methods=('GET', 'POST'))
def upgrade_building(b_type):
    if request.method == 'POST':
        city = City.query.filter_by(idOwner=g.user.idUser).first()
        existing_building = Building.query.filter_by(idCity=city.idCity, type=b_type).first()
        error = None
        if city is None:
            error = 'Grad ne postoji!'
        elif existing_building is None:
            error = 'Gradjevina ne postoji!'
        elif existing_building.status != 'A':
            error = 'Već ste pokrenuli izgradnju!'
        elif existing_building.level >= gr.building_max_level:
            error = 'Gradjevina je maksimalnog nivoa!'
        upgrade_level = min(existing_building.level + 1, gr.building_max_level)
        costs = gr.build_cost(b_type, upgrade_level)
        gold = costs['gold']
        wood = costs['wood']
        stone = costs['stone']
        if error is None and (-gold > city.gold or -wood > city.wood or -stone > city.stone):
            error = 'Nedovoljno resursa!'
        if error is None:
            finishTime = datetime.datetime.now() \
                + datetime.timedelta(minutes=gr.build_time(upgrade_level, b_type))
            # existing_building.level += 1
            existing_building.finishTime = finishTime
            existing_building.status = 'U'
            gr.adjust_resources(player=g.user, gold=gold, wood=wood, stone=stone)
            db.session.commit()
            flash(f"Uspešno je pokrenuto unapredjenje zgrade : {gr.building_types[b_type]}")
        else:
            flash(error)

    return redirect(url_for('playercity.player_city'))


@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/reassign_workers', methods=('GET', 'POST'))
def reassign_workers():
    if request.method == 'POST':
        city = City.query.filter_by(idOwner=g.user.idUser).first()
        Pilana = Building.query.filter_by(idCity=city.idCity, type="PI").first()
        Kamenolom = Building.query.filter_by(idCity=city.idCity, type="KL").first()
        pilana_level = 0
        kamenolom_level = 0
        if Pilana is not None:
            pilana_level = Pilana.level
        if Kamenolom is not None:
            kamenolom_level = Kamenolom.level
        ww = request.form['woodworkers']
        sw = request.form['stoneworkers']
        error = None
        if not sanitycheck(ww) or not sanitycheck(sw):
            error = 'Loš format raspodele!'
        if error is None:
            ww = int(ww)
            sw = int(sw)
            wwlimit = gr.resource_allocation_limit[pilana_level]
            swlimit = gr.resource_allocation_limit[kamenolom_level]
            if ww > wwlimit:
                ww = wwlimit
            if sw > swlimit:
                sw = swlimit
            if ww + sw > city.population:
                error = 'Nedovoljno populacije!'
            if error is None:
                civ = city.population - ww - sw
                city.woodworkers = ww
                city.stoneworkers = sw
                city.civilians = civ
        else:
            flash(error)
    return redirect(url_for('building.building_main', b_type='TH'))


@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/recruit_unit/<u_type>/<int:quantity>', methods=('GET', 'POST'))
def recruit_unit(u_type, quantity):
    if request.method == 'POST':
        city = City.query.filter_by(idOwner=g.user.idUser).first()
        barracks = Building.query.filter_by(idOwner=g.user.idUser, type=gr.barracks_allocation[u_type]).first()
        error = None
        if city is None:
            error = 'Grad ne postoji'
        elif barracks is None:
            error = 'Nepostojeca baraka!'
        elif barracks.level == 0:
            error = 'Baraka jos nije sagradjena!'
        elif quantity <= 0:
            error = 'Morati regrutuvati pozitivan broj jedinica!'
        else:
            cost = gr.recruit_cost(u_type, quantity)
            gold = cost['gold']
            wood = cost['wood']
            stone = cost['stone']
            population = cost['population']
            if gold > city.gold or wood > city.wood or stone > city.stone or population > city.population:
                error = 'Nedovoljno resursa!'
            if error is None:
                recruit_time = gr.recruit_time_seconds(u_type, quantity, barracks.level)
                recruit_date = datetime.datetime.now() + datetime.timedelta(seconds=recruit_time)
                new_army = Army(idCityFrom=city.idCity, idCityTo=None, status='R', timeToArrival=recruit_date,
                                lakaPesadija=0, teskaPesadija=0, lakaKonjica=0, teskaKonjica=0,
                                strelci=0, samostrelci=0, katapult=0, trebuset=0)
                setattr(new_army, gr.unit_type_fields[u_type], quantity)
                db.session.commit()
                flash(f"Pokrenuto regrutovanje {quantity} jedinica tipa {gr.unit_types[u_type]}")
            else:
                flash(error)
    return redirect(url_for('playercity.player_city'))
