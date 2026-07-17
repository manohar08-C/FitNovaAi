# 🏋️‍♂️ FitNovaAI – AI-Powered Fitness & Nutrition Companion

An AI-powered fitness and nutrition web application that provides personalized workout plans, nutrition analysis, posture correction, food recognition, and AI coaching using computer vision and Large Language Models.

---

# 🚀 Features

## 👤 User Management
- User Registration
- Secure Login & Logout
- Password Hashing using Flask-Bcrypt
- User Profile Management

---

## 📊 Dashboard
- Daily Calorie Tracking
- BMI Calculation
- Workout History
- Progress Tracking
- Workout Streak System
- Calories Burned vs Calories Consumed
- Interactive Dashboard

---

## 💪 Workout Module
- Add Workouts
- Update Workouts
- Delete Workouts
- Download Workout History as CSV
- Daily Workout Logs

---

## 🥗 Nutrition Module
- Add Meals
- Nutrition History
- Daily Nutrition Summary
- Calories
- Protein
- Carbohydrates
- Fats

---

## 🤖 AI Coach

Powered by **Google Gemini API**

Features:

- Personalized Fitness Guidance
- Diet Recommendations
- Workout Suggestions
- Goal-based Advice
- Fitness Q&A

---

## 🧠 AI Workout Planner

Generates

- Personalized Workout Plans
- Diet Plans
- Daily Calorie Targets

based on

- BMI
- Fitness Goal
- Experience Level

---

## 🍎 AI Food Detection

Powered by

- MobileNetV2
- USDA FoodData Central API

Features

- Food Recognition
- Nutrition Estimation
- Calories
- Protein
- Carbs
- Fats

---

## 🧍 AI Pose Detection

Powered by

- MediaPipe Pose Landmarker

Supports

- Pushups
- Squats
- Bicep Curls

Features

- Real-time Pose Detection
- Exercise Counting
- Confidence Score
- Form Correction

---

# 🏗 Project Architecture

```
FitNovaAI
│
├── app.py
├── config.py
│
├── routes
│   ├── auth.py
│   ├── dashboard.py
│   ├── nutrition.py
│   ├── profile.py
│   ├── ai.py
│   └── pose.py
│
├── databases
│   └── db.py
│
├── ai_modules
│   └── gemini_service.py
│
├── models
│
├── templates
│
├── static
│
└── utils
```

---

# 🛠 Technologies Used

## Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript

---

## Backend

- Flask
- Python

---

## Database

- MySQL
- Railway MySQL

---

## Artificial Intelligence

- Google Gemini API
- MobileNetV2
- MediaPipe Pose
- Computer Vision

---

## Machine Learning

- TensorFlow
- Keras
- OpenCV

---

## APIs

- Google Gemini API
- USDA FoodData Central API

---

# 📦 Python Libraries

- Flask
- Flask-Bcrypt
- mysql-connector-python
- TensorFlow
- Keras
- OpenCV
- MediaPipe
- Google GenAI
- Requests
- NumPy

---

# 📈 System Workflow

User

↓

Login/Register

↓

Dashboard

↓

Choose Module

↓

Workout

↓

Nutrition

↓

AI Coach

↓

Pose Detection

↓

Food Detection

↓

Database

↓

Analytics Dashboard

---

# 🔐 Authentication

Passwords are securely encrypted using

- Flask-Bcrypt

---

# 📷 AI Modules

## AI Coach

Uses Google Gemini to answer:

- Workout Questions
- Nutrition Questions
- Goal Planning
- Fitness Guidance

---

## Food Detection

Image Upload

↓

MobileNetV2

↓

Food Prediction

↓

USDA API

↓

Nutrition Information

↓

Save to Database

---

## Pose Detection

Webcam

↓

MediaPipe

↓

Pose Landmarks

↓

Angle Calculation

↓

Rep Counter

↓

Workout Log

---

# 📊 Database

Main Tables

- users
- user_profiles
- workout_logs
- nutrition_logs
- user_streaks

---

# ⚙ Installation

Clone Repository

```bash
git clone https://github.com/yourusername/FitNovaAI.git
```

Open Project

```bash
cd FitNovaAI
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Configure Environment Variables

Create

```
.env
```

Add

```env
SECRET_KEY=your_secret_key

MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

USDA_API_KEY=your_usda_api_key

GEMINI_API_KEY=your_gemini_api_key
```

Run

```bash
python app.py
```

---

# 🚀 Deployment

The project can be deployed on

- Render
- Railway
- PythonAnywhere

---

# Future Improvements

- Multi-language Support
- AI Meal Planner
- Weekly Analytics
- Monthly Reports
- Fitness Challenges
- Social Features
- Smart Notifications

---

# 👨‍💻 Developer

**Manohar Chodipalli**

Master of Computer Applications (MCA)

Python Full Stack Developer | AI & Machine Learning Enthusiast

---

# ⭐ If you like this project

Give this repository a ⭐ on GitHub.
