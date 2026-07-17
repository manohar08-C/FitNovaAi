import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
from flask import (
    Blueprint,
    Response,
    request,
    session
)
from databases.db import get_db_connection

pose_bp = Blueprint("pose", __name__)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle



current_exercise = None
session_counter = 0
session_active = False
stage = None
angle_history = []

def generate_frames():
    global session_active, session_counter, current_exercise, stage, angle_history

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera failed to open")
        return

    stage = None

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            try:
                detection_result = pose_detector.detect_for_video(
                    mp_image,
                    int(cap.get(cv2.CAP_PROP_POS_MSEC))
                )

                if session_active and detection_result.pose_landmarks:
                    landmarks = detection_result.pose_landmarks[0]


                    # Calculate confidence using average visibility
                    visibility_scores = [lm.visibility for lm in landmarks]
                    confidence = sum(visibility_scores) / len(visibility_scores)

                    confidence_percent = round(confidence * 100, 2)

                    cv2.putText(frame, f"Confidence: {confidence_percent}%",
                                (50, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0, 255, 255), 2)

                    # ================= PUSHUPS =================
                    if current_exercise == "pushup":
                        shoulder = landmarks[11]
                        elbow = landmarks[13]
                        wrist = landmarks[15]
                        
                        raw_angle = calculate_angle(
                            [shoulder.x, shoulder.y],
                            [elbow.x, elbow.y],
                            [wrist.x, wrist.y]
                        )
                        angle_history.append(raw_angle)

                        if len(angle_history) > 5:
                            angle_history.pop(0)

                        angle = sum(angle_history) / len(angle_history)


                        cv2.putText(frame, f"Pushup Angle: {int(angle)}",
                                    (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 255, 0), 2)

                        if angle > 160:
                            stage = "down"

                        if 90 < angle < 140:
                            cv2.putText(frame, "Go Lower!",
                                        (50, 150),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.8, (0, 0, 255), 2)

                        if angle < 90 and stage == "down":
                            stage = "up"
                            session_counter += 1



                    # ================= SQUATS =================
                    elif current_exercise == "squat":
                        hip = landmarks[23]
                        knee = landmarks[25]
                        ankle = landmarks[27]

                        angle = calculate_angle(
                            [hip.x, hip.y],
                            [knee.x, knee.y],
                            [ankle.x, ankle.y]
                        )

                        cv2.putText(frame, f"Squat Angle: {int(angle)}",
                                    (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (255, 255, 0), 2)

                        if angle > 160:
                            stage = "up"

                        if 90 < angle < 130:
                            cv2.putText(frame, "Squat Deeper!",
                                        (50, 150),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.8, (0, 0, 255), 2)

                        if angle < 90 and stage == "up":
                            stage = "down"
                            session_counter += 1



                    # ================= BICEP CURL =================
                    elif current_exercise == "bicep":
                        shoulder = landmarks[11]
                        elbow = landmarks[13]
                        wrist = landmarks[15]

                        angle = calculate_angle(
                            [shoulder.x, shoulder.y],
                            [elbow.x, elbow.y],
                            [wrist.x, wrist.y]
                        )

                        cv2.putText(frame, f"Curl Angle: {int(angle)}",
                                    (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 255, 255), 2)

                        if 60 < angle < 120:
                            cv2.putText(frame, "Full Curl!",
                                        (50, 150),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.8, (0, 0, 255), 2)



                    cv2.putText(frame, f"Reps: {session_counter}",
                                (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 0, 0), 2)



            except Exception as e:
                print("Pose detection error:", e)


            # ================= DRAW SKELETON =================
            if detection_result.pose_landmarks:
                for landmark in detection_result.pose_landmarks[0]:
                    h, w, _ = frame.shape
                    cx, cy = int(landmark.x * w), int(landmark.y * h)

                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

            POSE_CONNECTIONS = [
                (11, 13), (13, 15),   # Left arm
                (12, 14), (14, 16),   # Right arm
                (23, 25), (25, 27),   # Left leg
                (24, 26), (26, 28),   # Right leg
                (11, 12),             # Shoulders
                (23, 24),             # Hips
                (11, 23), (12, 24)    # Torso
            ]

            landmarks = detection_result.pose_landmarks[0]
            h, w, _ = frame.shape

            for connection in POSE_CONNECTIONS:
                start = landmarks[connection[0]]
                end = landmarks[connection[1]]

                x1, y1 = int(start.x * w), int(start.y * h)
                x2, y2 = int(end.x * w), int(end.y * h)

                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)


            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Camera released")



# model_path = "pose_landmarker.task"
model_path = os.path.join(MODELS_DIR, "pose_landmarker.task")

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO
)

pose_detector = PoseLandmarker.create_from_options(options)



@pose_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@pose_bp.route("/start_workout", methods=["POST"])
def start_workout():
    global current_exercise, session_counter, session_active

    current_exercise = request.form["exercise"]
    session_counter = 0
    session_active = True

    return ("", 204)


@pose_bp.route("/stop_workout", methods=["POST"])
def stop_workout():
    global session_active, session_counter, current_exercise

    session_active = False

    if current_exercise and session_counter > 0:
        conn = get_db_connection()
        cursor = conn.cursor()

        calories = round(session_counter * 0.5, 2)

        cursor.execute("""
            INSERT INTO workout_logs 
            (user_id, exercise_name, sets, reps, calories_burned)
            VALUES (%s, %s, %s, %s, %s)
        """, (session["user_id"], current_exercise, 1, session_counter, calories))

        conn.commit()
        cursor.close()
        conn.close()

    session_counter = 0
    current_exercise = None

    return ("", 204)