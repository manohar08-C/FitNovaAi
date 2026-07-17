import tensorflow as tf

train_dataset = tf.keras.utils.image_dataset_from_directory(
    "dataset/train",
    image_size=(224, 224),
    batch_size=32,
    label_mode="categorical"
)

class_names = train_dataset.class_names

print("Class Order:")
for i, name in enumerate(class_names):
    print(i, "→", name)
