import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from kavijar.auth import player_required, check_ban
from . import db, game_rules as gr, eventLogger
from . import updateWrappers
from .models import City, Building, User, Trade

bp = Blueprint('tradingpost', __name__, url_prefix='/tradingpost')


def sanitycheck(val):
    try:
        return int(val) >= 0
    except ValueError:
        return False

@bp.route('/trade')
@player_required
@check_ban
@updateWrappers.update_resources
def trade_main():
    city = City.query.filter_by(idOwner=g.user.idUser).first()
    username = request.args.get('username')
    if username is None:
        username=''
    return render_template('tradingpost/trade.html', username=username, city=city)



# Ovo je metoda koja generise templejt za podstranu trgovinske stanice. Ovoj strani se pristupa iz gradskog menija.
@bp.route('/', methods=('GET', 'POST'))
@player_required
@check_ban
@updateWrappers.update_resources
def trading_post():
    city = City.query.filter_by(idOwner=g.user.idUser).first()
    trades_sent_data = []
    trades_received_data = []
    if city is not None:
        # Sve ponude koje smo poslali
        trades_sent = Trade.query.filter_by(idCity1=city.idCity, status='P').all()
        # Sve ponude koje su nam stigle
        trades_received = Trade.query.filter_by(idCity2=city.idCity, status='P').all()
        print(f'SENTDATA: {trades_sent}')
        print(f'RECDATA: {trades_received}')
        userCity = City.query.filter_by(idOwner=g.user.idUser).first()
        citySend = userCity
        for trade in trades_sent:
            cityReceive = City.query.filter_by(idCity=Trade.idCity2).first()
            # Json reprezentacija ponude
            test = trade.gold2
            data = trade.serialize()
            # Dodato u json data imamo i imena gradova
            data['sendName'] = citySend.name
            data['receiveName'] = cityReceive.name
            trades_sent_data.append(data)
        cityReceive = userCity
        for trade in trades_received:
            citySend = City.query.filter_by(idCity=Trade.idCity1)
            # Json reprezentacija ponude
            data = trade.serialize()
            # Dodato u json data imamo i imena gradova
            data['sendName'] = citySend.name
            data['receiveName'] = cityReceive.name
            trades_received_data.append(data)
    return render_template('building/buildingTS.html', trades_sent=trades_sent_data,
                           trades_received=trades_received_data, city=city)


# Ova metoda se poziva kada korisnik kreira i salje ponudu drugom gradu. Ocekuje formular sa imenom igraca (NE GRADA)
# kom se salje ponuda, kao i resursima koji se nude i traze. Imena polja prate iste konvencije kao u bazi podataka (
# username, gold1, wood1...)
@bp.route('/create_trade', methods=('GET', 'POST'))
@player_required
@check_ban
@updateWrappers.update_resources
def create_trade():
    if request.method == 'POST':
        username = request.form['username']
        sender = g.user
        receiver = User.query.filter_by(username=username).first()
        city_send = City.query.filter_by(idOwner=sender.idUser).first()
        city_receive = City.query.filter_by(idOwner=receiver.idUser).first()
        tpost_send = Building.query.filter_by(idCity=city_send.idCity, type='TS').first()
        tpost_receive = Building.query.filter_by(idCity=city_receive.idCity, type='TS').first()
        error = None
        if city_send is None or city_receive is None:
            error = 'Transakcija mora uključivati dva grada!'
        elif tpost_send is None or tpost_receive is None:
            error = 'Oba grada moraju imati trgovinsku stanicu!'
        elif Trade.query.filter_by(idCity1=city_send.idCity, idCity2=city_receive.idCity).first() is not None:
            error = 'Već ste poslali ponudu ovom gradu!'
        elif city_send.idCity == city_receive.idCity:
            error = 'Ne možete poslati ponudu samom sebi!'
        else:
            res1 = {'gold': request.form['gold1'], 'wood': request.form['wood1'], 'stone': request.form['stone1']}
            res2 = {'gold': request.form['gold2'], 'wood': request.form['wood2'], 'stone': request.form['stone2']}
            for x in list(res1.values()) + list(res2.values()):
                if not sanitycheck(x):
                    error = 'Loš format resursa!'
                    break
            if error is None:
                # Ako igrac ima suvise slabu trgovinsku stanicu, ogranici mu resurse koji se salju u jednoj ponudi.
                trade_cap = gr.tp_resource_cap[tpost_send.level]
                for k in res1.keys():
                    res1[k] = min(int(res1[k]), trade_cap)
                for k in res2.keys():
                    res2[k] = min(int(res2[k]), trade_cap)
                # Obavesti igraca ako pokusava da salje vise nego sto ima
                if res1['gold'] > city_send.gold or res1['wood'] > city_send.wood or res1['stone'] > city_send.stone:
                    error = 'Nemate dovoljno resursa!'

        if error is None:
            # Pravimo ponudu i trpamo je u bazu
            new_trade = Trade(idCity1=city_send.idCity, idCity2=city_receive.idCity,
                              status='P', gold1=res1['gold'], wood1=res1['wood'], stone1=res1['stone'],
                              gold2=res2['gold'], wood2=res2['wood'], stone2=res2['stone'],
                              timeToArrival=None)
            db.session.add(new_trade)
            db.session.commit()
            flash(f"Poslali ste ponudu gradu {city_receive.name} igrača {username}")
        else:
            flash(error)
    return redirect(url_for('tradingpost.trading_post'))


# Ova metoda se poziva kada igrac zatrazi ponistavanje ponude koju je poslao.
@bp.route('/cancel_trade/<int:idTrade>', methods=('GET', 'POST'))
@player_required
@check_ban
@updateWrappers.update_resources
def cancel_trade(idTrade):
    if request.method == 'POST':
        trade = Trade.query.filter_by(idTrade=idTrade)
        city_send = City.query.filter_by(idOwner=trade.idCity1).first()
        city_receive = City.query.filter_by(idCity=trade.idCity2).first()
        tpost = Building.query.filter_by(idCity=city_send.idCity, type='TP').first()
        error = None
        if city_send is None or city_receive is None:
            error = 'Transakcija mora uključivati dva grada!'
        elif city_send.idOwner != g.user.idUser:
            error = 'Niste ovlašćeni da poništite ovu ponudu!'
        elif tpost is None:
            error = 'Nemate trgovinsku stanicu!'
        elif trade.status != 'P':
            error = 'Transakcija je već obradjena!'
        if error is None:
            receiver = User.query.filter_by(idUser=city_receive.idOwner).first()
            flash(f"Otkazali ste ponudu ka gradu {city_receive.name} igrača {receiver.username}")
            db.session.delete(trade)
            db.session.commit()
        else:
            flash(error)
    return redirect(url_for('tradingpost.trading_post'))


# Metoda se poziva kada igrac prihvati ponudu koja mu je stigla. Ponuda se postavlja na aktivni status i bice obradjena
# od strane event handlera, a u medjuvremenu se suspenduju resursi koji ucestvuju.
@bp.route('/accept_trade/<int:idTrade>', methods=('GET', 'POST'))
@player_required
@check_ban
@updateWrappers.update_resources
def accept_trade(idTrade):
    if request.method == 'POST':
        trade = Trade.query.filter_by(idTrade=idTrade).first()
        city_send = City.query.filter_by(idOwner=trade.idCity1).first()
        city_receive = City.query.filter_by(idOwner=trade.idCity2).first()
        tpost = Building.query.filter_by(idCity=city_receive.idCity, type='TP').first()
        error = None
        if city_receive is None:
            error = 'Nemate grad'
        elif city_receive.idOwner != g.user.idUser:
            error = 'Niste ovlašćeni da odbijete ovu ponudu'
        elif city_send is None:
            error = 'Nepostojeći grad je poslao ponudu'
        elif tpost is None:
            error = 'Nemate trgovinsku stanicu!'
        elif trade.gold1 > city_send.gold or trade.wood1 > city_send.wood or trade.stone1 > city_send.stone:
            error = 'Pošiljalac nema dovoljno resursa!'
        elif trade.gold2 > city_receive.gold or trade.wood2 > city_receive.wood or trade.stone2 > city_receive.stone:
            error = 'Nemate dovoljno resursa!'
        if error is None:
            sender = User.query.filter_by(idUser=city_send.idOwner).first()
            receiver = g.user
            trade.timeToArrival = datetime.datetime.now() + datetime.timedelta(
                seconds=gr.cityTravelTime_seconds(city_send, city_receive))
            trade.status = 'A'
            gr.adjust_resources(player=sender, gold=-trade.gold1,
                                wood=-trade.wood1, stone=-trade.stone1)
            gr.adjust_resources(player=receiver, gold=-trade.gold2,
                                wood=-trade.wood2, stone=-trade.stone2)
            db.session.commit()
            flash(f"Prihvatili ste ponudu od grada {city_send.name} igrača {sender.username}")
        else:
            flash(error)
    return redirect(url_for('tradingpost.trading_post'))


# Metoda se poziva kada igrac odbija ponudu koja mu je stigla.
# Ponuda se brise iz baze i posiljaocu se vracaju suspendovani resursi.
@bp.route('/reject_trade/<int:idTrade>', methods=('GET', 'POST'))
@player_required
@check_ban
@updateWrappers.update_resources
def reject_trade(idTrade):
    if request.method == 'POST':
        trade = Trade.query.filter_by(idTrade=idTrade).first()
        city_send = City.query.filter_by(idOwner=trade.idCity1).first()
        city_receive = City.query.filter_by(idOwner=trade.idCity2).first()
        tpost = Building.query.filter_by(idCity=city_receive.idCity, type='TP').first()
        error = None
        if city_receive is None:
            error = 'Nemate grad'
        elif city_receive.idOwner != g.user.idUser:
            error = 'Niste ovlašćeni da odbijete ovu ponudu'
        elif city_send is None:
            error = 'Nepostojeći grad je poslao ponudu'
        elif tpost is None:
            error = 'Nemate trgovinsku stanicu!'
        elif trade.status != 'P':
            error = 'Transakcija je već obradjena!'
        if error is None:
            sender = User.query.filter_by(idUser=city_send.idOwner).first()
            flash(f"Odbili ste ponudu od grada {city_send.name} igrača {sender.username}")
            db.session.delete(trade)
            db.session.commit()
        else:
            flash(error)
    return redirect(url_for('tradingpost.trading_post'))
