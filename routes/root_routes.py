from flask import Blueprint, render_template, request, redirect
from random import choice
from sqlalchemy import select
from controllers.db import DB
from models.models import User
import bcrypt


root_bp = Blueprint('root', __name__, template_folder='templates/')


@root_bp.route('/')
def root():
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
    user = DB.execute(select(User.username, User.password).filter(
        User.username == username)).one()
    if user is None:
        return render_template('login.html', error_message='invalid username')
    if bcrypt.checkpw(password.encode('utf-8'),
                      user.password.encode('utf-8')):
        return redirect('/')
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

    user = DB.execute(DB.query(User).filter(User.username == username)).first()
    if user is not None:
        return render_template('register.html', error_message='username taken')
    keys = DB.execute(select(User.api_key)).all()
    DB.add(User(username, hash_password(password), generate_api_key(keys)))
    DB.commit()
    return redirect('/')


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
