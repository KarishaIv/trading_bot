import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Dense, Dropout, Concatenate
from tensorflow.keras.optimizers import Adam
from sklearn.utils.class_weight import compute_class_weight


cnn_features = np.load("cnn_features.npy")
lstm_features = np.load("lstm_features.npy")
labels = np.load("cnn_labels.npy")

N = min(len(cnn_features), len(lstm_features), len(labels))
cnn_features = cnn_features[:N]
lstm_features = lstm_features[:N]
labels = labels[:N]


X_cnn_train, X_cnn_test, X_lstm_train, X_lstm_test, y_train, y_test = train_test_split(
    cnn_features, lstm_features, labels, test_size=0.2, random_state=42, stratify=labels
)
#чтобы снова не обучать
exit(777)
def build_fusion_model(cnn_dim, lstm_dim):
    cnn_input = Input(shape=(cnn_dim,))
    lstm_input = Input(shape=(lstm_dim,))

    x1 = Dense(64, activation="relu")(cnn_input)
    x2 = Dense(64, activation="relu")(lstm_input)

    fusion = Concatenate()([x1, x2])
    x = Dropout(0.3)(fusion)
    x = Dense(64, activation="relu")(x)
    output = Dense(1, activation="sigmoid")(x)

    return Model(inputs=[cnn_input, lstm_input], outputs=output)

model = build_fusion_model(cnn_features.shape[1], lstm_features.shape[1])
model.compile(optimizer=Adam(0.0005), loss="binary_crossentropy", metrics=["accuracy"])


classes = np.unique(y_train)
class_weights = compute_class_weight(class_weight='balanced', classes=classes, y=y_train)
class_weight_dict = dict(zip(classes, class_weights))

history = model.fit(
    [X_cnn_train, X_lstm_train], y_train,
    validation_data=([X_cnn_test, X_lstm_test], y_test),
    epochs=25,
    batch_size=32,
    class_weight=class_weight_dict,
    verbose=2
)

model.save("fusion_model.keras")

y_pred_prob = model.predict([X_cnn_test, X_lstm_test])
y_pred = (y_pred_prob > 0.5).astype(int).flatten()

report = classification_report(y_test, y_pred, target_names=["DOWN", "UP"])

print("Classification Report:")
print(report)

with open("fusion_classification_report.txt", "w") as f:
    f.write(report)

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["DOWN", "UP"], yticklabels=["DOWN", "UP"])
plt.title("Fusion Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig("fusion_confusion_matrix.png", dpi=150)
plt.show()

