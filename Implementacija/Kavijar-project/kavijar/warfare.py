#Autor: Konstantin Jaredic

import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from kavijar.auth import player_required, check_ban
from . import db, game_rules as gr, eventLogger
from . import updateWrappers
from .models import City, Building, User, Trade, Army

bp = Blueprint('warfare', __name__, url_prefix='/warfare')


# SANITACIJA INPUTA
def sanitycheck(val):
    try:
        return int(val) >= 0
    except ValueError:
        return False

# SANITACIJA INPUTA
def check_notzeroes(form):
    for k in gr.unit_types.keys():
        if int(form[k]) > 0:
            return True
    return False


# FORMULAR ZA NAPADANJE
@bp.route('/')
@player_required
@check_ban
@updateWrappers.update_resources
def warfare_main():
    city = City.query.filter_by(idOwner=g.user.idUser).first()
    username = request.args.get('username')
    garrison = Army.query.filter_by(idCityFrom=city.idCity, status='G').first()
    if username is None:
        username=''
    return render_template('warfare/warfare.html', username=username, city=city,
                           garrison=garrison)

# Metoda se poziva iz glavne mape kada se naredi napad na grad drugog igraca.
# Metoda ocekuje formular sa poljima za ime igraca koji se napada i broju svakog jedinica koji se salje u napad
# Imena polja za jedinice u formularu treba da prate istu konvenciju kao i u bazi (npr: polje 'LP' : broj lake pesadije)
@bp.route('/attack', methods=('GET', 'POST'))
@player_required
@check_ban
@updateWrappers.update_resources
def attack():
    if request.method == 'POST':
        username = request.form['username']
        # Dohvatamo gradove napadaca i branioca
        attacker = g.user
        defender = User.query.filter_by(username=username).first()
        city_attack = City.query.filter_by(user=attacker).first()
        city_defend = City.query.filter_by(user=defender).first()
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

        # Zabranjujemo slanje bilo kakvog broja jedinica koji nije pozitivan ceo broj barem u jednom polju
        for k in gr.unit_type_fields.keys():
            if not sanitycheck(request.form[k]):
                error = 'Loš format broja jedinica u armiji!'
                break
        if check_notzeroes(request.form) is False:
            error = 'Armija ne sme biti prazna!'

        garrison = Army.query.filter_by(idCityFrom=city_attack.idCity, status='G').first()
        if error is None:
            # Za svaki tip jedinica proveravamo da li ga ima dovoljno u garnizonu. Ako ne, napad nije moguc.
            for k in gr.unit_types.keys():
                if getattr(garrison, gr.unit_type_fields[k]) < int(request.form[k]):
                    error = 'Nedovoljno trupa!'
                    break

        if error is None:
            # Ista funkcija za racunanje vreme putovanja kao i za trgovinu
            arrive_date = datetime.datetime.now() + datetime.timedelta(
                seconds=gr.cityTravelTime_seconds(city_attack, city_defend))
            # Pravimo aktivnu armiju
            new_army = Army(idCityFrom=city_attack.idCity, idCityTo=city_defend.idCity, status='A',
                            timeToArrival=arrive_date)
            for k in gr.unit_type_fields.keys():
                # Uzimamo iz garnizona da bismo napravili tu armiju
                num_units = request.form[k]
                setattr(new_army, gr.unit_type_fields[k], int(num_units))
                setattr(garrison, gr.unit_type_fields[k], getattr(garrison, gr.unit_type_fields[k]) - int(num_units))
            #flash(f'Poslat je napad na {city_defend.user.username}')
            db.session.add(new_army)
            db.session.commit()
        else:
            flash(error)
            return redirect(url_for('warfare.warfare_main'))
    return redirect(url_for('index'))