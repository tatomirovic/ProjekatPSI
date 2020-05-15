# -*- coding: UTF-8 -*-
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kavijar.auth import admin_required, check_ban, mod_required
import datetime;
from . import db;
from .models import User;
bp = Blueprint('mod', __name__, url_prefix='/mod')


@bp.route('/<int:id>/mute', methods=('GET', 'POST'))
@check_ban
@mod_required
def mute_user(id):
    if request.method == 'POST':
        error = None
        user = User.query.filter_by(idUser=id).first()

        if not user:
            error = 'Korisnik ne postoji!'
        elif user.dateCharLift:
            error = 'Korisnik je već banovan sa četa!'
        elif user.role == 'M' or user.role == 'A':
            error = 'Nije moguće banovati admina ili drugog moda sa četa!'

        if error is not None:
            flash(error)
        else:
            bandate = request.args.get('bandate')
            if bandate is None or bandate < datetime.datetime.now():
                bandate = datetime.datetime.now() + datetime.timedelta(hours=1)
                # Podrazumevana duzina čet-bana je jedan sat
            user.dateCharLift = bandate
            db.session.commit()
            flash(f"User {user.username} je banovan sa četa do {bandate}")

    return redirect(url_for('mod.mod_main'))


@bp.route('/', methods=('GET', 'POST'))
@check_ban
@mod_required
def mod_main():
    user_list = User.query.filter(User.idUser != g.user.idUser).all()
    return render_template('mod/mod.html', user_list=user_list)
