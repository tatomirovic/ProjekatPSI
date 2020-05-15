# -*- coding: UTF-8 -*-
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kavijar.auth import admin_required, check_ban
import datetime;
from . import db;
from .models import User;
bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/<int:id>/ban', methods=('GET', 'POST'))
@admin_required
def banuser(id):
    if request.method == 'POST':
        error = None
        user = User.query.filter_by(idUser=id).first()

        if not user:
            error = 'Korisnik ne postoji!'
        elif user.dateUnban:
            error = 'Korisnik je već banovan!'
        elif user.role == 'A':
            error = 'Nije moguće banovati admina!'

        if error is not None:
            flash(error)
        else:
            bandate = request.args.get('bandate')
            if bandate is None or bandate < datetime.datetime.now():
                bandate = datetime.datetime.now() + datetime.timedelta(days=1)
                # Podrazumevana duzina bana je jedan dan
            user.dateUnban = bandate
            db.session.commit()
            flash(f"User {user.username} je banovan do {bandate}")

    return redirect(url_for('admin.admin_main'))


@bp.route('/', methods=('GET', 'POST'))
@check_ban
@admin_required
def admin_main():
    user_list = User.query.filter(User.idUser != g.user.idUser).all()
    return render_template('admin/admin.html', user_list=user_list, admin_name=g.user.username)
