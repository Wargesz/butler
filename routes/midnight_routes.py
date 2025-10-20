from flask import Blueprint

midnight_bp = Blueprint('midnight', __name__)


@midnight_bp.route('/')
def midnight():
    return "midnight"
