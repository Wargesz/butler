from flask import Flask
from routes.root_routes import root_bp
from routes.vault_routes import vault_bp
from routes.midnight_routes import midnight_bp
from controllers.db import setup_db, DB
from dotenv import dotenv_values

env = dotenv_values('.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = env['SECRET']

app.register_blueprint(root_bp, url_prefix='/')
app.register_blueprint(vault_bp, url_prefix='/vault')
app.register_blueprint(midnight_bp, url_prefix='/midnight')


def trailing(s):
    return s.split('/')[-1]


def nested(s):
    return s.count('/')


app.jinja_env.filters['trailing'] = trailing
app.jinja_env.filters['nested'] = nested


@app.teardown_appcontext
def shutdown_session(exception=None):
    DB.remove()


if __name__ == '__main__':
    setup_db()
    app.run(port=8080, debug=True)
