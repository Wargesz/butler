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


@vault_bp.route('/file', methods=['GET'])
@auth
def getFile():
    j = {}
    j['file'] = request.args.get('path')
    if j['file'] is None:
        return 'missing path param'
    if not validFile(j['file']):
        return 'invalid path', 400
    j['scope'] = request.args.get('scope')
    if j['scope'] is None:
        return 'missing scope param', 400
    j['content'], status = loadFileFromScope(j['scope'], j['file'])
    j['owner'] = getUserFromPath(j['file']) == session.get('user')
    j['scope'] = j['scope']
    if request.accept_mimetypes.accept_json:
        return dumps(j)
    return j['content'], status


@vault_bp.route('/file', methods=['POST'])
@auth
def updateFile():
    if not request.form.get('scope'):
        return 'scope not specified', 400
    if not request.form.get('path'):
        return 'path not specified', 400
    if not request.form.get('content'):
        return 'content not specified', 400
    scope = request.form.get('scope')
    path = request.form.get('path')
    content = request.form.get('content')
    user = session.get('user')
    if user != getUserFromPath(path):
        return 'cannot save changes', 403
    if scope != 'public' and scope != 'private':
        return 'invalid scope', 400
    file = secure_filename(path.split('/')[-1])
    path = secure_filename(path.removesuffix(file)).replace('_', '/')
    complete_path = f'content/{scope}/{path}/{file}'
    with open(complete_path, 'w') as f:
        f.write(content)
    return 'file successfully updated', 201


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
    filename = secure_filename(file.split('/')[-1])
    path = secure_filename(file.removesuffix(filename)).replace('_', '/')
    if scope == 'private':
        username = session.get('user')
        if username not in file.split('/')[0]:
            return 'no file'
    content = ''
    try:
        with open(f'./content/{scope}/{path}/{filename}') as f:
            content = f.read()
    except FileNotFoundError:
        return 'no file', 404
    return content, 200


def validFile(file):
    # user-{username}/*/{filename}.{type}
    file = secure_filename(file)
    return file.startswith('user-') and '.' in file


def getUserFromPath(path):
    path = secure_filename(path)
    return path.split('user-')[1].split('_')[0]
