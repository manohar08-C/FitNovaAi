from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from databases.db import get_db_connection


profile_bp = Blueprint("profile",__name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    if request.method == "POST":
        age = int(request.form["age"])
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        goal = request.form["goal"]
        level = request.form["level"]

        # --- AUTO CALCULATE CALORIES ---
        # BMR — Mifflin-St Jeor
        BMR = 10 * weight + 6.25 * height - 5 * age + 5  # assuming male user (customise later)

        if goal == "fat_loss":
            daily_calories = round(BMR * 1.2 - 400)
        elif goal == "muscle_gain":
            daily_calories = round(BMR * 1.4 + 300)
        else:   # maintenance
            daily_calories = round(BMR * 1.3)

        cursor.execute("SELECT * FROM user_profiles WHERE user_id=%s", (session["user_id"],))
        existing_profile = cursor.fetchone()

        if existing_profile:
            # UPDATE
            cursor.execute("""
                UPDATE user_profiles SET 
                    age=%s, height=%s, weight=%s, goal=%s, level=%s, daily_calorie_target=%s
                WHERE user_id=%s
            """, (age, height, weight, goal, level, daily_calories, session["user_id"]))

        else:
            # INSERT
            cursor.execute("""
                INSERT INTO user_profiles 
                (user_id, age, height, weight, goal, level, daily_calorie_target)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (session["user_id"], age, height, weight, goal, level, daily_calories))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.profile"))

    # GET profile details
    cursor.execute("SELECT * FROM user_profiles WHERE user_id=%s", (session["user_id"],))
    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("profile.html", profile=profile)
