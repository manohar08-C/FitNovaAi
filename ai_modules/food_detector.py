from ultralytics import YOLO
import cv2

# Load pretrained model
# model = YOLO("yolov8n.pt")

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "models", "yolov8n.pt")

model = YOLO(MODEL_PATH)

# Simple nutrition database
nutrition_data = {
    "banana": {"calories": 105, "protein": 1.3, "carbs": 27, "fats": 0.3},
    "apple": {"calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3},
    "pizza": {"calories": 285, "protein": 12, "carbs": 36, "fats": 10},
    "sandwich": {"calories": 250, "protein": 9, "carbs": 30, "fats": 8}
}

def detect_food(image_path):

    results = model(image_path)

    detected_items = []
    total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            if label in nutrition_data:
                detected_items.append(label)
                for key in total_nutrition:
                    total_nutrition[key] += nutrition_data[label][key]

    return detected_items, total_nutrition
