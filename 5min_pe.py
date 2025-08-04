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
    
    interval = pd.Timedelta(minutes=5)  # Define the time interval (5 minutes)

    # Initialize a list to store aggregated data
    aggregated_data = []
    for name, group in df.groupby(pd.Grouper(key='last_traded_time', freq=interval)):
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
        volume = group_diff['vol_traded_today'].sum()
        bid = group_sum['bid_size']
        ask = group_sum['ask_size']
        bid_ask_diff = bid - ask

        bid_pr_max, ask_pr_max = group['bid_price'].max(), group['ask_price'].max()
        bid_pr_min, ask_pr_min = group['bid_price'].min(), group['ask_price'].min()

        bid_pr_diff = bid_pr_max - bid_pr_min
        ask_pr_diff = ask_pr_max - ask_pr_min

        bid_ask_pr_diff = bid_pr_diff - ask_pr_diff
        last_trade = group_sum['last_traded_qty']
        buy_qty = group_diff['tot_buy_qty'].sum()
        sell_qty = group_diff['tot_sell_qty'].sum()
        avg_trade = group_diff['avg_trade_price'].sum()

        '''buy_qty = group_diff['tot_buy_qty'].sum()
        sell_qty = group_diff['tot_sell_qty'].sum()
        volume = group_diff['vol_traded_today'].sum()
        bid = group_sum['bid_size']
        ask = group_sum['ask_size']
        last_trade = group_sum['last_traded_qty']
        avg_trade = group_diff['avg_trade_price'].sum()'''

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

        '''row = {
            'last_traded_time': name,
            'bid_ask_diff' : bid_ask_diff,
            'bid_ask_pr_diff' : bid_ask_pr_diff,
        }'''
                

        # Create a row for each interval with the start time of the interval
        row = {
            'last_traded_time': name,  # Use the start time of the interval
            'ltp' : ltp,
            #'vol_traded_today': volume,     #1
            #'vol_sig' : signal,
            #'bid_size' : bid,               #2
            #'ask_size' : ask,
            'pe_bid_ask_diff' : bid_ask_diff,
            'pe_bid_ask_pr_diff' : bid_ask_pr_diff,
            'last_traded_qty' : last_trade, #4
            #'last_traded_sig' : last_traded_sig,
            'tot_buy_qty': buy_qty,         #5
            'tot_buy_sig' : tot_buy_sig,
            'tot_sell_qty' : sell_qty,       #6
            'tot_sell_sig' : tot_sell_sig,
            'avg_trade_price': avg_trade
            #'sentiment' : senti
        }

        '''row = {
                'last_traded_time': name,  # Use the start time of the interval
                'vol_traded_today': volume,     #1
                'vol_sig' : signal,
                'bid_size' : bid,               #2
                'ask_size' : ask,               #3
                'last_traded_qty' : last_trade, #4
                'last_traded_sig' : last_traded_sig,
                'tot_buy_qty': buy_qty,         #5
                'tot_buy_sig' : tot_buy_sig,
                'tot_sell_qty' : sell_qty,       #6
                'tot_sell_sig' : tot_sell_sig,
                'avg_trade_price': avg_trade
                #'sentiment' : senti
            }'''
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
    interval_str = f"{interval.components.minutes:02d}m"

    # Include interval in the filename and save aggregated data to CSV in the new directory
    output_filename = os.path.join(f"{date}_{interval_str}_{file_name}")
    aggregated_df.to_csv(output_filename, index=False)
    
    print(f"Saved aggregated data to {output_filename}")


# Prompt user to input filename and call the conversion function
filename = input('Enter filename with extension: ')
conversion(filename)
