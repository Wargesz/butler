from flask import Blueprint, request, render_template, session
from models.models import Midnight, User
from controllers.statements import getUserActivity
from json import dumps

midnight_bp = Blueprint('midnight', __name__)

REQUIRED_FIELDS = ['editor', 'seconds', 'start', 'end', 'api-key', 'file']


@midnight_bp.route('/')
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
def activity():
    d = {}
    user = session.get('user')
    results = getUserActivity(user)
    for res in results:
        d[res[0]] = res[1]
    return dumps(d)


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
