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
        return 'missing path param'
    scope = request.args.get('scope')
    if scope is None:
        return 'missing score param'
    content = loadFileFromScope(scope, file)
    return content


def loadFileFromScope(scope, file):
    # file = user-bob/asd
    if scope == 'private':
        username = session.get('user')
        if username not in file.split('/')[0]:
            return 'no file'
    content = ''
    try:
        with open(f'./content/{scope}/{file}') as f:
            content = f.read()
    except FileNotFoundError:
        return 'no file'
    return content
