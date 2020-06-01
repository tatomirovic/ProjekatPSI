from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import functools, datetime
from . import db, game_rules as gr

# Metoda kojom se pokrece upgrade proces.
def upgrade_building_function(building, use_resources=True, gold=0, wood=0, stone=0):
    b_type = building.type
    upgrade_level = min(building.level + 1, gr.building_max_level)
    finishTime = datetime.datetime.now() \
                 + datetime.timedelta(minutes=gr.build_time(upgrade_level, b_type))
    # existing_building.level += 1
    building.finishTime = finishTime
    building.status = 'U'
    if use_resources:
        gr.adjust_resources(player=g.user, gold=gold, wood=wood, stone=stone, debug=True, context='Upgrade Building')
    db.session.commit()