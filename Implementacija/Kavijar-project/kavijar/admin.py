# -*- coding: UTF-8 -*-
import click
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

from kavijar.auth import admin_required, check_ban
import datetime
from . import db
from .models import User
bp = Blueprint('admin', __name__, url_prefix='/admin')


# Metoda kojom admin banuje korisnika. Ide preko formulara.
@bp.route('/ban', methods=('GET', 'POST'))
@admin_required
def ban_user():
    if request.method == 'POST':
        error = None
        username = request.form['banUsername']
        user = User.query.filter_by(username=username).first()

        if not user:
            error = 'Korisnik ne postoji!'
        elif user.dateUnban:
            error = 'Korisnik je već banovan!'
        elif user.role == 'A':
            error = 'Nije moguće banovati admina!'

        if error is not None:
            flash(error)
        else:
            banDateStr = request.form['banDate']
            bandate = datetime.datetime.strptime(banDateStr, '%Y-%m-%d')
            #click.echo(f"The bandate is: {bandate}")
            if bandate is None or bandate < datetime.datetime.now():
                bandate = datetime.datetime.now() + datetime.timedelta(days=1)
                # Podrazumevana duzina bana je jedan dan
            user.dateUnban = bandate
            db.session.commit()
            flash(f"User {user.username} je banovan do {bandate}")

    return redirect(url_for('admin.admin_main'))


# Admin homepage
@bp.route('/', methods=('GET', 'POST'))
@admin_required
def admin_main():
    user_list = User.query.filter(User.idUser != g.user.idUser).all()
    return render_template('admin/admin.html', user_list=user_list)


# Metoda kojom admina kreira novog moda. Ide preko formulara.
@bp.route('/create_mod', methods=('GET', 'POST'))
@admin_required
def create_mod():
    if request.method == 'POST':
        error = None
        username = request.form['username']
        password = request.form['password']
        # Metoda se zove nakon sto se popuni formular - slicno stranici register
        error = None
        if not username:
            error = 'Korisničko ime ne sme biti prazno.'
        elif not password:
            error = 'Lozinka ne sme biti prazna.'
        elif User.query.filter_by(username=username).first():
            error = 'Korisnik sa tim imenom već postoji.'

        if error is None:
            new_user = User(username=username, password=generate_password_hash(password), role='M',
                            caviar=0, statusUpdate=0, dateUnban=None, dateCharLift=None)
            db.session.add(new_user)
            db.session.commit()
            flash(f"Mod sa username {username} je kreiran")
        else:
            flash(error)
        return redirect(url_for('admin.admin_main'))