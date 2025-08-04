import pandas as pd

# Load the CSV file
file_path = '21-03-2025_05m_correlation_results.csv'
df = pd.read_csv(file_path)

# Convert 'last_traded_time' to datetime if needed
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'])

# Define the mandatory sets
first_set = (df['n_buy_corr'] > 0) & (df['n_sell_corr'] < 0) & (df['n_tb_ts'] < 0)
second_set = (df['ce_buy_corr'] > 0) & (df['ce_sell_corr'] < 0) & (df['ce_tb_ts'] < 0)
third_set = (df['pe_buy_corr'] > 0) & (df['pe_sell_corr'] < 0) & (df['pe_tb_ts'] < 0)


first_set_with_val = (df['n_buy_corr'] > 0.35) & (df['n_sell_corr'] < -0.35)
second_set_with_val = (df['ce_buy_corr'] > 0.35) & (df['ce_sell_corr'] < -0.35)
third_set_with_val = (df['pe_buy_corr'] > 0.35) & (df['pe_sell_corr'] < -0.35)

satisfied_conditions = (
    (df['n_buy_corr'] > 0.35).astype(int) +
    (df['n_sell_corr'] < -0.35).astype(int) +
    (df['ce_buy_corr'] > 0.35).astype(int) +
    (df['ce_sell_corr'] < -0.35).astype(int) +
    (df['pe_buy_corr'] > 0.35).astype(int) +
    (df['pe_sell_corr'] < -0.35).astype(int)
) >= 5

satisfied_buy = (
    (df['n_buy_diff'] > 0).astype(int) +
    (df['n_sell_diff'] < 0).astype(int) +
    (df['ce_buy_diff'] > 0).astype(int) +
    (df['ce_sell_diff'] < 0).astype(int) +
    (df['pe_buy_diff'] < 0).astype(int) +
    (df['pe_sell_diff'] > 0).astype(int)
) >= 5

satisfied_sell = (
    (df['n_buy_diff'] < 0).astype(int) +
    (df['n_sell_diff'] > 0).astype(int) +
    (df['ce_buy_diff'] < 0).astype(int) +
    (df['ce_sell_diff'] > 0).astype(int) +
    (df['pe_buy_diff'] > 0).astype(int) +
    (df['pe_sell_diff'] < 0).astype(int)
) >= 5

if satisfied_buy.sum() >= 5:
    ltp_diff = (abs(df['ce_ltp_diff'] / df['n_ltp_diff']) > 0.5) & (abs(df['ce_ltp_diff'] / df['n_ltp_diff']) < 1.5)
else:
    ltp_diff = None

if satisfied_sell.sum() >= 5:
    ltp_diff = (abs(df['pe_ltp_diff'] / df['n_ltp_diff']) > 0.5) & (abs(df['pe_ltp_diff'] / df['n_ltp_diff']) < 1.5)
else:
    ltp_diff = None

# Additional condition: One of these should be below -0.7
additional_condition = (df['n_tb_ts'] < -0.6) | (df['ce_tb_ts'] < -0.6) | (df['pe_tb_ts'] < -0.6)
additional_condition2 = (df['n_tb_ts'] < -0.65) | (df['ce_tb_ts'] < -0.65) | (df['pe_tb_ts'] < -0.65)

# Buy Criteria
buy_criteria = (
    (df['n_buy_diff'] > 0).astype(int) +
    (df['n_sell_diff'] < 0).astype(int) +
    (df['ce_buy_diff'] > 0).astype(int) +
    (df['ce_sell_diff'] < 0).astype(int) +
    (df['pe_buy_diff'] < 0).astype(int) +
    (df['pe_sell_diff'] > 0).astype(int)
) == 6

# Sell Criteria
sell_criteria = (
    (df['n_buy_diff'] < 0).astype(int) +
    (df['n_sell_diff'] > 0).astype(int) +
    (df['ce_buy_diff'] < 0).astype(int) +
    (df['ce_sell_diff'] > 0).astype(int) +
    (df['pe_buy_diff'] > 0).astype(int) +
    (df['pe_sell_diff'] < 0).astype(int)
) == 6

first_condition = (
    first_set & second_set & third_set & additional_condition &
    satisfied_conditions & (satisfied_buy | satisfied_sell) & ltp_diff
)
second_condition = ((first_set & first_set_with_val) & 
                    ((second_set & second_set_with_val) | (third_set & third_set_with_val)) & 
                    additional_condition2 & (satisfied_buy | satisfied_sell) & ltp_diff
                     )
def check_ratio(df, ratio1=3, ratio2=5):
    # Convert values to absolute for correct ratio checks
    abs_n_buy_diff = df['n_buy_diff'].abs()
    abs_n_sell_diff = df['n_sell_diff'].abs()
    abs_ce_buy_diff = df['ce_buy_diff'].abs()
    abs_ce_sell_diff = df['ce_sell_diff'].abs()
    abs_pe_buy_diff = df['pe_buy_diff'].abs()
    abs_pe_sell_diff = df['pe_sell_diff'].abs()
    
    # Check which pairs satisfy 3x condition
    pairs_3x = (
        ((abs_n_buy_diff >= ratio1 * abs_n_sell_diff) | (abs_n_sell_diff >= ratio1 * abs_n_buy_diff)).astype(int) +
        ((abs_ce_buy_diff >= ratio1 * abs_ce_sell_diff) | (abs_ce_sell_diff >= ratio1 * abs_ce_buy_diff)).astype(int) +
        ((abs_pe_buy_diff >= ratio1 * abs_pe_sell_diff) | (abs_pe_sell_diff >= ratio1 * abs_pe_buy_diff)).astype(int)
    )
    
    # Check which pairs satisfy 5x condition
    pairs_5x = (
        ((abs_n_buy_diff >= ratio2 * abs_n_sell_diff) | (abs_n_sell_diff >= ratio2 * abs_n_buy_diff)).astype(int) +
        ((abs_ce_buy_diff >= ratio2 * abs_ce_sell_diff) | (abs_ce_sell_diff >= ratio2 * abs_ce_buy_diff)).astype(int) +
        ((abs_pe_buy_diff >= ratio2 * abs_pe_sell_diff) | (abs_pe_sell_diff >= ratio2 * abs_pe_buy_diff)).astype(int)
    )

    # Ensure at least 1 pair satisfies 3x and a DIFFERENT pair satisfies 5x
    return (pairs_3x > 1) & (pairs_5x > 0)

imbalance = check_ratio(df)
# Check for rows that satisfy all criteria
matching_rows = df[
    (first_condition | second_condition) & imbalance
]

# Print the timestamps where the criteria are satisfied & specify if it's Buy or Sell
if not matching_rows.empty:
    for index, row in matching_rows.iterrows():
        #print(f"{row['last_traded_time']} - Matching Criteria")
        if satisfied_buy.iloc[index]:
            print(f"{row['last_traded_time']} - Buy")
        elif satisfied_sell.iloc[index]:
            print(f"{row['last_traded_time']} - Sell")
else:
    print("No timestamps matched the criteria.")
