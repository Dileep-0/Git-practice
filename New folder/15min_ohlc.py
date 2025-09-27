from fyers_apiv3 import fyersModel
import pandas as pd
from datetime import datetime, time
import pytz
import sys
import os

sys.path.append(os.path.abspath("../../ce copy"))
import variable
import filenames

# Access token and client ID
access_token = variable.token
client_id = "DEEYXXPP9Z-100"

sym = filenames.signals
date, file_name = sym.split("_", 1)
print(date)

trade_date = datetime.strptime(date, "%d-%m-%Y").date()

# Define IST timezone
ist = pytz.timezone("Asia/Kolkata")

# Create datetime objects in IST
start_dt_ist = ist.localize(datetime.combine(trade_date, time(9, 15, 0)))
end_dt_ist = ist.localize(datetime.combine(trade_date, time(15, 30, 0)))

# Convert to UTC timestamps (seconds since epoch)
range_from_ts = int(start_dt_ist.astimezone(pytz.UTC).timestamp())
range_to_ts = int(end_dt_ist.astimezone(pytz.UTC).timestamp())

# Initialize the FyersModel instance
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

data = {
    "symbol": "NSE:INDIAVIX-INDEX",
    "resolution": "5",   # fetch 5-minute data
    "date_format": "0",
    "range_from": str(range_from_ts),
    "range_to": str(range_to_ts),
    "cont_flag": "1"
}

response = fyers.history(data=data)

if response.get("s") == "ok" and "candles" in response:
    candles = response["candles"]
    
    # Convert to DataFrame
    df = pd.DataFrame(candles, columns=[
        "timestamp", "open", "high", "low", "close", "volume"
    ])
    
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", errors='coerce')  # UTC
    df["datetime"] = df["datetime"].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
    
    # Set datetime as index
    df.set_index("datetime", inplace=True)

    df_15m_list = []

    # Window = 3 rows (since 3 × 5min = 15min)
    window_size = 3

    for i in range(len(df) - window_size + 1):
        window = df.iloc[i:i+window_size]

        agg_row = {
            "datetime": window.index[-1],  # end of the window
            "open": window["open"].iloc[0],
            "high": window["high"].max(),
            "low": window["low"].min(),
            "close": window["close"].iloc[-1],
            "volume": window["volume"].sum()
        }
        df_15m_list.append(agg_row)

    df_15m = pd.DataFrame(df_15m_list)


    df.reset_index(inplace=True)
    

    # Format datetime for saving
    df["datetime"] = df["datetime"].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_15m["datetime"] = df_15m["datetime"].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Save original 5-min data
    file_5m = f"{date}_nifty50_5m.csv"
    df.to_csv(file_5m, index=False)

    # Save aggregated 15-min data
    file_15m = f"{date}_nifty50_15m.csv"
    df_15m.to_csv(file_15m, index=False)

    print(f"CSV saved as {file_5m} and {file_15m}")
else:
    print("Failed to retrieve data:", response)
