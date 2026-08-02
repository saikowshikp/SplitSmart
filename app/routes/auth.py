from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, logout_user

from app.forms.auth_forms import LoginForm, RegisterForm
from app.services.auth_service import AuthService


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/")
def home():
    """Redirect the application root to the login page."""
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Authenticate an existing user.

    Authentication logic is delegated to AuthService.
    Validation is handled by LoginForm.
    """

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        success, message = AuthService.login(
            email=form.email.data,
            password=form.password.data,
        )

        if success:
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard.dashboard"))

        flash(message, "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.

    Validation is handled by RegisterForm.
    Account creation is delegated to AuthService.
    """

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():
        success, message = AuthService.register(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
        )

        if success:
            flash(
                "Account created successfully. Please login.",
                "success",
            )
            return redirect(url_for("auth.login"))

        flash(message, "danger")

    return render_template("register.html", form=form)


@auth_bp.post("/logout")
def logout():
    """
    Log out the currently authenticated user.

    Logout is intentionally POST-only to prevent CSRF-triggered
    logout via a simple GET request.
    """

    if current_user.is_authenticated:
        logout_user()

    flash("You have been logged out.", "info")

    return redirect(url_for("auth.login"))