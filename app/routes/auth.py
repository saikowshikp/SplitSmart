from flask import Blueprint, render_template, request, redirect, url_for, flash

from flask_login import current_user, logout_user

from app.forms.auth_forms import LoginForm, RegisterForm
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))



@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = LoginForm()

    if request.method == "POST":

        if form.validate_on_submit():

            success, message = AuthService.login(
                email=form.email.data.strip(),
                password=form.password.data
            )

            if success:

                flash("Welcome back!", "success")

                return redirect(url_for("dashboard.dashboard"))

            flash(message, "danger")

    return render_template(
        "login.html",
        form=form,
        user=None
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        success, message = AuthService.register(
            name=form.name.data.strip(),
            email=form.email.data.strip(),
            password=form.password.data
        )

        if success:

            flash(
                "Account created successfully. Please login.",
                "success"
            )

            return redirect(
                url_for("auth.login")
            )


        flash(message, "danger")


    return render_template(
        "register.html",
        form=form
    )


@auth_bp.route("/logout")
def logout():

    logout_user()

    flash("You have been logged out.", "info")

    return redirect(url_for("auth.login"))