from flask import Blueprint, render_template, request, redirect
from models.models import User
from sqlalchemy import select, insert
from random import choice
import bcrypt

root_bp = Blueprint('root', __name__, template_folder='../templates/')


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
    conn = get_engine().connect()
    stmt = select(User).where(User.username == username)
    user = conn.execute(stmt).fetchone()
    conn.close()
    if user is None:
        return render_template('login.html', error_message='invalid username')
    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
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

    stmt = select(User.id).where(User.username == username)
    conn = get_engine().connect()
    res = conn.execute(stmt).fetchone()
    if res is not None:
        return render_template('register.html', error_message='username taken')

    hashed_password = hash_password(password)
    api_key = generate_api_key(conn.execute(
        select(User.api_key)
        ).fetchall())
    stmt = insert(User).values(username=username,
                               password=hashed_password,
                               api_key=api_key)
    conn.execute(stmt)
    conn.commit()
    conn.close()
    return redirect('/')


def generate_api_key(keys):
    c = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    key = ''
    for _ in range(64):
        key += choice(c)
    while key in keys:
        key = ''
        for _ in range(64):
            key += choice(c)
    return key


def hash_password(plain_password):
    b = plain_password.encode('utf-8')
    hash = bcrypt.hashpw(b, bcrypt.gensalt())
    return hash.decode('utf-8')
