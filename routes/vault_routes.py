from flask import Blueprint, render_template, session, request
from controllers.content import buildVaults
from middleware.auth import auth
from json import dumps

vault_bp = Blueprint('vault', __name__)


@vault_bp.route('/')
@auth
def vault():
    public, private = buildVaults(session.get('user'))
    return render_template('vault.html', public=public, private=private)


@vault_bp.route('/file')
@auth
def getFile():
    j = {}
    j['file'] = request.args.get('path')
    if j['file'] is None:
        return 'missing path param'
    j['scope'] = request.args.get('scope')
    if j['scope'] is None:
        return 'missing scope param'
    j['content'] = loadFileFromScope(j['scope'],
                                     j['file'])
    j['owner'] = getUserFromPath(j['file'])
    j['scope'] = j['scope']
    if request.accept_mimetypes.accept_json:
        return dumps(j)
    return j['content']


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


def getUserFromPath(path):
    return path.split('/')[0].split('user-')[1]
