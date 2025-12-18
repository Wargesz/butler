from flask import (
        Blueprint, render_template, session, request, redirect,
        url_for)
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
        return dumps(j), status
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
    file, path = unpackPath(path)
    complete_path = f'content/{scope}/{path}/{file}'
    with open(complete_path, 'w') as f:
        f.write(content)
    return 'file successfully updated', 201


@vault_bp.route('/file', methods=['PUT'])
@auth
def createFile():
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
    path = f'user-{user}{path}'
    if scope != 'public' and scope != 'private':
        return 'invalid scope', 400
    file, path = unpackPath(path)
    complete_path = f'content/{scope}/{path}/{file}'
    with open(complete_path, 'w') as f:
        f.write(content)
    return 'file successfully updated', 201


@vault_bp.route('/file', methods=['DELETE'])
@auth
def deleteFile():
    path = request.args.get('path')
    if path is None:
        return 'no path specified', 400
    if not validFile(path):
        return 'invalid path', 400
    user = getUserFromPath(path)
    if user != session.get('user'):
        return 'cannot delete file', 403
    scope = request.args.get('scope')
    if scope not in ['private', 'public']:
        return 'wrong path specified', 400
    file, path = unpackPath(path)
    try:
        os.remove(os.path.join('.', 'content', scope, path, file))
    except FileNotFoundError:
        return 'invalid file specified', 400
    deleteDirIfEmpty(scope, path)
    return 'file deleted', 200


@vault_bp.route('/upload', methods=['POST'])
@auth
def upload():
    if 'path' not in request.form:
        return 'no path specified', 400
    scope, path = request.form['path'].split(':')
    scope = scope.lower()
    _, path = unpackPath(path)
    if scope not in ['public', 'private']:
        return 'wrong scope specified', 400
    user = session.get('user')
    if 'files' not in request.files:
        return 'no file part', 400
    if request.files.getlist('files')[0].filename == '':
        return 'no file specified', 400
    folder = request.form['folder']
    if folder != '':
        if containsForbiddenCharacter(folder):
            return 'folder name may not contain special characters', 400
        folder = f'{secure_filename(folder)}/'
    for file in request.files.getlist('files'):
        if '.' not in file.filename:
            return 'filename is invalid'
    for file in request.files.getlist('files'):
        os.makedirs(os.path.dirname(
            f'content/{scope}/user-{user}/{path}/{folder}'),
                    exist_ok=True)
        file.save(os.path.join(f'content/{scope}/user-{user}/{path}/{folder}',
                               secure_filename(file.filename)))
    return redirect(url_for('vault.vault'), 301)


@vault_bp.route('/paths', methods=['GET'])
@auth
def paths():
    if not request.accept_mimetypes.accept_json:
        return 'only application/json is allowed', 415
    return dumps(getAllPathsOfUser(session.get('user')))


def loadFileFromScope(scope, file):
    # file = user-bob/asd
    filename, path = unpackPath(file)
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


def unpackPath(path):
    file = ''
    if '.' in path:
        file = secure_filename(path.split('/')[-1])
    path = secure_filename(path.removesuffix(file)).replace('_', '/')
    return file, path


def deleteDirIfEmpty(scope, path):
    full_path = os.path.join('.', 'content', scope, path)
    for _, dirs, files in os.walk(full_path):
        if not dirs and not files:
            os.removedirs(full_path)


def validFile(file):
    # user-{username}/*/{filename}.{type}
    file = secure_filename(file)
    return file.startswith('user-') and '.' in file


def containsForbiddenCharacter(s):
    return any(not c.isalnum() for c in s)


def getUserFromPath(path):
    path = secure_filename(path)
    return path.split('user-')[1].split('_')[0]
