from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

from  config import MODEL_PATH_CNN


cnn_model = load_model(MODEL_PATH_CNN)
IMG_SIZE = (100, 100)


def predict_cnn_from_image(image_path: str) -> str:
    img = image.load_img(image_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    preds = cnn_model.predict(img_array)
    pred_class = np.argmax(preds, axis=1)[0]
    return "UP" if pred_class == 1 else "DOWN"
