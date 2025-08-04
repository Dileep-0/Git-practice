import os
import pandas as pd

import filenames

file_path = filenames.signals
# Load the CSV file
df = pd.read_csv(file_path)
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], dayfirst=True, errors='coerce')

#pattern of bid, ask sizes and prices for buy side 
buy_side = (
    (df['n_bid_ask_diff'] < 0).astype(int)+
    (df['n_bid_ask_pr_diff'] > 0).astype(int)+
    (df['ce_bid_ask_diff'] < 0).astype(int)+
    (df['ce_bid_ask_pr_diff'] > 0).astype(int)+
    (df['pe_bid_ask_diff'] < 0).astype(int)+
    (df['pe_bid_ask_pr_diff'] > 0).astype(int)
    ) >= 4

sell_side = (
    (df['n_bid_ask_diff'] > 0).astype(int)+
    (df['n_bid_ask_pr_diff'] < 0).astype(int)+
    (df['ce_bid_ask_diff'] > 0).astype(int)+
    (df['ce_bid_ask_pr_diff'] < 0).astype(int)+
    (df['pe_bid_ask_diff'] > 0).astype(int)+
    (df['pe_bid_ask_pr_diff'] < 0).astype(int)
    ) >= 4

matching_rows = df[buy_side | sell_side]
for index, row in matching_rows.iterrows():
    criteria = "Buy" if buy_side.iloc[index] else "Sell"
    print(f"{row['last_traded_time']} - {criteria}")