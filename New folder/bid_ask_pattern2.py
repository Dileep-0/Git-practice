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
    (df['ce_bid_ask_pr_diff'] > -0.09).astype(int)+
    (df['pe_bid_ask_diff'] < 0).astype(int)+
    (df['pe_bid_ask_pr_diff'] > -0.09).astype(int)
    ) >= 6

sell_side = (
    (df['n_bid_ask_diff'] > 0).astype(int)+
    (df['n_bid_ask_pr_diff'] < 0).astype(int)+
    (df['ce_bid_ask_diff'] > 0).astype(int)+
    (df['ce_bid_ask_pr_diff'] < 0.09).astype(int)+
    (df['pe_bid_ask_diff'] > 0).astype(int)+
    (df['pe_bid_ask_pr_diff'] < 0.09).astype(int)
    ) >= 6

matching_rows = df[buy_side | sell_side]
for index, row in matching_rows.iterrows():
    criteria = "Buy" if buy_side.iloc[index] else "Sell"
    print(f"{row['last_traded_time']} - {criteria}")

    ltp_ni_check = abs(ltp_price) > max(abs(bid_pr), abs(ask_pr))
            if ltp_ni_check:
                min_bid_ask = min(abs(bid_pr), abs(ask_pr))
                ltp_diff = abs(ltp_price) - min_bid_ask
                #print(ltp_diff)
                ltp_ni_check = 0.9 < ltp_diff < 5
            else:
                ltp_ni_check = False
            ltp_ce_check = abs(ltp_price_ce) > max(abs(bid_pr_ce), abs(ask_pr_ce))
            if ltp_ce_check:
                min_bid_ask_ce = min(abs(bid_pr_ce), abs(ask_pr_ce))
                ltp_diff_ce = abs(ltp_price_ce) - min_bid_ask_ce
                #print(ltp_diff_ce)
                ltp_ce_check = 0.45 < ltp_diff_ce < 3
            else:
                ltp_ce_check = False
            ltp_pe_check = abs(ltp_price_pe) > max(abs(bid_pr_pe), abs(ask_pr_pe))
            if ltp_pe_check:
                min_bid_ask_pe = min(abs(bid_pr_pe), abs(ask_pr_pe))
                ltp_diff_pe = abs(ltp_price_pe) - min_bid_ask_pe
                #print(ltp_diff_pe)
                ltp_pe_check = 0.45 < ltp_diff_pe < 3
            else:
                ltp_pe_check = False
        else:
            ltp_ni_check, ltp_ce_check, ltp_pe_check = False, False, False