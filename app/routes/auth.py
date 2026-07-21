from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from flask_login import login_user
from flask_login import logout_user

from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))



@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard.dashboard"))

        return "Invalid Credentials"

    return render_template("login.html",
                           user = None)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return "Email already exists"

        User.add_user(name, email, password)

        return redirect(url_for("auth.login"))

    return render_template("register.html",
                           user = None)


@auth_bp.route("/logout")
def logout():

    logout_user()

    return redirect(url_for("auth.login"))