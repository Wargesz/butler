from flask import Flask
from routes.root_routes import root_bp
from routes.vault_routes import vault_bp
from routes.midnight_routes import midnight_bp
from controllers.db import setup_db, DB
from models.models import User

app = Flask(__name__)
app.register_blueprint(root_bp, prefix='/')
app.register_blueprint(vault_bp, prefix='/vault')
app.register_blueprint(midnight_bp, prefix='/midnight')


@app.teardown_appcontext
def shutdown_session(exception=None):
    DB.remove()


if __name__ == '__main__':
    setup_db()
    app.run(port=8080)
