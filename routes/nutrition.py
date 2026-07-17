from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

# import datetime
# import csv
# from io import StringIO

from databases.db import get_db_connection


nutrition_bp = Blueprint("nutrition", __name__)

@nutrition_bp.route("/nutrition")
def nutrition():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Fetch meals (date + time separately)
    cursor.execute("""
        SELECT 
            meal_name, calories, protein, carbs, fats,
            DATE(meal_date) AS meal_day,
            TIME(meal_date) AS meal_time
        FROM nutrition_logs
        WHERE user_id=%s
        ORDER BY meal_date DESC
    """, (session["user_id"],))

    rows = cursor.fetchall()

    # Convert dates/times to string (safer for Jinja) and group by day
    meal_history = {}
    for row in rows:
        # row["meal_day"] and row["meal_time"] might be date/time objects or strings depending on connector
        day = row["meal_day"]
        time = row["meal_time"]

        # Normalize to string if they are date/time objects
        try:
            day_str = day.strftime("%Y-%m-%d")
        except Exception:
            day_str = str(day)

        try:
            time_str = time.strftime("%H:%M:%S")
        except Exception:
            time_str = str(time)

        row["meal_day"] = day_str
        row["meal_time"] = time_str

        if day_str not in meal_history:
            meal_history[day_str] = []
        meal_history[day_str].append(row)

    # Daily totals (could be None if no rows)
    cursor.execute("""
        SELECT 
            COALESCE(SUM(calories),0) AS total_calories,
            COALESCE(SUM(protein),0) AS total_protein,
            COALESCE(SUM(carbs),0) AS total_carbs,
            COALESCE(SUM(fats),0) AS total_fats
        FROM nutrition_logs
        WHERE user_id = %s
        AND DATE(meal_date) = CURDATE()
    """, (session["user_id"],))


    totals = cursor.fetchone() or {
        "total_calories": 0,
        "total_protein": 0,
        "total_carbs": 0,
        "total_fats": 0
    }

    # Make sure totals fields exist and are numeric (avoid None in template)
    totals["total_calories"] = totals.get("total_calories") or 0
    totals["total_protein"]  = totals.get("total_protein")  or 0
    totals["total_carbs"]    = totals.get("total_carbs")    or 0
    totals["total_fats"]     = totals.get("total_fats")     or 0

    cursor.close()
    conn.close()

    # Pass both the totals dict and individual variables for convenience
    return render_template(
        "nutrition.html",
        meal_history=meal_history,
        totals=totals,
        total_calories=totals["total_calories"],
        total_protein=totals["total_protein"],
        total_carbs=totals["total_carbs"],
        total_fats=totals["total_fats"],
    )


#nutrition
@nutrition_bp.route("/add_meal", methods=["POST"])
def add_meal():
    if "user_id" not in session:
        return redirect(url_for("login"))

    meal = request.form["meal"]
    calories = float(request.form["calories"])
    protein = float(request.form["protein"])
    carbs = float(request.form["carbs"])
    fats = float(request.form["fats"])

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO nutrition_logs 
        (user_id, meal_name, calories, protein, carbs, fats)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (session["user_id"], meal, calories, protein, carbs, fats))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Meal Added Successfully 🍎", "success")
    return redirect(url_for("nutrition.nutrition"))
