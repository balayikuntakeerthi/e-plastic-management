from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from app.routes.data_entry import data_bp
    from app.routes.analysis import analysis_bp
    from app.routes.prediction import predict_bp
    from app.routes.auth import auth_bp
    from app.routes.nss import nss_bp
    from app.routes.events import events_bp
    from app.routes.report import report_bp
    app.register_blueprint(data_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(nss_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(report_bp)

    # ✅ Unified CLI command to create any user
    @click.command("create-user")
    @with_appcontext
    def create_user():
        username = input("Enter username: ")
        password = input("Enter password: ")
        role = input("Enter role (admin/volunteer): ").lower()
        is_super = input("Is superadmin? (y/n): ").lower() == "y"

        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role,
            is_superuser=is_super
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ User {username} ({role}) created successfully!")

    app.cli.add_command(create_user)

    return app
