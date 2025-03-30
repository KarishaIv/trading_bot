import os
import numpy as np
from tqdm import tqdm
import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dropout, Rescaling
from tensorflow.keras.preprocessing import image_dataset_from_directory

IMG_SIZE = (100, 100)
BATCH_SIZE = 32
TIMEFRAME = "1d"
WEIGHTS_PATH = "../cnn/cnn_model.keras"
DATASET_PATH = "../cnn/images/training_dataset"

def build_cnn_feature_extractor(input_shape):
    inputs = Input(shape=input_shape)
    x = Rescaling(1. / 255)(inputs)

    x = Conv2D(32, (3, 3), activation='relu')(x)
    x = MaxPooling2D(2, 2)(x)

    x = Conv2D(64, (3, 3), activation='relu')(x)
    x = MaxPooling2D(2, 2)(x)

    x = Conv2D(128, (3, 3), activation='relu')(x)
    x = MaxPooling2D(2, 2)(x)

    x = Flatten()(x)
    x = Dropout(0.3)(x)
    return Model(inputs, x, name="cnn_feature_extractor")

model = build_cnn_feature_extractor((*IMG_SIZE, 3))
model.load_weights(WEIGHTS_PATH, skip_mismatch=True)

image_ds = image_dataset_from_directory(
    DATASET_PATH,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

all_features, all_labels = [], []

for batch_images, batch_labels in tqdm(image_ds):
    features = model(batch_images, training=False).numpy()
    all_features.append(features)
    all_labels.append(batch_labels.numpy())

cnn_features = np.vstack(all_features)
cnn_labels = np.concatenate(all_labels)

np.save(f"cnn_features.npy", cnn_features)
np.save(f"cnn_labels.npy", cnn_labels)

