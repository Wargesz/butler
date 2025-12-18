from flask import request, redirect, session, url_for
from dotenv import dotenv_values
from jwt import decode, ExpiredSignatureError
from models.models import User

env = dotenv_values(".env")


def auth(f):
    def wrap(*args, **kwargs):
        token = request.cookies.get('Authorize')
        if token is None:
            return redirect(url_for('root.get_login'))
        try:
            claims = decode(token, env['SECRET'], algorithms=["HS256"])
            user = User.query.filter(User.id == claims['sub']).first()
            if user is None:
                return redirect('/login')
            session['user'] = user.username
        except ExpiredSignatureError:
            return redirect('/login')
        return f()
    wrap.__name__ = f.__name__
    return wrap
