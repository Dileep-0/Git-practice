import os
from datetime import datetime
import pandas as pd
import numpy as np

def conversion(input_file):
    df = pd.read_csv(input_file)
    date, file_name = input_file.split("_", 1)
    
    # Correct Datetime format with seconds
    df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], errors='coerce')
    
    # Round down to the nearest 5-minute boundary
    
    df['interval_start'] = df['last_traded_time'].dt.floor('5min')

    # Initialize a list to store aggregated data
    aggregated_data = []
    for interval_start in df['interval_start'].unique():
        interval_end = interval_start + pd.Timedelta(minutes=15)

        # Slice last 15-minutes window
        group = df[(df['last_traded_time'] >= interval_start) &
                   (df['last_traded_time'] < interval_end)]
        formatted_time = interval_end.strftime('%d-%m-%Y %H:%M:%S') if not pd.isnull(interval_end) else None
        selected_column = 'last_traded_time'
        differ = group.columns.difference([selected_column])
        numeric_columns = group[differ].select_dtypes(include=[np.number]).columns
        group_diff = group[numeric_columns].diff()

        columns_to_sum = group[numeric_columns]
        group_sum = columns_to_sum.sum()

        # Calculate sums for relevant columns
        ltp = group_diff['ltp'].sum()
        if 'ltp' in group and not group['ltp'].empty:
            open = group['ltp'].iloc[0]
        else:
            open = 0
        if 'ltp' in group and not group['ltp'].empty:
            close = group['ltp'].iloc[-1]
        else:
            close = 0
        high = group['ltp'].max()
        low = group['ltp'].min()
        bid_price = group_diff['bid_price'].sum()
        ask_price = group_diff['ask_price'].sum()
        volume = group_diff['vol_traded_today'].sum()
        volume_count = group_diff['vol_traded_today']
        non_zero_count = (volume_count != 0).sum()
        ch = group_diff['ch'].sum()
        bid = group_sum['bid_size']
        ask = group_sum['ask_size']
        bid_pr = group_sum['bid_price']
        ask_pr = group_sum['ask_price']
        
        bid_ask_diff = bid - ask

        bid_ask_pr_diff = bid_pr - ask_pr
        last_trade = group_sum['last_traded_qty']
        buy_qty = group_diff['tot_buy_qty'].sum()
        sell_qty = group_diff['tot_sell_qty'].sum()
        if 'avg_trade_price' in group and not group['avg_trade_price'].empty:
            avg_trade = group['avg_trade_price'].iloc[-1]
        else:
            avg_trade = 0 


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

            #first condition check(BUY signal)
            
        if aggregated_data:
            previous_tot_buy = aggregated_data[-1]['tot_buy_qty']
            previous_tot_sell = aggregated_data[-1]['tot_sell_qty']



            # First condition check
            if buy_qty < 3000 and previous_tot_buy > buy_qty:
                tot_buy_sig = 'Y'

            elif (buy_qty - previous_tot_buy) > 20000 and previous_tot_buy < buy_qty:
                tot_buy_sig = 'YES'

            if (sell_qty - previous_tot_sell) > 20000 and sell_qty > previous_tot_sell:
                tot_sell_sig = 'Y'
            
            elif sell_qty < 3000 and sell_qty < previous_tot_sell:
                tot_sell_sig = 'YES'
                

        # Create a row for each interval with the start time of the interval
        row = {
            'last_traded_time': formatted_time,  # Use the start time of the interval
            'ltp' : ltp,
            'vol_traded_today': volume,     #1
            'non_zero_vol' : non_zero_count,
            'bid' : bid,
            'ask' : ask,
            'bid_price' : bid_price,               #2
            'ask_price' : ask_price,
            'pe_bid_ask_diff' : bid_ask_diff,
            'pe_bid_ask_pr_diff' : bid_ask_pr_diff,
            'last_traded_qty' : last_trade, #4
            #'last_traded_sig' : last_traded_sig,
            'tot_buy_qty': buy_qty,         #5
            'tot_buy_sig' : tot_buy_sig,
            'tot_sell_qty' : sell_qty,       #6
            'tot_sell_sig' : tot_sell_sig,
            'open_3' : open,
            'close_3' : close,
            'high' : high,
            'low' : low,
            'avg_trade_price': avg_trade
            #'sentiment' : senti
        }

        
        aggregated_data.append(row)

    # Create DataFrame from aggregated_data list
    aggregated_df = pd.DataFrame(aggregated_data)

    # Create a string for interval minutes (e.g., '05m')
    '''base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = base_name

    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)'''

    # Create a string for interval minutes (e.g., '05m')
    interval_str = '15m'

    # Include interval in the filename and save aggregated data to CSV in the new directory
    output_filename = os.path.join(f"{date}_{interval_str}_{file_name}")
    aggregated_df.to_csv(output_filename, index=False)
    
    print(f"Saved aggregated data to {output_filename}")


# Prompt user to input filename and call the conversion function
filename = input('Enter filename with extension: ')
conversion(filename)
