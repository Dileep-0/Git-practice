"""import os
from datetime import datetime
import pandas as pd
import numpy as np

def conversion(input_file):
    df = pd.read_csv(input_file)
    date, file_name = input_file.split("_", 1)
    
        # Correct Datetime format with seconds
    df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], errors='coerce')
    #df['adjusted_time'] = df['last_traded_time'] - pd.Timedelta(minutes=1)
    
    # Reindex the DataFrame to include all timestamps in the range
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
    #for name, group in df.groupby(pd.Grouper(key='adjusted_time', freq='5min')):
    for name, group in df.groupby(pd.Grouper(key='last_traded_time', freq='10s')):
        #updated_min = name + pd.Timedelta(minutes=1)
        selected_column = 'last_traded_time'
        differ = group.columns.difference([selected_column])
        numeric_columns = group[differ].select_dtypes(include=[np.number]).columns
        group_diff = group[numeric_columns].diff()


        columns_to_sum = group[numeric_columns]
        group_sum = columns_to_sum.sum()

        if not group.empty:
            open_value = group['ltp'].iloc[0] if 'ltp' in group else 0
            close_value = group['ltp'].iloc[-1] if 'ltp' in group else 0
            High_value = group['ltp'].max() if 'ltp' in group else 0
            Low_value = group['ltp'].min() if 'ltp' in group else 0

            # Calculate sums for relevant columns
        ltp = group_diff['ltp'].sum()
        volume = group_diff['vol_traded_today'].sum()
        bid = group_diff['bid_size'].sum()
        ask = group_diff['ask_size'].sum()
        bid_price = group_diff['bid_price'].sum()
        ask_price = group_diff['ask_price'].sum()
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
                'vol_traded_today': volume,     #1
                #'vol_sig' : signal,
                'bid_size' : bid,               #2
                'ask_size' : ask,               #3
                'bid_price' : bid_price,
                'ask_price' : ask_price,
                'last_traded_qty' : last_trade, #4
                #'last_traded_sig' : last_traded_sig,
                'tot_buy_qty': buy_qty,         #5
                'tot_buy_sig' : tot_buy_sig,
                'tot_sell_qty' : sell_qty,       #6
                'tot_sell_sig' : tot_sell_sig,
                'avg_trade_price': avg_trade,
                'Open_NSE:NIFTY50-INDEX':open_value,
                'Close_9':close_value,
                'High_9': High_value,
                'Low_9' : Low_value
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

    interval_str = f"{interval.components.minutes:02d}m"

        # Include interval in the filename and save aggregated data to CSV in the new directory
        #output_filename = os.path.join(output_dir, f"{date}_{interval_str}_{file_name}")
    output_filename = os.path.join(f"{date}_{interval_str}_{file_name}")
    aggregated_df.to_csv(output_filename, index=False)
        
    print(f"Saved aggregated data to {output_filename}")


# Prompt user to input filename and call the conversion function
filename = input('Enter filename with extension: ')
conversion(filename)"""
import os
from datetime import datetime
import pandas as pd
import numpy as np

def conversion(input_file):
    df = pd.read_csv(input_file)
    date, file_name = input_file.split("_", 1)
    
        # Correct Datetime format with seconds
    df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], dayfirst=False, errors='coerce')
    #df['adjusted_time'] = df['last_traded_time'] - pd.Timedelta(minutes=1)
    
    # Reindex the DataFrame to include all timestamps in the range
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
    #for name, group in df.groupby(pd.Grouper(key='adjusted_time', freq='5min')):
    for name, group in df.groupby(pd.Grouper(key='last_traded_time', freq='10s')):
        #updated_min = name + pd.Timedelta(minutes=1)
        selected_column = 'last_traded_time'
        differ = group.columns.difference([selected_column])
        numeric_columns = group[differ].select_dtypes(include=[np.number]).columns
        group_diff = group[numeric_columns].diff()


        columns_to_sum = group[numeric_columns]
        group_sum = columns_to_sum.sum()

        if not group.empty:
            open_value = group['ltp'].iloc[0] if 'ltp' in group else 0
            close_value = group['ltp'].iloc[-1] if 'ltp' in group else 0
            High_value = group['ltp'].max() if 'ltp' in group else 0
            Low_value = group['ltp'].min() if 'ltp' in group else 0

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
        '''bid_len = len(group['bid_price'])
        ask_len = len(group['ask_price'])
        bid_price  = group_sum['bid_price'] / bid_len
        ask_price  = group_sum['ask_price'] / ask_len

        bid_value = group['bid_size'].max()
        ask_value = group['ask_size'].max()'''
        avg_trade = group_diff['avg_trade_price'].sum()


        '''buy_qty = group_diff['tot_buy_qty'].sum()
            sell_qty = group_diff['tot_sell_qty'].sum()
            volume = group_diff['vol_traded_today'].sum()
            bid = group_sum['bid_size']
            ask = group_sum['ask_size']
            last_trade = group_sum['last_traded_qty']
            avg_trade = group_diff['avg_trade_price'].sum()'''

        #formatted_time = updated_min.strftime('%d-%m-%Y %H:%M:%S') if not pd.isnull(updated_min) else None
        formatted_time = name.strftime('%d-%m-%Y %H:%M:%S') if not pd.isnull(name) else None
            
        
                    


            # Create a row for each interval with the start time of the interval
        row = {
            'last_traded_time': formatted_time,  # Use the start time of the interval
                'ltp' : ltp,
                #'vol_sig' : signal,
                'tot_buy_qty': buy_qty,         #5
                'tot_sell_qty' : sell_qty,
                

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

    interval_str = f"{interval.components.minutes:02d}m"

        # Include interval in the filename and save aggregated data to CSV in the new directory
        #output_filename = os.path.join(output_dir, f"{date}_{interval_str}_{file_name}")
    output_filename = os.path.join(f"{date}_{interval_str}_{file_name}")
    aggregated_df.to_csv(output_filename, index=False)
        
    print(f"Saved aggregated data to {output_filename}")


# Prompt user to input filename and call the conversion function
filename = input('Enter filename with extension: ')
conversion(filename)
