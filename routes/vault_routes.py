from flask import Blueprint, render_template

vault_bp = Blueprint('vault', __name__)


@vault_bp.route('/')
def vault():
    return render_template('vault.html')
