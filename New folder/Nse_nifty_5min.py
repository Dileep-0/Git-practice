import os
from datetime import datetime
import pandas as pd
import numpy as np

def conversion(input_file):
    df = pd.read_csv(input_file)
    date, file_name = input_file.split("_", 1)
    
        # Correct Datetime format with seconds
    df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], errors='coerce')
    #df['adjusted_time'] = df['last_traded_time'] - pd.Timedelta(minutes=1)

        
        # Round down to the nearest 5-minute boundary
        
    interval = pd.Timedelta(minutes=5)  # Define the time interval (5 minutes)

        # Initialize a list to store aggregated data
    aggregated_data = []
    #for name, group in df.groupby(pd.Grouper(key='adjusted_time', freq='5min')):
    for name, group in df.groupby(pd.Grouper(key='last_traded_time', freq=interval)):
        
        #updated_min = name + pd.Timedelta(minutes=1)
        selected_column = 'last_traded_time'
        differ = group.columns.difference([selected_column])
        numeric_columns = group[differ].select_dtypes(include=[np.number]).columns
        group_diff = group[numeric_columns].diff()


        columns_to_sum = group[numeric_columns]
        group_sum = columns_to_sum.sum()

        

            # Calculate sums for relevant columns
        
        ltp = group_diff['ltp'].sum()
        bid_price = group_diff['bid_price'].sum()
        ask_price = group_diff['ask_price'].sum()

        if 'ltp' in group and not group['ltp'].empty:
            open = group['ltp'].iloc[0]
        else:
            open = 0 
        if 'ltp' in group and not group['ltp'].empty:
            close = group['ltp'].iloc[-1]
        else:
            close = 0 
        if 'avg_trade_price' in group and not group['avg_trade_price'].empty:
            avg_trade = group['avg_trade_price'].iloc[-1]
        else:
            avg_trade = 0 
        

        volume = group_diff['vol_traded_today'].sum()

        bid = group_sum['bid_size']
        ask = group_sum['ask_size']
        bid_pr = group_sum['bid_price']
        ask_pr = group_sum['ask_price']

        bid_ask_diff = bid - ask

        bid_ask_pr_diff = bid_pr - ask_pr

        
        last_trade = group_sum['last_traded_qty']
        buy_qty = group_diff['tot_buy_qty'].sum()
        sell_qty = group_diff['tot_sell_qty'].sum()
        #avg_trade = group_diff['avg_trade_price'].sum()

        #formatted_time = updated_min.strftime('%d-%m-%Y %H:%M:%S') if not pd.isnull(updated_min) else None
        formatted_time = name.strftime('%d-%m-%Y %H:%M:%S') if not pd.isnull(name) else None
            
        senti="Buy" if bid > ask else "Sell"
        signal=''
        if volume > 30000:
            signal='Y'
        else:
            signal="N"

        last_traded_sig = 'N'  # Default value
        if aggregated_data:  # Check if there's any previous data to compare with
            previous_last_trade = aggregated_data[-1]['last_traded_qty']
            if (last_trade - previous_last_trade) > 100:
                last_traded_sig = 'Y'

        tot_buy_sig = 'N'
        tot_sell_sig = 'N'
                
        if aggregated_data:
            previous_tot_buy = aggregated_data[-1]['tot_buy_qty']
            previous_tot_sell = aggregated_data[-1]['tot_sell_qty']

                # First condition check
            if (buy_qty - previous_tot_buy) > 20000 and buy_qty > previous_tot_buy:
                tot_buy_sig = 'Y'
            elif buy_qty < 3000 and previous_tot_buy > buy_qty:
                tot_buy_sig = 'YES'

            if sell_qty < 3000 and previous_tot_sell > sell_qty: 
                tot_sell_sig = 'Y'
            elif (sell_qty - previous_tot_sell) >  20000 and sell_qty > previous_tot_sell:
                tot_sell_sig = 'YES'

            # Create a row for each interval with the start time of the interval
        row = {
            'last_traded_time': formatted_time,  # Use the start time of the interval
                'ltp' : ltp,
                #'vol_traded_today': volume,     #1
                #'vol_sig' : signal,
                'bid_price' : bid_price,               #2
                'ask_price' : ask_price,
                'n_bid_ask_diff' : bid_ask_diff,
                'n_bid_ask_pr_diff' : bid_ask_pr_diff,
                'last_traded_qty' : last_trade, #4
                #'last_traded_sig' : last_traded_sig,
                'tot_buy_qty': buy_qty,         #5
                'tot_buy_sig' : tot_buy_sig,
                'tot_sell_qty' : sell_qty,       #6
                'tot_sell_sig' : tot_sell_sig,
                'avg_trade_price': avg_trade,
                'Open_NSE:NIFTY50-INDEX' : open,
                'Close_9' : close
                #'sentiment' : senti

            }
   
        aggregated_data.append(row)

        # Create DataFrame from aggregated_data list
    aggregated_df = pd.DataFrame(aggregated_data)

    interval_str = f"{interval.components.minutes:02d}m"

        # Include interval in the filename and save aggregated data to CSV in the new directory
        #output_filename = os.path.join(output_dir, f"{date}_{interval_str}_{file_name}")
    output_filename = os.path.join(f"{date}_{interval_str}_{file_name}")
    aggregated_df.to_csv(output_filename, index=False)
        
    print(f"Saved aggregated data to {output_filename}")


# Prompt user to input filename and call the conversion function
filename = input('Enter filename with extension: ')
conversion(filename)
"""import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Bidirectional, LSTM, Dense, Dropout, Masking
from tensorflow.keras.preprocessing.sequence import pad_sequences

# === 1. Load CSV ===
file_path = "aggregated_master.csv"
df = pd.read_csv(file_path)

timestamps = df['last_traded_time'].values
group_key = 'date'
target = 'result'

df_features = df.drop(columns=['last_traded_time', 'date'])
feature_cols = [col for col in df_features.columns if col != group_key]

# === 2. Handle Categorical Columns ===
categorical_cols = df_features[feature_cols].select_dtypes(include=['object', 'string']).columns
encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df_features[col] = le.fit_transform(df_features[col])
    encoders[col] = le
with open("encoders.pkl", "wb") as f:
    pickle.dump(encoders, f)


feature_cols = df_features.columns.tolist()

# === 3. Normalize Features ===
scaler = MinMaxScaler()
df_features[feature_cols] = scaler.fit_transform(df_features[feature_cols])
scaler.fit(df_features[feature_cols])

with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open("feature_cols.pkl", "wb") as f:
    pickle.dump(feature_cols, f)



# === 4. Group by Day and Create Padded Sequences ===
window_size = 75
X_sequences = []
y_labels = []

for i in range(len(df) - window_size):
    window = df_features.iloc[i:i+window_size].values
    label = df[target].iloc[i + window_size]
    X_sequences.append(window)
    y_labels.append(label)

# Pad all sequences to 75 steps
X_padded = pad_sequences(X_sequences, maxlen=75, dtype='float32', padding='post', truncating='post')
y_array = np.array(y_labels)

label_encoder = LabelEncoder()
y_array = label_encoder.fit_transform(y_array)
unique, counts = np.unique(y_array, return_counts=True)
print("unique", dict(zip(unique, counts)))


X_train, X_test, y_train, y_test = train_test_split(X_padded, y_array, test_size=0.2, random_state=42)

num_features = X_padded.shape[2]

#[train_timestamps, test_timestamps]
timestamps_test = train_test_split(timestamps, test_size=0.2, random_state=42)[1]

model = Sequential()
model.add(Masking(mask_value=0., input_shape=(75, num_features)))
model.add(Bidirectional(LSTM(64)))
model.add(Dropout(0.2))
model.add(Dense(32, activation='relu'))
model.add(Dense(3, activation='softmax'))  # Change to match number of classes

model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

model.summary()

# === 8. Train ===
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))


# === 10. Evaluate ===
loss, metric = model.evaluate(X_test, y_test)
y_pred = model.predict(X_test)
print(f"Test Loss: {loss}, Test Metric: {metric}")
'''for ts, pred, actual in zip(timestamps_test, y_pred, y_test):
    pred_class = np.argmax(pred)
    print(f"Time: {ts}, Prediction: {pred}")
    print(f"  Predicted Class: {pred_class}, Actual Class: {actual}\n")'''
        
model.save("my_lstm_model.h5")

"""

"""import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, precision_recall_curve
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Conv1D, BatchNormalization, Activation, Add, GlobalAveragePooling1D, Dense, MultiHeadAttention, LayerNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import CustomObjectScope
import matplotlib.pyplot as plt
import seaborn as sns
from imblearn.over_sampling import RandomOverSampler


# === 1. Define Custom Objects ===
class WeightedFocalLoss(tf.keras.losses.Loss):

    def __init__(self, gamma=2.0, class_weights=None, name="weighted_focal_loss"):
        super().__init__(name=name)
        self.gamma = gamma
        self.class_weights = class_weights if class_weights is not None else {}

    def call(self, y_true, y_pred):
        y_true = tf.cast(y_true, tf.int32)
        ce = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=y_true, logits=y_pred)
        pt = tf.exp(-ce)
        weights = tf.gather(list(self.class_weights.values()), y_true)
        loss = weights * tf.pow(1 - pt, self.gamma) * ce
        return tf.reduce_mean(loss)

    def get_config(self):
        return {"gamma": self.gamma, "class_weights": self.class_weights}


class ThresholdModel(tf.keras.Model):

    def __init__(self, base_model, thresholds, **kwargs):
        super().__init__(**kwargs)
        self.base_model = base_model
        self.thresholds = thresholds

    def call(self, inputs):
        logits = self.base_model(inputs)
        return tf.nn.softmax(logits)

    def predict_with_thresholds(self, X):
        probs = self.predict(X)
        predictions = np.zeros_like(probs)
        for class_idx, threshold in self.thresholds.items():
            predictions[:, class_idx] = (probs[:, class_idx] >= threshold).astype(int)
        return np.argmax(predictions * probs, axis=1)

    def get_config(self):
        config = super().get_config()
        config.update({
            "base_model": tf.keras.models.clone_model(self.base_model),
            "thresholds": self.thresholds
        })
        return config

    @classmethod
    def from_config(cls, config):
        # First create the base model
        base_model = Model.from_config(config['base_model'].get_config())
        # Then create the ThresholdModel instance
        return cls(base_model, config['thresholds'])


# Register custom objects
custom_objects = {
    'WeightedFocalLoss': WeightedFocalLoss,
    'ThresholdModel': ThresholdModel
}

# === 2. Data Loading and Preprocessing ===
print("Loading data...")
df = pd.read_csv("aggregated_master.csv")

# Prepare features and target
df_features = df.drop(columns=['date'])
df_features['last_traded_time'] = pd.to_datetime(df_features['last_traded_time'], dayfirst=True)
df_features['last_traded_time'] = df_features['last_traded_time'].astype('int64') / 1e9


target = 'result'

# Encode categorical features
categorical_cols = df_features.select_dtypes(include=['object', 'string']).columns
for col in categorical_cols:
    df_features[col] = LabelEncoder().fit_transform(df_features[col])

# Normalize features
scaler = MinMaxScaler()
feature_cols = [col for col in df_features.columns if col != target]
df_features[feature_cols] = scaler.fit_transform(df_features[feature_cols])

# === 3. Create Sequences ===
window_size = 75
X_sequences = []
y_labels = []

for i in range(len(df) - window_size):
    window = df_features.iloc[i:i + window_size].values
    label = df[target].iloc[i + window_size]
    X_sequences.append(window)
    y_labels.append(label)


X_padded = np.array(X_sequences)
y_array = np.array(y_labels)

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y_array)
num_classes = len(label_encoder.classes_)
num_features = X_padded.shape[2]

print(f"Input shape: {X_padded.shape}")
print("Class distribution:", {cls: count for cls, count in zip(label_encoder.classes_, np.bincount(y_encoded))})

# === 4. Data Augmentation for Minority Classes ===
n_samples, n_timesteps, n_features = X_padded.shape
X_flat = X_padded.reshape(n_samples, -1)
ros = RandomOverSampler(random_state=42)
X_resampled, y_resampled = ros.fit_resample(X_flat, y_encoded)
X_resampled = X_resampled.reshape(-1, n_timesteps, n_features)

timestamp_idx = feature_cols.index('last_traded_time')

# Extract timestamp at the **last time step** of each window
timestamps = X_resampled[:, -1, timestamp_idx]
timestamps = pd.to_datetime(timestamps * 1e9)

# === 5. Train/Validation/Test Split ===
X_train, X_temp, y_train, y_temp, timestamps_train, timestamps_temp = train_test_split(
    X_resampled, y_resampled, timestamps, test_size=0.3, random_state=42, stratify=y_resampled)
X_val, X_test, y_val, y_test, timestamps_val, timestamps_test = train_test_split(
    X_temp, y_temp, timestamps_temp, test_size=0.5, random_state=42, stratify=y_temp)


# === 6. Build Hybrid TCN + Attention Model ===
def residual_block(x, filters, kernel_size, dilation_rate):
    shortcut = x
    print('shortcut', shortcut)
    x = Conv1D(filters, kernel_size, padding='same', dilation_rate=dilation_rate)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Conv1D(filters, kernel_size, padding='same', dilation_rate=dilation_rate)(x)
    x = BatchNormalization()(x)

    if shortcut.shape[-1] != filters:
        shortcut = Conv1D(filters, 1, padding='same')(shortcut)
        print("shorts", shortcut)

    x = Add()([shortcut, x])
    print("x2", x)
    return Activation('relu')(x)


inputs = Input(shape=(window_size, num_features))
x = Conv1D(64, 3, padding='same')(inputs)

print("xs", x)

for dilation_rate in [1, 2, 4]:
    x = residual_block(x, 64, 3, dilation_rate)

attention_output = MultiHeadAttention(num_heads=4, key_dim=64)(x, x)
x = LayerNormalization()(Add()([x, attention_output]))
x = GlobalAveragePooling1D()(x)
x = Dense(128, activation='relu')(x)
logits = Dense(num_classes, activation='linear')(x)
base_model = Model(inputs, logits)

# === 7. Training ===
class_counts = np.bincount(y_train)
class_weights = len(y_train) / (num_classes * class_counts)
class_weights_dict = {i: weight for i, weight in enumerate(class_weights)}

base_model.compile(
    optimizer=Adam(learning_rate=0.0005, clipvalue=0.5),
    loss=WeightedFocalLoss(gamma=2.0, class_weights=class_weights_dict),
    metrics=['accuracy']
)

history = base_model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=150,
    batch_size=64,
    callbacks=[
        EarlyStopping(monitor='val_accuracy', patience=20, restore_best_weights=True),
        ModelCheckpoint('best_model.h5', monitor='val_accuracy', save_best_only=True)
    ],
    verbose=1
)


# === 8. Evaluation ===
def plot_confusion_matrix(y_true, y_pred, title):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=label_encoder.classes_,
                yticklabels=label_encoder.classes_)
    plt.title(title)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()


# Training data evaluation
y_train_pred = np.argmax(base_model.predict(X_train), axis=1)
print("\n=== Training Data ===")
print("Classification Report:")
print(classification_report(y_train, y_train_pred, target_names=[str(cls) for cls in label_encoder.classes_]))
plot_confusion_matrix(y_train, y_train_pred, "Training Data Confusion Matrix")

# Test data evaluation
y_test_pred = np.argmax(base_model.predict(X_test), axis=1)
print("\n=== Test Data ===")
print("Classification Report:")
print(classification_report(y_test, y_test_pred, target_names=[str(cls) for cls in label_encoder.classes_]))
plot_confusion_matrix(y_test, y_test_pred, "Test Data Confusion Matrix")

for ts, pred, actual in zip(timestamps_test, y_test_pred, y_test):
    pred_class = np.argmax(pred)
    print(f"Time: {ts}, Prediction: {pred}")
    print(f"  Predicted Class: {pred_class}, Actual Class: {actual}\n")

# === 9. Threshold Optimization ===
logits_val = base_model.predict(X_val)
probs_val = tf.nn.softmax(logits_val).numpy()

thresholds = {}
for class_idx in range(num_classes):
    precision, recall, thresh = precision_recall_curve(
        (y_val == class_idx).astype(int),
        probs_val[:, class_idx]
    )
    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-6)
    thresholds[class_idx] = thresh[np.argmax(f1_scores)]

print("\nOptimal thresholds per class:")
for class_idx, class_name in enumerate(label_encoder.classes_):
    print(f"{class_name}: {thresholds[class_idx]:.3f}")

# === 10. Create and Save Final Model ===
final_model = ThresholdModel(base_model, thresholds)

with CustomObjectScope(custom_objects):
    final_model.save("final_model.h5")
    print("\nModel saved to 'final_model.h5'")"""