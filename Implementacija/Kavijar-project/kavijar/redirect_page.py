# -*- coding: UTF-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from kavijar.auth import login_required

bp = Blueprint('redirect_page', __name__, url_prefix='/redirect')


@bp.route('/')
@login_required
def redirect_page():
    rolePageDict = {
        'I': url_for('index'),
        'M': url_for('mod.mod_main'),
        'A': url_for('admin.admin_main')
    }
    return redirect(rolePageDict[g.user.role])
