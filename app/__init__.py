from flask import Flask
from app.routes.vault_routes import vault_bp
from app.routes.midnight_routes import midnight_bp
from app.routes.root_routes import root_bp

DATABASE = "butler.db"


def create_app():
    app = Flask(__name__)
    app.register_blueprint(vault_bp, url_prefix='/vault')
    app.register_blueprint(midnight_bp, url_prefix='/midnight')
    app.register_blueprint(root_bp)
    return app
