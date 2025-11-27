from flask import Blueprint, render_template, session, request
from controllers.content import buildVaults
from middleware.auth import auth

vault_bp = Blueprint('vault', __name__)


@vault_bp.route('/')
@auth
def vault():
    public, private = buildVaults(session.get('user'))
    return render_template('vault.html', public=public, private=private)


@vault_bp.route('/file')
@auth
def getFile():
    file = request.args.get('path')
    if file is None:
        return ''
    content = ""
    try:
        with open(f'./content/public/{file}') as f:
            content = f.read()
    except FileNotFoundError:
        return "no file"
    return content
