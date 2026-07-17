import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras.models import load_model
import os

# Load model ONCE (important)
# model = keras.models.load_model("food_model.h5")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FOOD_MODEL_PATH = os.path.join(BASE_DIR, "models", "food_model.h5")

model = load_model(FOOD_MODEL_PATH)

# ⚠ Replace with your actual printed class order
CLASS_NAMES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit"
]

def predict_food(image_path):

    img = tf.keras.utils.load_img(
        image_path,
        target_size=(224, 224)
    )

    img_array = tf.keras.utils.img_to_array(img)
    img_array = img_array / 255.0   # normalize
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array)
    confidence = float(np.max(predictions))
    predicted_index = int(np.argmax(predictions))

    predicted_class = CLASS_NAMES[predicted_index]

    return predicted_class, confidence
