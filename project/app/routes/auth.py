from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm, RegisterForm
from app.models import Role, User
from app.services.audit_service import log_session
from app.utils.security import rate_limit


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
@rate_limit("login", max_calls=8, period_seconds=300)
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            log_session(user.id)
            flash("Bienvenido de nuevo.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("public.home"))
        flash("Credenciales inválidas.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("public.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash("El email ya está registrado.", "warning")
            return render_template("auth/register.html", form=form)

        visitor_role = Role.query.filter_by(name="Visitor").first()
        if not visitor_role:
            visitor_role = Role(name="Visitor", description="Usuario visitante")
            db.session.add(visitor_role)
            db.session.flush()

        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            role_id=visitor_role.id,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Registro completado. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("public.home"))


@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("auth/profile.html")
