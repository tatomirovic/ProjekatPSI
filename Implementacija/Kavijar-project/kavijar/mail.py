# -*- coding: UTF-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import datetime

from kavijar.auth import login_required, check_ban
from kavijar.models import User, Mailmsg
from . import db

bp = Blueprint('mail', __name__, url_prefix='/mail')


@bp.route('/', methods=('GET', 'POST'))
@login_required
@check_ban
def msg_main():
    g.user.statusUpdate = 0
    msg_list = Mailmsg.query.filter_by(idTo=g.user.idUser).all()
    return render_template('mail/mail.html', msg_list=msg_list)


@bp.route('/send_msg', methods=('GET', 'POST'))
@login_required
@check_ban
def send_msg():
    if request.method == 'POST':
        sender = g.user
        recipient = User.query.filter_by(username=request.form['recipient'])
        msgbody = request.form['body']
        msgtime = datetime.datetime.now()
        error = None
        if recipient is None:
            error = "Nepostojeći korisnik!"
        elif len(msgbody) > 256 or len(msgbody) == 0:
            error = "Losa duzina poruke!"
        if error is None:
            new_message = Mailmsg(idFrom=sender.idUser, idTo=recipient.idUser,
                                  time=msgtime, content=msgbody, readFlag=0)
            db.session.add(new_message)
            db.session.commit()
    return render_template('mail/send_msg.html')


@bp.route('/view_msg/<int:id>')
@login_required
@check_ban
def view_msg(id):
    curr_msg = Mailmsg.query.filter_by(idMail=id).first()
    if curr_msg is not None and curr_msg.idTo != g.user.idUser:
        curr_msg = None
    if curr_msg is not None:
        curr_msg.readFlag = 1
        db.session.commit()
    return render_template('mail/view_msg.html', curr_msg=curr_msg)
