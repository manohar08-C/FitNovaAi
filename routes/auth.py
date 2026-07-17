from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from flask_bcrypt import Bcrypt
import mysql.connector

from databases.db import get_db_connection

auth_bp = Blueprint("auth", __name__)

bcrypt = Bcrypt()


@auth_bp.route("/")
def home():
    return render_template("landing.html")


@auth_bp.route("/start")
def start():
    return redirect(url_for("auth.login"))

# Register route
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        age = request.form["age"]
        gender = request.form["gender"]

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        try:
            cursor.execute("""
                INSERT INTO users (name, email, password, age, gender)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, email, hashed_password, age, gender))
            conn.commit()
            flash("Registration Successful! Please Login.", "success")
            return redirect(url_for("auth.login"))
        except mysql.connector.Error:
            flash("Email already exists!", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")

# Login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid Credentials!", "danger")

    return render_template("login.html")

# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))