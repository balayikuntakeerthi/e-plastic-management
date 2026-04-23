from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate   # ✅ NEW
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()   # ✅ NEW

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)   # ✅ NEW

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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

    return app
