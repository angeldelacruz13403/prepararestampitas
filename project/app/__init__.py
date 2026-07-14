import os

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import config_by_name
from app.extensions import csrf, db, login_manager, migrate
from app.models import Role, Settings, User
from app.routes import admin_bp, auth_bp, public_bp, seo_bp

load_dotenv()


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


def _seed_defaults() -> None:
    if not Role.query.first():
        roles = [
            Role(name="Admin", description="Administrador"),
            Role(name="Editor", description="Editor"),
            Role(name="Visitor", description="Visitante"),
        ]
        db.session.add_all(roles)
    if not Settings.query.first():
        db.session.add(Settings())
    db.session.commit()


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    env = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(env, config_by_name["development"]))
    if env == "production" and app.config["TRUSTED_PROXY_COUNT"] > 0:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=app.config["TRUSTED_PROXY_COUNT"], x_host=1)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para continuar."

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(seo_bp)

    @app.context_processor
    def inject_seo_defaults():
        return {
            "default_meta": {
                "title": "Cruz Cofrade",
                "description": "Fotografía profesional de Semana Santa",
            }
        }

    with app.app_context():
        db.create_all()
        _seed_defaults()

    return app
