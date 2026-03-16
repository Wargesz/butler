from flask import Blueprint, request, render_template, session
from models.models import Midnight, User
from controllers.statements import (getUserActivity, getProjectActivity,
                                    getHeatMap, getUserHeatMap, getEditorData,
                                    getUserWeeklyActivity,
                                    getProjectWeeklyActivity, getScopeData,
                                    getBestMonth, getBestWeek, getBestDay)
from middleware.auth import auth
from datetime import datetime, timedelta

midnight_bp = Blueprint('midnight', __name__)

REQUIRED_FIELDS = ['editor', 'seconds', 'start', 'end', 'api-key', 'file']


@midnight_bp.route('/')
@auth
def midnight():
    user = User.query.filter(User.username == session.get('user')).first()
    firstMidnight = Midnight.query.filter(Midnight.user_id ==
                                          user.id).order_by(Midnight.start_date
                                                            .asc()).first()
    lastMidnight = Midnight.query.filter(Midnight.user_id ==
                                         user.id).order_by(Midnight.start_date
                                                           .desc()).first()
    defaultFrom = (datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d')
    defaultTo = datetime.today().strftime('%Y-%m-%d')
    return render_template('midnight.html',
                           firstMidnight=firstMidnight.start_date.date(),
                           lastMidnight=lastMidnight.end_date.date(),
                           defaultFrom=defaultFrom, defaultTo=defaultTo)


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
    fromDate = request.args.get('from')
    toDate = request.args.get('to')
    if tab == 'calendar' and fromDate and toDate:
        return getCalendarValues(user, fromDate, toDate)
    return 'invalid tab', 400


def getTotalValues(user):
    d = {}
    d['heatmap'] = {'days': {}, 'weeks': {}}
    d['time'] = {}
    d['editor'] = {}
    d['stats'] = {'month': {}, 'week': {}, 'day': {}}
    results = getUserActivity(user)
    for res in results:
        d['time'][res[0]] = res[1]
    results = getUserHeatMap(user)
    for res in results:
        d['heatmap']['days'][res[0]] = res[1]
    results = getUserWeeklyActivity(user)
    for res in results:
        d['heatmap']['weeks'][res[0]] = res[1]
    results = getEditorData(user)
    for res in results:
        d['editor'][res[0]] = res[1]
    results = getBestMonth(user)
    for res in results:
        d['stats']['month'] = f'{res[0]}|{res[1]}'
    results = getBestWeek(user)
    for res in results:
        d['stats']['week'] = f'{res[0]}|{res[1]}'
    results = getBestDay(user)
    for res in results:
        d['stats']['day'] = f'{res[0]}|{res[1]}'
    return d


def getProjectValues(user, project):
    d = {}
    d['heatmap'] = {'days': {}, 'weeks': {}}
    d['time'] = {}
    results = getHeatMap(user, project)
    for res in results:
        d['heatmap']['days'][res[0]] = res[1]
    results = getProjectWeeklyActivity(user, project)
    for res in results:
        d['heatmap']['weeks'][res[0]] = res[1]
    results = getProjectActivity(user, project)
    for res in results:
        d['time'][res[0]] = res[1]
    return d


def getCalendarValues(user, fromDate, toDate):
    d = {}
    results = getScopeData(user, fromDate, toDate)
    for res in results:
        d[res[0]] = res[1]
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
