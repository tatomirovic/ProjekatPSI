from flask import (
    g, redirect, url_for
)
from werkzeug.exceptions import abort
import functools, datetime
from . import eventLogger


##Obavezno koristiti ovaj dekorator pri svakoj modifikaciji tabela city, building, army, trade, recruiting
def update_resources(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        eventLogger.logEvents(g.user, datetime.datetime.now())
        
        return view(**kwargs)

    return wrapped_view
