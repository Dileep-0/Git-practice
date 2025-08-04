import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# === Configuration ===
CSV_FILE = "new_aggregated_master.csv"       # Your live data file
MODEL_PATH = "final_model.keras"              # Saved base model (not ThresholdModel)
THRESHOLDS = {0: 0.125, 1: 0.0851, 2: 0.889}         # Replace with your actual thresholds
CLASS_NAMES = ['loss', 'neutral', 'win']  # Replace with your actual class labels
WINDOW_SIZE = 75

# === Load and preprocess data ===
df = pd.read_csv(CSV_FILE)
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], dayfirst=True)

# Drop non-numeric timestamp
timestamps = df['last_traded_time'].values
df = df.drop(columns=['last_traded_time'])

# Encode categorical columns (you should reuse saved encoders in production)
cat_cols = df.select_dtypes(include=['object', 'string']).columns
for col in cat_cols:
    df[col] = LabelEncoder().fit_transform(df[col])

# Normalize features (you should reuse saved scaler in production)
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df)

# === Check if enough rows exist ===
if df_scaled.shape[0] < WINDOW_SIZE:
    print(f"❌ Not enough data. Found {df_scaled.shape[0]} rows, need at least {WINDOW_SIZE}.")
    exit()

# === Get latest 75 rows ===
latest_window = df_scaled[-WINDOW_SIZE:]
X_input = latest_window.reshape(1, WINDOW_SIZE, df_scaled.shape[1])

# === Load base model ===
base_model = load_model(MODEL_PATH, custom_objects={"WeightedFocalLoss": tf.keras.losses.Loss})

# === Predict probabilities ===
logits = base_model.predict(X_input)
probs = tf.nn.softmax(logits).numpy()[0]

# === Apply thresholds manually ===
pred_mask = np.array([(p >= THRESHOLDS[i]) for i, p in enumerate(probs)], dtype=int)
final_class = np.argmax(pred_mask * probs)

# === Decode class name ===
label_encoder = LabelEncoder()
label_encoder.fit(CLASS_NAMES)
predicted_class = label_encoder.inverse_transform([final_class])[0]

# === Output prediction ===
latest_time = timestamps[-1]
print(f"🕒 Time: {latest_time}")
print(f"🔮 Prediction: {probs}")
print(f"✅ Predicted Class: {predicted_class}")

