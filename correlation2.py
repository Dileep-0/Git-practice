import pandas as pd

# Load the CSV file
input_file = '17-03-2025_00m_NIFTY25MARFUT.csv'
df = pd.read_csv(input_file)
date, file_name = input_file.split("_", 1)

# Convert the 'last_traded_time' column to datetime format
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'])

# Set 'last_traded_time' as the index (optional, but helps in time-based operations)
df.set_index('last_traded_time', inplace=True)

# List of column pairs to correlate

# Prepare an empty list to store the correlation data
correlation_data = []
interval = pd.Timedelta(minutes=5)

# Iterate through the data, group by minute, and calculate correlations
for timestamp, group in df.resample('5min'):

    filtered_group = group[(group[['ltp', 'tot_buy_qty', 'tot_sell_qty']] != 0).all(axis=1)]
    filtered_group = filtered_group.copy()
    filtered_group['buy_sell_diff'] = filtered_group['tot_buy_qty'] - filtered_group['tot_sell_qty']
    filtered_group['ce_buy_sell_diff'] = filtered_group['tot_buy_qty.1'] - filtered_group['tot_sell_qty.1']
    filtered_group['pe_buy_sell_diff'] = filtered_group['tot_buy_qty.2'] - filtered_group['tot_sell_qty.2']
    # Initialize a dictionary to store the correlation values for this timestamp
    correlation_values = {'last_traded_time': timestamp.strftime('%d-%m-%Y %H:%M')}

    
    # Calculate the correlation for each column pair
    correlation_values['n_buy_corr'] = filtered_group[['ltp', 'tot_buy_qty']].corr().iloc[0, 1]  # ltp vs tot_buy_qty
    correlation_values['n_sell_corr'] = filtered_group[['ltp', 'tot_sell_qty']].corr().iloc[0, 1]  # ltp vs tot_sell_qty
    correlation_values['buy_sell_diff'] = filtered_group[['ltp', 'buy_sell_diff']].corr().iloc[0, 1]
    correlation_values['ce_buy_corr'] = filtered_group[['ltp.1', 'tot_buy_qty.1']].corr().iloc[0, 1]  # ltp vs tot_buy_qty.1
    correlation_values['ce_sell_corr'] = filtered_group[['ltp.1', 'tot_sell_qty.1']].corr().iloc[0, 1]  # ltp vs tot_sell_qty.1
    correlation_values['ce_buy_sell_diff'] = filtered_group[['ltp.1', 'ce_buy_sell_diff']].corr().iloc[0, 1]
    correlation_values['pe_buy_corr'] = filtered_group[['ltp.2', 'tot_buy_qty.2']].corr().iloc[0, 1]  # ltp vs tot_buy_qty.2
    correlation_values['pe_sell_corr'] = filtered_group[['ltp.2', 'tot_sell_qty.2']].corr().iloc[0, 1]  # ltp vs tot_sell_qty.2
    correlation_values['pe_buy_sell_diff'] = filtered_group[['ltp.2', 'pe_buy_sell_diff']].corr().iloc[0, 1]
    correlation_values['n_ltp_diff'] = group.iloc[-1]['ltp'] - group.iloc[0]['ltp']
    correlation_values['n_buy_diff'] = group.iloc[-1]['tot_buy_qty'] - group.iloc[0]['tot_buy_qty']
    correlation_values['n_sell_diff'] = group.iloc[-1]['tot_sell_qty'] - group.iloc[0]['tot_sell_qty']
    correlation_values['ce_ltp_diff'] = group.iloc[-1]['ltp.1'] - group.iloc[0]['ltp.1']
    correlation_values['ce_buy_diff'] = group.iloc[-1]['tot_buy_qty.1'] - group.iloc[0]['tot_buy_qty.1']
    correlation_values['ce_sell_diff'] = group.iloc[-1]['tot_sell_qty.1'] - group.iloc[0]['tot_sell_qty.1']
    correlation_values['pe_ltp_diff'] = group.iloc[-1]['ltp.2'] - group.iloc[0]['ltp.2']
    correlation_values['pe_buy_diff'] = group.iloc[-1]['tot_buy_qty.2'] - group.iloc[0]['tot_buy_qty.2']
    correlation_values['pe_sell_diff'] = group.iloc[-1]['tot_sell_qty.2'] - group.iloc[0]['tot_sell_qty.2']
    
    
    '''correlation_values['Open_NSE:NIFTY50-INDEX'] = group['Open_NSE:NIFTY50-INDEX'].iloc[0]
    correlation_values['Close_9'] = group['Close_9'].iloc[-1]
    '''
    # Append the result to the correlation_data list
    correlation_data.append(correlation_values)

# Create a DataFrame from the correlation data
correlation_df = pd.DataFrame(correlation_data)
interval_str = f"{interval.components.minutes:02d}m"

# Save the correlation data to a new CSV file
correlation_df.to_csv(f'{date}_{interval_str}_correlation_results_2.csv', index=False)

print("Correlation results saved to 'correlation_results.csv'")

"""
import pandas as pd

# Load the CSV file
input_file = '07-02-2025_00m_NIFTY25FEBFUT.csv'
df = pd.read_csv(input_file)
date, file_name = input_file.split("_", 1)

# Convert the 'last_traded_time' column to datetime format
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'])

# Sort by time to ensure proper rolling
df.sort_values(by='last_traded_time', inplace=True)

# Set 'last_traded_time' as the index
df.set_index('last_traded_time', inplace=True)

# Define the rolling window size (1-minute overlapping 2-minute window)
####
window = '3min'

# Prepare an empty list to store the correlation data
correlation_data = []

# Iterate through the data using a rolling window with a 1-minute shift
for timestamp, group in df.resample('1min'):
    ####
    rolling_group = df.loc[timestamp - pd.Timedelta(minutes=2): timestamp]
    ####
    if len(rolling_group) < 3:
        continue  # Skip if there's not enough data in the window
    ####
    start_time = (timestamp - pd.Timedelta(minutes=2)).strftime('%d-%m-%Y %H:%M')
    correlation_values = {'last_traded_time': start_time}
    
    # Calculate the correlation for each column pair
    correlation_values['n_buy_corr'] = rolling_group[['ltp', 'tot_buy_qty']].corr().iloc[0, 1]
    correlation_values['n_sell_corr'] = rolling_group[['ltp', 'tot_sell_qty']].corr().iloc[0, 1]
    correlation_values['n_tb_ts'] = rolling_group[['tot_buy_qty', 'tot_sell_qty']].corr().iloc[0, 1]
    correlation_values['ce_buy_corr'] = rolling_group[['ltp.1', 'tot_buy_qty.1']].corr().iloc[0, 1]
    correlation_values['ce_sell_corr'] = rolling_group[['ltp.1', 'tot_sell_qty.1']].corr().iloc[0, 1]
    correlation_values['ce_tb_ts'] = rolling_group[['tot_buy_qty.1', 'tot_sell_qty.1']].corr().iloc[0, 1]
    correlation_values['pe_buy_corr'] = rolling_group[['ltp.2', 'tot_buy_qty.2']].corr().iloc[0, 1]
    correlation_values['pe_sell_corr'] = rolling_group[['ltp.2', 'tot_sell_qty.2']].corr().iloc[0, 1]
    correlation_values['pe_tb_ts'] = rolling_group[['tot_buy_qty.2', 'tot_sell_qty.2']].corr().iloc[0, 1]
    
    # Append the result to the correlation_data list
    correlation_data.append(correlation_values)

# Create a DataFrame from the correlation data
correlation_df = pd.DataFrame(correlation_data)

# Save the correlation data to a new CSV file
correlation_df.to_csv(f'{date}_rolling_3m_correlation_results.csv', index=False)

print("Rolling correlation results saved to 'rolling_2m_correlation_results.csv'")
"""