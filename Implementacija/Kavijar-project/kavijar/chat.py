# -*- coding: UTF-8 -*-
import click
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


@bp.route('/')
@login_required
def sessions():
    recent_messages = Chatmsg.query.order_by(desc(Chatmsg.time)).limit(15).all()
    return render_template('chat/chat.html', recent_messages=recent_messages)

def message_received(methods=['GET', 'POST']):
    #click.echo(f'User name is: {g.user.username}')
    pass


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    if session['user_id']:
        new_msg = Chatmsg(idSender=session['user_od'], time=datetime.datetime.now(), content=json.message)
        db.session.add(new_msg)
        db.session.commit()
        socketio.emit('my response', json, callback=message_received)






