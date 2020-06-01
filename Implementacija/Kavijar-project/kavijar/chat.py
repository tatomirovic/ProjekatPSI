# -*- coding: UTF-8 -*-
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import datetime;
from flask_socketio import SocketIO
from sqlalchemy import desc

from kavijar.auth import login_required, check_ban
from kavijar.models import User, Chatmsg
from . import db, socketio

bp = Blueprint('chat', __name__, url_prefix='/chat')


# Glavna chat stranica - prikazujemo zadnjih 15 poruka
@bp.route('/')
@login_required
@check_ban
def sessions():
    recent_messages = (Chatmsg.query.order_by(desc(Chatmsg.time)).limit(15).all())[::-1]
    #print(f"MSG IS {recent_messages[1].content}")
    return render_template('chat/chat.html', recent_messages=recent_messages)


# Callback metoda, koriscena pri debuggovanju
def message_received(methods=['GET', 'POST']):
    #print('message was received!!!')
    # click.echo(f'User name is: {g.user.username}')
    pass


# Event handler za interakciju sa klijentskim jsom
@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    sender = User.query.filter_by(idUser=session['user_id']).first()
    if sender is None:
        return

    #print('received my event: ' + str(json))

    if sender.dateCharLift is not None and sender.dateCharLift <= datetime.datetime.now():
        sender.dateCharLift = None
        db.session.commit()

    if sender.dateCharLift is None and json['message'] and len(json['message']) > 0:
        # print(f"JSO is: {json}")
        new_msg = Chatmsg(idSender=session['user_id'], time=datetime.datetime.now(), content=json['message'])
        db.session.add(new_msg)
        db.session.commit()
        socketio.emit('my response', json, callback=message_received)
    else:
        if sender.dateCharLift is not None:
            json['user_name'] = ''
            json['message'] = 'Banovani ste sa četa!'
            socketio.emit('my response', json, callback=message_received)
