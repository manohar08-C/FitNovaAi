from databases.db import get_db_connection
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    make_response
)

import datetime
import csv
from io import StringIO




dashboard_bp = Blueprint("dashboard",__name__)

def update_streak(user_id, did_activity_today):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get existing streak record
    cursor.execute("SELECT * FROM user_streaks WHERE user_id=%s", (user_id,))
    record = cursor.fetchone()

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    # If no record exists for this user
    if not record:
        if did_activity_today:
            cursor.execute("""
                INSERT INTO user_streaks (user_id, current_streak, last_workout_date)
                VALUES (%s, %s, %s)
            """, (user_id, 1, today))
            conn.commit()
        return

    last_date = record["last_workout_date"]
    streak = record["current_streak"]

    if did_activity_today:
        if last_date == yesterday:
            streak += 1
        else:
            streak = 1

        cursor.execute("""
            UPDATE user_streaks 
            SET current_streak=%s, last_workout_date=%s
            WHERE user_id=%s
        """, (streak, today, user_id))

        conn.commit()

    cursor.close()
    conn.close()



@dashboard_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # ---------- USER ----------
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()

    # ---------- PROFILE ----------
    cursor.execute("SELECT * FROM user_profiles WHERE user_id=%s", (session["user_id"],))
    profile = cursor.fetchone()

    # Default values
    bmi = 0
    daily_goal = 0
    user_goal = "Not Set"

    if profile:
        if profile["height"] and profile["weight"]:
            bmi = round(profile["weight"] / ((profile["height"] / 100) ** 2), 2)

        daily_goal = profile.get("daily_calorie_target", 0)
        user_goal = profile.get("goal", "Not Set")

    # ---------- FOOD CALORIES TODAY ----------
    cursor.execute("""
        SELECT COALESCE(SUM(calories),0) AS food_today
        FROM nutrition_logs
        WHERE user_id=%s AND DATE(meal_date)=CURDATE()
    """, (session["user_id"],))

    food_today = cursor.fetchone()["food_today"]

    # ---------- WORKOUT CALORIES TODAY ----------
    cursor.execute("""
        SELECT COALESCE(SUM(calories_burned),0) AS workout_today
        FROM workout_logs
        WHERE user_id=%s AND DATE(workout_date)=CURDATE()
    """, (session["user_id"],))

    workout_today = cursor.fetchone()["workout_today"]
    
    did_activity = (food_today > 0 or workout_today > 0)
    update_streak(session["user_id"], did_activity)

    remaining = daily_goal - (food_today - workout_today)

    if remaining < 0:
        remaining = 0

    # ---------- STREAK ----------
    cursor.execute("""
        SELECT current_streak
        FROM user_streaks
        WHERE user_id=%s
    """, (session["user_id"],))

    streak_record = cursor.fetchone()
    current_streak = streak_record["current_streak"] if streak_record else 0

    # ---------- WORKOUT HISTORY (LATEST 20) ----------
    cursor.execute("""
        SELECT exercise_name, sets, reps, calories_burned, workout_date
        FROM workout_logs
        WHERE user_id=%s
        ORDER BY workout_date DESC
        LIMIT 20
    """, (session["user_id"],))

    workouts = cursor.fetchall()

    # ---------- CHART DATA ----------
    cursor.execute("""
        SELECT DATE(workout_date) AS date,
            SUM(calories_burned) AS daily_calories
        FROM workout_logs
        WHERE user_id=%s
        GROUP BY DATE(workout_date)
        ORDER BY DATE(workout_date) ASC
    """, (session["user_id"],))
    chart_data = cursor.fetchall()



    # DAY-WISE WORKOUT HISTORY
    cursor.execute("""
        SELECT 
            DATE(workout_date) AS day,
            id,
            exercise_name,
            sets,
            reps,
            calories_burned,
            workout_date
        FROM workout_logs
        WHERE user_id=%s
        ORDER BY workout_date DESC
    """, (session["user_id"],))

    rows = cursor.fetchall()

    workout_history = {}
    for w in rows:
        day = str(w["day"])
        if day not in workout_history:
            workout_history[day] = []
        workout_history[day].append(w)

    cursor.close()
    conn.close()

    progress_percentage = 0

    if daily_goal > 0:
        net_calories = food_today - workout_today  
        progress_percentage = min((net_calories / daily_goal) * 100, 100)

    return render_template(
        "dashboard.html",
        user=user,
        profile=profile,
        bmi=bmi,
        total_calories=daily_goal,       # Total Calories = Daily Target
        food_calories=food_today,        # Food Calories Today
        workout_calories=workout_today,  # Workout Calories Today
        remaining=remaining,
        user_goal=user_goal,
        current_streak=current_streak,
        progress_percentage=round(progress_percentage, 2),
        chart_data=chart_data,
        workouts=workouts,
        workout_history=workout_history
    )



@dashboard_bp.route("/add_workout", methods=["POST"])
def add_workout():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    exercise = request.form["exercise"]
    sets = int(request.form["sets"])
    reps = int(request.form["reps"])

    # ✅ ADD THIS LINE (IMPORTANT)
    calories = round(int(sets) * int(reps) * 0.5, 2)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO workout_logs 
        (user_id, exercise_name, sets, reps, calories_burned, workout_date)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (session["user_id"], exercise, sets, reps, calories))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("dashboard.dashboard"))


#delete specific workout
@dashboard_bp.route("/delete_workout/<int:wid>")
def delete_workout(wid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workout_logs WHERE id=%s AND user_id=%s",
                   (wid, session["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("dashboard.dashboard"))
#delete whole workout
@dashboard_bp.route("/delete_day/<date>")
def delete_day(date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM workout_logs
        WHERE user_id=%s AND DATE(workout_date)=%s
    """, (session["user_id"], date))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("dashboard.dashboard"))



#edit workout
@dashboard_bp.route("/get_workout/<int:wid>")
def get_workout(wid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, exercise_name, sets, reps
        FROM workout_logs
        WHERE id=%s AND user_id=%s
    """, (wid, session["user_id"]))

    workout = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(workout)


@dashboard_bp.route("/update_workout/<int:wid>")
def update_workout_page(wid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, exercise_name, sets, reps
        FROM workout_logs
        WHERE id=%s AND user_id=%s
    """, (wid, session["user_id"]))

    workout = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("update_workout.html", workout=workout)


@dashboard_bp.route("/update_workout_submit", methods=["POST"])
def update_workout_submit():
    wid = request.form["workout_id"]
    exercise = request.form["exercise"]
    sets = request.form["sets"]
    reps = request.form["reps"]

    # Recalculate calories (simple logic)
    calories = int(reps) * 0.5

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE workout_logs
        SET exercise_name=%s, sets=%s, reps=%s, calories_burned=%s
        WHERE id=%s AND user_id=%s
    """, (exercise, sets, reps, calories, wid, session["user_id"]))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Workout updated successfully!", "success")
    return redirect(url_for("dashboard.dashboard"))


#download csv file, redirect

@dashboard_bp.route("/download_day/<date>")
def download_day(date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM workout_logs
        WHERE user_id=%s AND DATE(workout_date)=%s
    """, (session["user_id"], date))

    rows = cursor.fetchall()

    if not rows:
        flash("No workouts found for this day.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # Use StringIO to build CSV data
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=workouts_{date}.csv"
    response.headers["Content-Type"] = "text/csv"

    return response