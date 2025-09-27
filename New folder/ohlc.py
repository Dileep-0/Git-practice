from fyers_apiv3 import fyersModel
import pandas as pd
import time as time_module
import numpy as np
from fyers_apiv3.FyersWebsocket import data_ws
from datetime import datetime, timedelta, time, timezone
import pytz
import sys
import os

sys.path.append(os.path.abspath("../../ce copy"))
import variable

data_buffer = []
aggregation_interval = 5  # in minutes
next_aggregation_time = None


# Access token and client ID
access_token =  variable.token
client_id = "DEEYXXPP9Z-100"

import filenames
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


# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

data = {
    "symbol":"NSE:NIFTY50-INDEX",
    "resolution":"5",
    "date_format":"0",
    "range_from":str(range_from_ts),
    "range_to": str(range_to_ts),
    "cont_flag":"1"
}

response = fyers.history(data=data)
#print(response)
if response.get("s") == "ok" and "candles" in response:
    candles = response["candles"]
    
    # Convert to DataFrame
    df = pd.DataFrame(candles, columns=[
        "timestamp", "open", "high", "low", "close", "volume"
    ])
    
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", errors='coerce')  # Default: UTC
    # To convert to IST
    df["datetime"] = df["datetime"].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
    df["datetime"] = df["datetime"].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Reorder columns (optional)
    df = df[["datetime", "open", "high", "low", "close", "volume"]]
    file = f"{date}_nifty50_ohlc.csv"

    # Save to CSV
    df.to_csv(file, index=False)
    print(f"CSV saved as {file}")
else:
    print("Failed to retrieve data:", response)
