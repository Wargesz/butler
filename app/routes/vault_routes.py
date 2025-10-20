from flask import Blueprint

vault_bp = Blueprint('vault', __name__)


@vault_bp.route('/')
def vault():
    return "vault"
