from flask import Flask

from config import Config

from .extensions import db
from .extensions import login_manager
from .extensions import migrate

from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.group import group_bp
from .routes.expense import expense_bp
from .routes.settlements import settlement_bp
from .routes.receipt import receipt_bp


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    migrate.init_app(app, db)

    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(group_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(settlement_bp)
    app.register_blueprint(receipt_bp)

    return app