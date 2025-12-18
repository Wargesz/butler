from flask import Blueprint, request
from models.models import Midnight, User

midnight_bp = Blueprint('midnight', __name__)

REQUIRED_FIELDS = ['editor', 'seconds', 'start', 'end', 'api-key', 'file']


@midnight_bp.route('/')
def midnight():
    return "midnight"


@midnight_bp.route('/mno', methods=['POST'])
def midnight_post():
    form = request.form
    if not validMidnight(form):
        return 'wrong parameters', 400
    saveMidnight(form)
    return 'ok'


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
