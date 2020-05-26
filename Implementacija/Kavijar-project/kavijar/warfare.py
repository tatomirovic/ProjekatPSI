import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from kavijar.auth import player_required, check_ban
from . import db, game_rules as gr, eventLogger
from . import updateWrappers
from .models import City, Building, User, Trade, Army

bp = Blueprint('warfare', __name__, url_prefix='/warfare')


def sanitycheck(val):
    try:
        return int(val) >= 0
    except ValueError:
        return False


@bp.route('/')
@player_required
@check_ban
@updateWrappers.update_resources
def attack_form():
    city = City.query.filter_by(idOwner=g.user.idUser).first()
    username = request.args.get('username')
    if username is None:
        username=''
    return render_template('warfare/warfare.html', username=username, city=city)

# Metoda se poziva iz glavne mape kada se naredi napad na grad drugog igraca.
# Metoda ocekuje formular sa poljima za ime igraca koji se napada i broju svakog jedinica koji se salje u napad
# Imena polja za jedinice u formularu treba da prate istu konvenciju kao i u bazi (npr: polje 'LP' : broj lake pesadije)
@player_required
@check_ban
@updateWrappers.update_resources
@bp.route('/attack', methods=('GET', 'POST'))
def attack():
    if request.method == 'POST':
        username = request.form['username']
        # Dohvatamo gradove napadaca i branioca
        attacker = g.user
        defender = User.query.filter_by(username=username).first()
        city_attack = City.query.filter_by(idOwner=attacker.idUser).first()
        city_defend = City.query.filter_by(idOwner=defender.idUser).first()
        error = None
        # Greska ako ijedan grad ne postoji
        if city_attack is None or city_defend is None:
            error = 'Napad mora uključivati dva grada!'
        # Dozvoljavamo samo jednu armiju poslatu ka jednom gradu u datom trenutku
        elif Army.query.filter_by(idCityFrom=city_attack.idCity, idCityTo=city_defend.idCity).first() is not None:
            error = 'Već napadate ovaj grad!'
        # Zabranjujemo gradjanski rat
        elif city_attack.idCity == city_defend.idCity:
            error = 'Ne možete napasti samog sebe!'
        # Zabranjujemo slanje bilo kakvog broja jedinica koji nije pozitivan ceo broj
        for k in gr.unit_type_fields.keys():
            if not sanitycheck(request.form[k]):
                error = 'Loš format broja jedinica u armiji!'
                break
        garrison = Army.query.filter_by(idCityFrom=city_attack.idCity, status='G')
        if error is None:
            # Za svaki tip jedinica proveravamo da li ga ima dovoljno u garnizonu. Ako ne, napad nije moguc.
            for k in gr.unit_types.values():
                if getattr(garrison, k) < int(request.form[k]):
                    error = 'Nedovljno trupa!'
                    break

        if error is None:
            # Ista funkcija za racunanje vreme putovanja kao i za trgovinu
            arrive_date = datetime.datetime.now() + datetime.timedelta(
                seconds=gr.cityTravelTime_seconds(city_attack, city_defend))
            # Pravimo aktivnu armiju
            new_army = Army(idCityFrom=city_attack.idCity, idCityTo=city_defend.idCity, status='A',
                            timeToArrival=arrive_date)
            for k in gr.unit_type_fields.values():
                # Uzimamo iz garnizona da bismo napravili tu armiju
                num_units = request.form[k]
                setattr(new_army, k, num_units)
                setattr(garrison, k, getattr(garrison, k) - num_units)
            db.session.add(new_army)
            db.session.commit()
        else:
            flash(error)
    return redirect(url_for('index'))