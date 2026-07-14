from flask import Flask

from config import Config

from .extensions import db
from .extensions import login_manager
from .extensions import migrate

from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    migrate.init_app(app, db)

    login_manager.init_app(app)

    app.register_blueprint(auth_bp)

    app.register_blueprint(dashboard_bp)


    return app