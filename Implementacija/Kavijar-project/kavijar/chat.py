# -*- coding: UTF-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import datetime
from flask_socketio import SocketIO

from kavijar.auth import login_required, check_ban
from kavijar.models import User, Mailmsg
from . import db, socketio

bp = Blueprint('chat', __name__, url_prefix='/chat')


@bp.route('/')
def sessions():
    return render_template('chat/chat.html')

def message_received(methods=['GET', 'POST']):
    #print('message was received!!!')

    pass


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    #print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=message_received)






