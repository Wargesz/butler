from flask import Blueprint, request, render_template, session
from models.models import Midnight, User
from controllers.statements import (getUserActivity, getProjectActivity,
                                    getHeatMap, getUserHeatMap, getEditorData)
from middleware.auth import auth
from json import dumps

midnight_bp = Blueprint('midnight', __name__)

REQUIRED_FIELDS = ['editor', 'seconds', 'start', 'end', 'api-key', 'file']


@midnight_bp.route('/')
@auth
def midnight():
    return render_template('midnight.html')


@midnight_bp.route('/mno', methods=['POST'])
def midnight_post():
    form = request.form
    if not validMidnight(form):
        return 'wrong parameters', 400
    saveMidnight(form)
    return 'ok'


@midnight_bp.route('/activity', methods=['GET'])
@auth
def activity():
    tab = request.args.get('tab')
    if not tab:
        return 'tab not specified'
    user = session.get('user')
    if tab == 'total':
        return getTotalValues(user)
    project = request.args.get('project')
    if tab == 'project' and project:
        return getProjectValues(user, project)
    return 'invalid tab', 400


def getTotalValues(user):
    d = {}
    d['heatmap'] = {}
    d['time'] = {}
    d['editor'] = {}
    results = getUserActivity(user)
    for res in results:
        d['time'][res[0]] = res[1]
    results = getUserHeatMap(user)
    for res in results:
        d['heatmap'][res[0]] = res[1]
    results = getEditorData(user)
    for res in results:
        d['editor'][res[0]] = res[1]
    return d


def getProjectValues(user, project):
    d = {}
    d['heatmap'] = {}
    d['time'] = {}
    results = getHeatMap(user, project)
    for res in results:
        d['heatmap'][res[0]] = res[1]
    results = getProjectActivity(user, project)
    for res in results:
        d['time'][res[0]] = res[1]
    return d


def validMidnight(form):
    if len(form) != len(REQUIRED_FIELDS):
        return False
    for field in REQUIRED_FIELDS:
        if form[field] is None:
            return False
    user = User.query.filter(User.api_key == form['api-key']).first()
    if user is None:
        return False
    return True


def saveMidnight(form):
    user = User.query.filter(User.api_key == form['api-key']).first()
    midnight = Midnight(editor=form['editor'], seconds=form['seconds'],
                        start=form['start'], end=form['end'],
                        file=form['file'], user=user)
    midnight.save()
