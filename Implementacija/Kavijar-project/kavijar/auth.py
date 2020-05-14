import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import db;
from .models import User;

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        error = None
        username = request.form['username']
        password = request.form['password']
        rolePageDict = {
            'I': url_for('index'),
            'M': url_for('mod'),
            'A': url_for('admin')
        }

        if (request.form['loginuser'] != 'Registruj se'):
            user = User.query.filter_by(username=username).first()
            if user is None:
                error = 'Pogrešno korisničko ime.'
            elif not check_password_hash(user.password, password):
                error = 'Pogrešna lozinka.'
            if error is None:
                session.clear()
                session['user_id'] = user.idUser;
                return redirect(rolePageDict[user.role])
        else:
            error = None
            if not username:
                error = 'Korisničko ime ne sme biti prazno.'
            elif not password:
                error = 'Lozinka ne sme biti prazna.'
            elif User.query.filter_by(username=username).first():
                error = 'Korisnik sa tim imenom već postoji.'

            if error is None:
                new_user = User(username=username, password=generate_password_hash(password), role='I',
                                caviar=0, statusUpdate=0, dateUnban=None, dateCharLift=None)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('auth.login'))

            flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(idUser=user_id).first()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        elif g.user.dateUnban is not None:
            error = "Banovani ste!"
            flash(error)
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
