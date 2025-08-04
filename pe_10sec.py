import os
from datetime import datetime
import pandas as pd
import numpy as np

def conversion(input_file):
    df = pd.read_csv(input_file)
    date, file_name = input_file.split("_", 1)
    
    # Correct Datetime format with seconds
    df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], errors='coerce')

    df.rename(columns={'index': 'last_traded_time'}, inplace=True)
    
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Add placeholder values for non-numeric columns (if any exist)
    non_numeric_columns = df.select_dtypes(exclude=[np.number]).columns
    df[non_numeric_columns] = df[non_numeric_columns].fillna("")
    
    # Round down to the nearest 5-minute boundary
    
    interval = pd.Timedelta(seconds=10)  # Define the time interval (5 minutes)

    # Initialize a list to store aggregated data
    aggregated_data = []
    for name, group in df.groupby(pd.Grouper(key='last_traded_time', freq='10s')):
        selected_column = 'last_traded_time'
        differ = group.columns.difference([selected_column])
        numeric_columns = group[differ].select_dtypes(include=[np.number]).columns
        group_diff = group[numeric_columns].diff()

        columns_to_sum = group.drop(columns=[selected_column])
        group_sum = columns_to_sum.sum()

        # Calculate sums for relevant columns
        if 'ltp' in group and not group['ltp'].empty:
            ltp = group['ltp'].iloc[-1]
        else:
            ltp = 0
        if 'tot_buy_qty' in group and not group['tot_buy_qty'].empty:
            buy_qty = group['tot_buy_qty'].max()
        else:
            buy_qty = 0
        if 'tot_sell_qty' in group and not group['tot_sell_qty'].empty:
            sell_qty = group['tot_sell_qty'].max()
        else:
            sell_qty = 0
        """volume = group_diff['vol_traded_today'].sum()
        bid = group_diff['bid_size'].sum()
        ask = group_diff['ask_size'].sum()
        bid_price = group_diff['bid_price'].sum()
        ask_price = group_diff['ask_price'].sum()
        last_trade = group_sum['last_traded_qty']
        buy_qty = group_diff['tot_buy_qty'].sum()
        avg_trade = group_diff['avg_trade_price'].sum()

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
                tot_sell_sig = 'YES'"""
                

        # Create a row for each interval with the start time of the interval
        row = {
            'last_traded_time': name,  # Use the start time of the interval
            'ltp' : ltp,
            'tot_buy_qty': buy_qty,         #5
            'tot_sell_qty' : sell_qty,
            #'sentiment' : senti
        }

        aggregated_data.append(row)

    # Create DataFrame from aggregated_data list
    aggregated_df = pd.DataFrame(aggregated_data)

    # Create a string for interval minutes (e.g., '05m')
    interval_str = f"{interval.components.minutes:02d}m"

    # Include interval in the filename and save aggregated data to CSV in the new directory
    output_filename = os.path.join(f"{date}_{interval_str}_{file_name}")
    aggregated_df.to_csv(output_filename, index=False)
    
    print(f"Saved aggregated data to {output_filename}")

filename = input('Enter filename with extension: ')
conversion(filename)
