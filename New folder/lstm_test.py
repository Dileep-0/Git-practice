import pandas as pd
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from tensorflow.keras.preprocessing.sequence import pad_sequences



# === Load the trained model ===
model = load_model("my_lstm_model.h5")  # Replace with your actual file path

# === Load new data ===
new_df = pd.read_csv("new_data.csv")  # Your new data file without 'result'
group_key = 'date'

# === Preprocess new data ===
# Drop irrelevant columns

df_features = new_df.drop(columns=['last_traded_time', 'date'])
feature_cols = [col for col in df_features.columns if col != group_key]

# === 2. Handle Categorical Columns ===
categorical_cols = df_features[feature_cols].select_dtypes(include=['object', 'string']).columns



with open("encoders.pkl", "rb") as f:
    encoders = pickle.load(f)
with open("feature_cols.pkl", "rb") as f:
    feature_cols = pickle.load(f)

print(new_df.columns.tolist())
print(feature_cols)


# Use the same encoders you used during training
for col in categorical_cols:
    new_df[col] = encoders[col].transform(new_df[col])


# Scale features using your original scaler
scaler = MinMaxScaler()
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

new_df[feature_cols] = scaler.transform(new_df[feature_cols])

# === Create sequences ===
window_size = 75
X_new_sequences = []

for i in range(len(new_df) - window_size + 1):
    window = new_df.iloc[i:i+window_size].values
    X_new_sequences.append(window)

# Pad just in case
X_new_padded = pad_sequences(X_new_sequences, maxlen=75, dtype='float32', padding='post', truncating='post')

# === Predict ===
predictions = model.predict(X_new_padded)


# === Display results ===
for i, probs in enumerate(predictions):
    pred_class = np.argmax(probs)
    confidence = np.max(probs)
    print(f"Sample {i+1} → Predicted Class: {pred_class} (Confidence: {confidence:.2f}) | Probabilities: {probs}")