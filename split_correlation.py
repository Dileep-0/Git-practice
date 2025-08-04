import pandas as pd
import filenames

file_path = filenames.split_correlation
# Load the data
df = pd.read_csv(file_path)


# Convert time column to datetime format
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], format='%d-%m-%Y %H:%M')
df.set_index('last_traded_time', inplace=True)

# Resample data into 5-minute intervals
groups = df.resample('5min')

correlation_results = []
filtered_timestamps = []

for time, group in groups:
    
    if group.empty:
        continue  # Skip empty groups
    
    group = group.loc[(group != 0).all(axis=1)]

    # Get the first and last timestamps in the 5-minute window
    start_time = group.index.min()
    end_time = group.index.max()

    # Filter the first 3 minutes and last 3 minutes
    first_half = group[group.index < (start_time + pd.Timedelta(minutes=3))]
    last_half = group[group.index >= (end_time - pd.Timedelta(minutes=2))]

    if first_half.empty or last_half.empty:
        continue 
    
    correlations_first = {
        'timestamp': time,
        'half': 'first',
        'ltp_buy': first_half[['ltp', 'tot_buy_qty']].corr().iloc[0, 1],
        'ltp_sell': first_half[['ltp', 'tot_sell_qty']].corr().iloc[0, 1],
        'ltp1_buy': first_half[['ltp.1', 'tot_buy_qty.1']].corr().iloc[0, 1],
        'ltp1_sell': first_half[['ltp.1', 'tot_sell_qty.1']].corr().iloc[0, 1],
        'ltp2_buy': first_half[['ltp.2', 'tot_buy_qty.2']].corr().iloc[0, 1],
        'ltp2_sell': first_half[['ltp.2', 'tot_sell_qty.2']].corr().iloc[0, 1],
    }
    correlation_results.append(correlations_first)

    # Second Half Correlation (Separate Line)
    correlations_second = {
        'timestamp': time,
        'half': 'second',
        'ltp_buy': last_half[['ltp', 'tot_buy_qty']].corr().iloc[0, 1],
        'ltp_sell': last_half[['ltp', 'tot_sell_qty']].corr().iloc[0, 1],
        'ltp1_buy': last_half[['ltp.1', 'tot_buy_qty.1']].corr().iloc[0, 1],
        'ltp1_sell': last_half[['ltp.1', 'tot_sell_qty.1']].corr().iloc[0, 1],
        'ltp2_buy': last_half[['ltp.2', 'tot_buy_qty.2']].corr().iloc[0, 1],
        'ltp2_sell': last_half[['ltp.2', 'tot_sell_qty.2']].corr().iloc[0, 1],
    }
    correlation_results.append(correlations_second)

    '''f_half = (
        correlations_first['ltp_buy'] > 0 and correlations_first['ltp_sell'] < 0 and \
        correlations_first['ltp1_buy'] > 0 and correlations_first['ltp1_sell'] < 0 and \
        correlations_first['ltp2_buy'] > 0 and correlations_first['ltp2_sell'] < 0 
    )

    s_half = (
        correlations_second['ltp_buy'] > 0 and correlations_second['ltp_sell'] < 0 and \
        correlations_second['ltp1_buy'] > 0 and correlations_second['ltp1_sell'] < 0 and \
        correlations_second['ltp2_buy'] > 0 and correlations_second['ltp2_sell'] < 0 
    )'''

    '''pair1_match = (
        correlations_first['ltp_buy'] < correlations_second['ltp_buy'] or
        correlations_first['ltp_sell'] > correlations_second['ltp_sell']
    )

    pair2_match = (
        correlations_first['ltp1_buy'] < correlations_second['ltp1_buy'] or
        correlations_first['ltp1_sell'] > correlations_second['ltp1_sell']
    )

    pair3_match = (
        correlations_first['ltp2_buy'] < correlations_second['ltp2_buy'] or
        correlations_first['ltp2_sell'] > correlations_second['ltp2_sell']
    )'''

    # Store timestamps where all three pairs meet the condition
    conditions = [
        correlations_first['ltp_buy'] > 0, correlations_first['ltp_sell'] < 0,
        correlations_first['ltp1_buy'] > 0, correlations_first['ltp1_sell'] < 0,
        correlations_first['ltp2_buy'] > 0, correlations_first['ltp2_sell'] < 0,
        correlations_second['ltp_buy'] > 0, correlations_second['ltp_sell'] < 0,
        correlations_second['ltp1_buy'] > 0, correlations_second['ltp1_sell'] < 0,
        correlations_second['ltp2_buy'] > 0, correlations_second['ltp2_sell'] < 0
]

    abs_conditions = [
        abs(correlations_first['ltp_buy']) > 0.2, abs(correlations_first['ltp_sell']) > 0.2,
        abs(correlations_first['ltp1_buy']) > 0.2, abs(correlations_first['ltp1_sell']) > 0.2,
        abs(correlations_first['ltp2_buy']) > 0.2, abs(correlations_first['ltp2_sell']) > 0.2,
        abs(correlations_second['ltp_buy']) > 0.2, abs(correlations_second['ltp_sell']) > 0.2,
        abs(correlations_second['ltp1_buy']) > 0.2, abs(correlations_second['ltp1_sell']) > 0.2,
        abs(correlations_second['ltp2_buy']) > 0.2, abs(correlations_second['ltp2_sell']) > 0.2
    ]
    if (sum(conditions) >= 10 and sum(abs_conditions) >= 9):
        filtered_timestamps.append(time)

# Convert results to DataFrame
correlation_df = pd.DataFrame(correlation_results)

# Save to file
output_file = "split_correlation_results.csv"
correlation_df.to_csv(output_file, index=False)
print(f"Correlation results saved to {output_file}")

"""filtered_df = pd.DataFrame({'timestamp': filtered_timestamps})
filtered_output_file = "filtered_timestamps_pairs.csv"
filtered_df.to_csv(filtered_output_file, index=False)
print(f"Filtered timestamps saved to {filtered_output_file}")"""
print("Matching timestamps:")
for ts in filtered_timestamps:
    print(ts)
