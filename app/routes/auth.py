from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import User
from app.services.security import role_required, validate_password_policy


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("用户名或密码错误", "error")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
@login_required
@role_required("admin")
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user").strip()
        if not username:
            flash("用户名不能为空", "error")
            return render_template("register.html")
        if User.query.filter_by(username=username).first():
            flash("用户名已存在", "error")
            return render_template("register.html")
        valid, msg = validate_password_policy(password)
        if not valid:
            flash(msg, "error")
            return render_template("register.html")
        if role not in {"admin", "user"}:
            role = "user"
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("用户创建成功", "success")
        return redirect(url_for("auth.user_admin"))
    return render_template("register.html")


@auth_bp.route("/admin/users")
@login_required
@role_required("admin")
def user_admin():
    users = User.query.order_by(User.id.asc()).all()
    return render_template("users.html", users=users)


@auth_bp.route("/admin/users/create", methods=["POST"])
@login_required
@role_required("admin")
def user_create_inline():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "user").strip()
    if not username:
        flash("用户名不能为空", "error")
        return redirect(url_for("auth.user_admin"))
    if User.query.filter_by(username=username).first():
        flash("用户名已存在", "error")
        return redirect(url_for("auth.user_admin"))
    valid, msg = validate_password_policy(password)
    if not valid:
        flash(msg, "error")
        return redirect(url_for("auth.user_admin"))
    if role not in {"admin", "user"}:
        role = "user"
    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash("用户创建成功", "success")
    return redirect(url_for("auth.user_admin"))


@auth_bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def user_delete(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("用户不存在", "error")
        return redirect(url_for("auth.user_admin"))
    if user.username == "admin":
        flash("默认管理员不可删除", "error")
        return redirect(url_for("auth.user_admin"))
    db.session.delete(user)
    db.session.commit()
    flash("用户删除成功", "success")
    return redirect(url_for("auth.user_admin"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


def ensure_default_user():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", role="admin")
        admin.set_password("Admin@123")
        db.session.add(admin)
        db.session.commit()
        return
    if admin.role != "admin":
        admin.role = "admin"
    if admin.check_password("admin123"):
        admin.set_password("Admin@123")
    db.session.commit()
