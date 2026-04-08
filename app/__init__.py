from flask import Flask, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user
from sqlalchemy import inspect, text

from app.config import Config
from app.extensions import db, login_manager
from app.models import Job, User
from app.routes.auth import auth_bp, ensure_default_user
from app.routes.main import main_bp
from app.services.analytics import category_menu, refresh_ml_cache
from app.services.data_loader import load_jobs_from_csv


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "请先登录后再访问系统"

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_menu():
        return {"menu": category_menu()}

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route("/bootstrap")
    @login_required
    def bootstrap():
        if User.query.count() > 0 and current_user.role != "admin":
            return redirect(url_for("main.dashboard"))
        with app.app_context():
            db.create_all()
            ensure_schema_columns()
            ensure_default_user()
            load_jobs_from_csv(app.config["RAW_CSV_PATH"])
            refresh_ml_cache()
        return redirect(url_for("entry"))

    @app.route("/setup")
    def setup():
        jobs_count = Job.query.count()
        users_count = User.query.count()
        return render_template("setup.html", jobs_count=jobs_count, users_count=users_count)

    @app.route("/entry")
    def entry():
        if Job.query.count() == 0:
            return redirect(url_for("setup"))
        if current_user.is_authenticated:
            logout_user()
        return redirect(url_for("auth.login"))

    with app.app_context():
        db.create_all()
        ensure_schema_columns()
        ensure_default_user()
        if Job.query.count() > 0:
            refresh_ml_cache()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def ensure_schema_columns():
    inspector = inspect(db.engine)
    if "jobs" not in inspector.get_table_names():
        return
    cols = {c["name"] for c in inspector.get_columns("jobs")}
    if "company_industry" not in cols:
        db.session.execute(text("ALTER TABLE jobs ADD COLUMN company_industry VARCHAR(128)"))
        db.session.commit()
