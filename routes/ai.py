from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
    current_app
)

from werkzeug.utils import secure_filename

import os
import requests

from databases.db import get_db_connection

from ai_modules.gemini_service import generate_response
from utils.predict_food import predict_food

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_DIR = os.path.join(BASE_DIR, "static")

UPLOAD_FOLDER = os.path.join(STATIC_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)



ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai_workout")
def ai_workout():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("ai_workout.html")

@ai_bp.route("/ai_coach")
def ai_coach():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("ai_coach.html")


@ai_bp.route("/ai_planner")
def ai_planner():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("ai_planner.html")





@ai_bp.route("/ask_ai", methods=["POST"])
def ask_ai():
    question = request.json["message"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # 1️⃣ Get basic user info
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()

    # 2️⃣ Get fitness profile
    cursor.execute("SELECT * FROM user_profiles WHERE user_id=%s", (session["user_id"],))
    profile = cursor.fetchone()

    # 3️⃣ Get total workout calories
    cursor.execute("""
        SELECT SUM(calories_burned) AS total_workout
        FROM workout_logs
        WHERE user_id=%s
    """, (session["user_id"],))
    workout = cursor.fetchone()

    # 4️⃣ Get food calories
    cursor.execute("""
        SELECT SUM(calories) AS total_food
        FROM nutrition_logs
        WHERE user_id=%s
    """, (session["user_id"],))
    food = cursor.fetchone()

    # 5️⃣ Streak
    cursor.execute("""
        SELECT current_streak 
        FROM user_streaks
        WHERE user_id=%s
    """, (session["user_id"],))
    streak = cursor.fetchone()

    cursor.close()
    conn.close()

    if not profile:
        return jsonify({
        "reply": "Please complete your profile before using the AI Coach."
        })
    
    # 6️⃣ Calculate BMI
    bmi = round(profile["weight"] / ((profile["height"]/100)**2), 2)

    # 7️⃣ Build AI prompt
    prompt = f"""
            You are an expert AI fitness coach.

            User Profile:
            Name: {user["name"]}
            Age: {profile["age"]}
            BMI: {bmi}
            Goal: {profile["goal"]}
            Level: {profile["level"]}
            Current Streak: {streak["current_streak"] if streak else 0}
            Total Workout Calories: {workout["total_workout"] if workout["total_workout"] else 0}
            Total Food Calories: {food["total_food"] if food["total_food"] else 0}

            Give clear, professional advice.

            User Question:
            {question}
            """

    answer = generate_response(prompt)

    return jsonify({"reply": answer})



@ai_bp.route("/generate_plan", methods=["POST"])
def generate_plan():

    if "user_id" not in session:
        return {"error": "Not logged in"}, 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute(
        "SELECT * FROM user_profiles WHERE user_id=%s",
        (session["user_id"],)
    )

    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    if not profile:
        return {"error": "Please complete your profile first."}, 400

    bmi = round(
        profile["weight"] / ((profile["height"] / 100) ** 2),
        2
    )

    prompt = f"""
    You are a professional fitness coach.

    User Profile:
    Age: {profile["age"]}
    BMI: {bmi}
    Goal: {profile["goal"]}
    Level: {profile["level"]}
    Daily Calories Target: {profile["daily_calorie_target"]}

    Generate:
    1. A 1-day workout plan (exercise name, sets, reps)
    2. A 1-day diet plan (breakfast, lunch, dinner, calories)

    Keep it clear and structured.
    """

    answer = generate_response(prompt)
    return jsonify({
    "plan": answer
    })
    


CATEGORY_MACROS = {
    "Rice": {"calories": 200, "protein": 4, "carbs": 45, "fats": 1},
    "Bread": {"calories": 250, "protein": 8, "carbs": 49, "fats": 3},
    "Egg": {"calories": 78, "protein": 6, "carbs": 1, "fats": 5},
    "Meat": {"calories": 250, "protein": 26, "carbs": 0, "fats": 15},
    "Vegetable-Fruit": {"calories": 80, "protein": 2, "carbs": 15, "fats": 0},
    "Dessert": {"calories": 300, "protein": 4, "carbs": 50, "fats": 10},
    "Fried food": {"calories": 350, "protein": 5, "carbs": 40, "fats": 20},
    "Seafood": {"calories": 180, "protein": 20, "carbs": 0, "fats": 5},
    "Soup": {"calories": 120, "protein": 5, "carbs": 15, "fats": 3},
    "Dairy product": {"calories": 150, "protein": 8, "carbs": 12, "fats": 8},
    "Noodles-Pasta": {"calories": 220, "protein": 7, "carbs": 42, "fats": 3}
}



# UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # type: ignore


def get_nutrition_from_api(food_name, quantity):
    try:
        # API_KEY = "gkcXjG3bTlrtkC8BlWvcCIzs5Z58kZFADrb0rnXa"
        API_KEY = current_app.config["USDA_API_KEY"]

        # 1️⃣ SEARCH FOOD
        search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        search_params = {
            "query": food_name,
            "api_key": API_KEY
        }

        search_res = requests.get(search_url, params=search_params)
        search_data = search_res.json()

        foods = search_data.get("foods", [])
        if not foods:
            return None

        food_item = foods[0]  # take top result

        # 2️⃣ EXTRACT NUTRIENTS
        nutrients = food_item.get("foodNutrients", [])

        calories = protein = carbs = fats = 0

        for n in nutrients:
            name = n.get("nutrientName", "").lower()

            if "energy" in name:
                calories = n.get("value", 0)
            elif "protein" in name:
                protein = n.get("value", 0)
            elif "carbohydrate" in name:
                carbs = n.get("value", 0)
            elif "total lipid" in name or "fat" in name:
                fats = n.get("value", 0)

        # 3️⃣ SCALE BASED ON QUANTITY (default USDA = per 100g)
        factor = quantity / 100

        return {
            "calories": round(calories * factor, 2),
            "protein": round(protein * factor, 2),
            "carbs": round(carbs * factor, 2),
            "fats": round(fats * factor, 2)
        }

    except Exception as e:
        print("USDA API Error:", e)
        return None
    

@ai_bp.route("/ai_food", methods=["GET", "POST"])
def ai_food():
    from utils.predict_food import predict_food
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    result = None
    confidence = 0

    if request.method == "POST":
        file = request.files["food_image"]

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            image_path = f"uploads/{filename}"

            # 🔥 YOUR FOOD MODEL PREDICTION HERE
            predicted_food, confidence = predict_food(filepath)

            
            quantity = request.form.get("quantity", 100)  # default 100g
            quantity = float(quantity)


            macros = get_nutrition_from_api(predicted_food, quantity)

            # If USDA API fails, use local nutrition values
            if macros is None:
                base = CATEGORY_MACROS.get(predicted_food)

                if base:
                    macros = {
                        "calories": base["calories"] * quantity / 100,
                        "protein": base["protein"] * quantity / 100,
                        "carbs": base["carbs"] * quantity / 100,
                        "fats": base["fats"] * quantity / 100
                    }
                else:
                    macros = {
                        "calories": 0,
                        "protein": 0,
                        "carbs": 0,
                        "fats": 0
                    }


            result = {
                "food": predicted_food,
                "quantity": quantity,
                "calories": macros["calories"],
                "protein": macros["protein"],
                "carbs": macros["carbs"],
                "fats": macros["fats"],
                "confidence": round(confidence * 100, 2),
                "image": image_path,
            }

        flash("AI Food Detected & Logged 🍎", "success")

        print(result)

    return render_template("ai_food.html", result=result)




@ai_bp.route("/add_meal_from_ai", methods=["POST"])
def add_meal_from_ai():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    food = request.form["food"]
    calories = float(request.form["calories"])
    protein = float(request.form["protein"])
    carbs = float(request.form["carbs"])
    fats = float(request.form["fats"])

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO nutrition_logs 
        (user_id, meal_name, calories, protein, carbs, fats, meal_date)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """, (session["user_id"], food, calories, protein, carbs, fats))

    conn.commit()
    cursor.close()
    conn.close()


    return redirect(url_for("nutrition.nutrition"))



@ai_bp.route("/nutrition")
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
@ai_bp.route("/add_meal", methods=["POST"])
def add_meal():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

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