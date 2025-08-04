import pandas as pd

def check_step_1(row):
    """Step 1: Check if the absolute greater or lesser value pattern repeats in other pairs."""
    n_buy_corr, n_sell_corr = abs(row['n_buy_corr']), abs(row['n_sell_corr'])
    ce_buy_corr, ce_sell_corr = abs(row['ce_buy_corr']), abs(row['ce_sell_corr'])
    pe_buy_corr, pe_sell_corr = abs(row['pe_buy_corr']), abs(row['pe_sell_corr'])
    
    n_condition = n_buy_corr > n_sell_corr if ce_buy_corr > ce_sell_corr or pe_buy_corr > pe_sell_corr else n_buy_corr < n_sell_corr
    return n_condition

def check_step_2(row):
    """Step 2: Check if the values follow the positive-negative pattern."""
    try:
        values = [
            float(row.get('n_buy_corr', 0)), float(row.get('n_sell_corr', 0)), 
            float(row.get('ce_buy_corr', 0)), float(row.get('ce_sell_corr', 0)), 
            float(row.get('pe_buy_corr', 0)), float(row.get('pe_sell_corr', 0))
        ]
    except ValueError:
        return False  # Return False if conversion fails
    
    pattern = [1, -1, 1, -1, 1, -1]
    
    match_count = sum(1 for i in range(6) if (values[i] > 0 and pattern[i] == 1) or (values[i] < 0 and pattern[i] == -1))
    
    return match_count >= 5


def check_step_3(row):
    """Step 3: Check conditions on n_tb_ts, ce_tb_ts, pe_tb_ts."""
    tb_ts_values = [row['n_tb_ts'], row['ce_tb_ts'], row['pe_tb_ts']]
    below_threshold = sum(1 for val in tb_ts_values if val < -0.45)
    above_threshold = sum(1 for val in tb_ts_values if val > -0.2)
    return below_threshold >= 1 and above_threshold <= 1

def check_step_4(row, df):
    """Step 4: Check for extreme differences or historical highest values."""
    pairs = [('n_buy_diff', 'n_sell_diff'), ('ce_buy_diff', 'ce_sell_diff'), ('pe_buy_diff', 'pe_sell_diff')]
    for col1, col2 in pairs:
        if abs(row[col1]) > 5 * abs(row[col2]) or abs(row[col2]) > 5 * abs(row[col1]):
            return True
    
    # Check historical values
    past_rows = df.loc[:row.name][-5:]
    print(past_rows)
    match_count = sum(1 for col in ['n_buy_diff', 'n_sell_diff', 'ce_buy_diff', 'ce_sell_diff', 'pe_buy_diff', 'pe_sell_diff'] if abs(row[col]) > past_rows[col].abs().max())
    return match_count >= 2

def check_step_5(row):
    """Step 5: Identify whether the flow follows a BUY or SELL pattern."""
    values = [row['n_buy_diff'], row['n_sell_diff'], row['ce_buy_diff'], row['ce_sell_diff'], row['pe_buy_diff'], row['pe_sell_diff']]
    buy_pattern = [1, -1, 1, -1, -1, 1]
    sell_pattern = [-1, 1, -1, 1, 1, -1]
    buy_match = sum(1 for i in range(6) if (values[i] > 0 and buy_pattern[i] == 1) or (values[i] < 0 and buy_pattern[i] == -1))
    sell_match = sum(1 for i in range(6) if (values[i] > 0 and sell_pattern[i] == 1) or (values[i] < 0 and sell_pattern[i] == -1))
    if buy_match >= 5:
        return "BUY"
    elif sell_match >= 5:
        return "SELL"
    return None

def check_step_6(previous_row, current_row, trade_type):
    """Step 6: Verify sign change or digit change based on Step 5 trade type (BUY/SELL)."""
    expected_sign_patterns = {
        "BUY": [-1, 1, -1, 1, 1, -1],
        "SELL": [1, -1, 1, -1, -1, 1]
    }
    
    expected_signs = expected_sign_patterns[trade_type]
    prev_values = previous_row.iloc[[11, 12, 14, 15, 17, 18]].tolist()
    curr_values = current_row.iloc[[11, 12, 14, 15, 17, 18]].tolist()
    
    sign_change_count = sum(1 for i in range(6) if (-1 if prev_values[i] < 0 else 1) == expected_signs[i])
    if sign_change_count >= 4:
        return True
    
    digit_change_count = sum(1 for i in range(6) if (curr_values[i] > prev_values[i] and len(str(abs(curr_values[i]))) > len(str(abs(prev_values[i])))) or (curr_values[i] < prev_values[i] and len(str(abs(curr_values[i]))) < len(str(abs(prev_values[i])))))
    return digit_change_count >= 4

def process_csv(file_path):
    df = pd.read_csv(file_path, sep=",", engine="python")
    df.columns = df.columns.str.strip()  # Removes leading/trailing spaces

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i - 1]
        
        if (check_step_1(row) and check_step_2(row) and check_step_3(row) and check_step_4(row, df)):
            trade_type = check_step_5(row)
            if trade_type and check_step_6(prev_row, row, trade_type):
                print(f"{row['last_traded_time']} meets all criteria")

# Example usage
process_csv("06-01-2025_05m_correlation_results.csv")
import pandas as pd

# Load the CSV file
file_path = '04-02-2025_05m_correlation_results.csv'
df = pd.read_csv(file_path)
date, file_name = file_path.split("_", 1)

# Convert 'last_traded_time' to datetime if needed
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'])

# Define the mandatory sets
first_set = (df['n_buy_corr'] > 0) & (df['n_sell_corr'] < 0) & (df['n_tb_ts'] < 0)
second_set = (df['ce_buy_corr'] > 0) & (df['ce_sell_corr'] < 0) & (df['ce_tb_ts'] < 0)
third_set = (df['pe_buy_corr'] > 0) & (df['pe_sell_corr'] < 0) & (df['pe_tb_ts'] < 0)


first_set_with_val = (df['n_buy_corr'] > 0.35) & (df['n_sell_corr'] < -0.35)
second_set_with_val = (df['ce_buy_corr'] > 0.35) & (df['ce_sell_corr'] < -0.35)
third_set_with_val = (df['pe_buy_corr'] > 0.35) & (df['pe_sell_corr'] < -0.35)

above_point_2 = abs(df['n_buy_corr'] > 0.2) & abs(df['n_sell_corr'] > 0.2) & abs(df['n_tb_ts'] > 0.2) & \
                abs(df['ce_buy_corr'] > 0.2) & abs(df['ce_sell_corr'] > 0.2) & abs(df['ce_tb_ts'] > 0.2) & \
                abs(df['pe_buy_corr'] > 0.2) & abs(df['pe_sell_corr'] > 0.2) & abs(df['pe_tb_ts'] > 0.2)

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

first_pair_greater = abs(df['n_buy_corr']) > abs(df['n_sell_corr'])
first_pair_lesser = abs(df['n_buy_corr']) < abs(df['n_sell_corr'])

repeat_greater = (
    ((abs(df['ce_buy_corr']) > abs(df['ce_sell_corr'])).astype(int)) +
    ((abs(df['pe_buy_corr']) > abs(df['pe_sell_corr'])).astype(int))
) >= 1

repeat_lesser = (
    ((abs(df['ce_buy_corr']) < abs(df['ce_sell_corr'])).astype(int)) +
    ((abs(df['pe_buy_corr']) < abs(df['pe_sell_corr'])).astype(int))
) >= 1

dominating_flow = (first_pair_greater & repeat_greater) | (first_pair_lesser & repeat_lesser)

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
     (satisfied_buy | satisfied_sell) & dominating_flow
)
second_condition = (first_set & 
                    (second_set| third_set ) & 
                    additional_condition2 & (satisfied_buy | satisfied_sell) & dominating_flow
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
    five_x = pairs_5x > 0
    three_x = pairs_3x > 1
    return five_x, three_x

five_x, three_x = check_ratio(df)
# Check for rows that satisfy all criteria
'''matching_rows = df[
    ((first_condition & five_x) | (second_condition & five_x & three_x))
]'''
matching_rows = df[
    (first_condition | second_condition)
]

# Print the timestamps where the criteria are satisfied & specify if it's Buy or Sell
output_file = f"{date}_correlation_timestamps.txt"
with open(output_file, "w") as file:
    if not matching_rows.empty:
        for index, row in matching_rows.iterrows():
            if satisfied_buy.iloc[index]:
                file.write(f"{row['last_traded_time']} - Buy\n")
            elif satisfied_sell.iloc[index]:
                file.write(f"{row['last_traded_time']} - Sell\n")
    else:
        file.write("No timestamps matched the criteria.\n")
print(f"Results saved to {output_file}")
