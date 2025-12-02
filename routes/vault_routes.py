from flask import Blueprint, render_template, session, request, redirect
from controllers.content import buildVaults, getAllPathsOfUser
from middleware.auth import auth
from json import dumps
from werkzeug.utils import secure_filename
import os

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
    j['owner'] = getUserFromPath(j['file']) == session.get('user')
    j['scope'] = j['scope']
    if request.accept_mimetypes.accept_json:
        return dumps(j)
    return j['content']


@vault_bp.route('/upload', methods=['POST'])
@auth
def upload():
    if 'path' not in request.form:
        return 'no path specified', 400
    scope, path = request.form['path'].split(':')
    scope = scope.lower()
    user = session.get('user')
    if 'files' not in request.files:
        return 'no file part', 400
    if request.files.getlist('files')[0].filename == '':
        return 'no file specified', 400
    for file in request.files.getlist('files'):
        os.makedirs(os.path.dirname(f'content/{scope}/user-{user}/{path}'),
                    exist_ok=True)
        file.save(os.path.join(f'content/{scope}/user-{user}/{path}',
                               secure_filename(file.filename)))
    return redirect('/vault', 301)


@vault_bp.route('/paths', methods=['GET'])
@auth
def paths():
    if not request.accept_mimetypes.accept_json:
        return 'only application/json is allowed', 415
    return dumps(getAllPathsOfUser(session.get('user')))


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
