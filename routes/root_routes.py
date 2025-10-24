from flask import Blueprint, render_template, request, redirect, session
from dotenv import dotenv_values
from random import choice
from controllers.db import DB
from models.models import User
from middleware.auth import auth
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt

env = dotenv_values('.env')


root_bp = Blueprint('root', __name__, template_folder='templates/')


@root_bp.route('/')
@auth
def root():
    print(f'authed: {session.get('user')}')
    return render_template('index.html')


@root_bp.route('/login', methods=['GET'])
def get_login():
    return render_template('login.html')


@root_bp.route('/login', methods=['POST'])
def post_login():
    username = request.form['username']
    if username == "":
        return render_template('login.html', error_message='no username \
                provided')

    password = request.form['password']
    if password == "":
        return render_template('login.html', error_message='no password \
                provided')
    user = User.query.filter(username == username).first()
    if user is None:
        return render_template('login.html', error_message='invalid username')
    if bcrypt.checkpw(password.encode('utf-8'),
                      user.password.encode('utf-8')):

        res = redirect('/')
        res.set_cookie('Authorize', signCookie(user))
        return res
    else:
        return render_template('login.html', error_message='invalid password')


@root_bp.route('/register', methods=['GET'])
def get_register():
    return render_template('register.html')


@root_bp.route('/register', methods=['POST'])
def post_register():
    username = request.form['username']
    if username == "":
        return render_template('register.html', error_message='no username \
                provided')

    password = request.form['password']
    if password == "":
        return render_template('register.html', error_message='no password \
                provided')
    user = User.query.filter(User.username == username).first()
    if user is not None:
        return render_template('register.html', error_message='username taken')
    keys = User.query.with_entities(User.api_key).all()
    DB.add(User(username, hash_password(password), generate_api_key(keys)))
    DB.commit()
    res = redirect('/')
    res.set_cookie('Authorize', signCookie(user))
    return res


def generate_api_key(keys):
    c = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    key = ''
    for _ in range(64):
        key += choice(c)
    while key in keys:
        print('generated existing key')
        key = ''
        for _ in range(64):
            key += choice(c)
    return key


def hash_password(plain_password):
    b = plain_password.encode('utf-8')
    hash = bcrypt.hashpw(b, bcrypt.gensalt())
    return hash.decode('utf-8')


def signCookie(user):
    token = jwt.encode({"sub": str(user.id), "exp": datetime.now(tz=timezone.utc) +
                        timedelta(days=3)}, env['SECRET'], algorithm="HS256")
    return token
