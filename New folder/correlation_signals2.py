import pandas as pd
import filenames

file_path = filenames.correlation_signals

df = pd.read_csv(file_path, dtype={
    'n_buy_diff': 'float64',
    'n_sell_diff': 'float64',
    'ce_buy_diff': 'float64',
    'ce_sell_diff': 'float64',
    'pe_buy_diff': 'float64',
    'pe_sell_diff': 'float64'
})


date, file_name = file_path.split("_", 1)

# Convert 'last_traded_time' to datetime if needed
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], dayfirst=True, errors='coerce')


flow_sets = (
    (df['n_buy_corr'] > 0.2).astype(int) +
    (df['n_sell_corr'] < -0.2).astype(int) +
    (df['ce_buy_corr'] > 0.2).astype(int) +
    (df['ce_sell_corr'] < -0.2).astype(int) +
    (df['pe_buy_corr'] > 0.2).astype(int) +
    (df['pe_sell_corr'] < -0.2).astype(int)
) >= 5

flow_sets_b_s = (
    (abs(df['n_tb_ts']) > 0.2).astype(int) +
    (abs(df['ce_tb_ts']) > 0.2).astype(int) +
    (abs(df['pe_tb_ts']) > 0.2).astype(int)
) >= 2

flow_sets_b_s_2 = (
    (df['n_tb_ts'] < -0.45).astype(int) +
    (df['ce_tb_ts'] < -0.45).astype(int) +
    (df['pe_tb_ts'] < -0.45).astype(int)
) >= 1


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


def check_opposite(prev, curr, should_increase):
    if should_increase:
        cond1 = (prev < 0) & (curr > 0)
        cond2 = (prev > 0) & (curr > 0) & (prev < curr) & (prev.astype(str).str.len() < curr.astype(str).str.len())
        cond3 = (prev < 0) & (curr < 0) & (prev < curr) & (prev.astype(str).str.len() > curr.astype(str).str.len())

        return cond1 | cond2 | cond3

    else:
        cond1 = (prev > 0) & (curr < 0)
        cond2 = (prev > 0) & (curr > 0) & (prev > curr) & (prev.astype(str).str.len() > curr.astype(str).str.len())
        cond3 = (prev < 0) & (curr < 0) & (prev > curr) & (prev.astype(str).str.len() < curr.astype(str).str.len())

        return cond1 | cond2 | cond3


prev_opposite_buy = (
    (
        (check_opposite(df['n_buy_diff'].shift(1), df['n_buy_diff'], should_increase=True)).astype(int) +
        (check_opposite(df['n_sell_diff'].shift(1), df['n_sell_diff'], should_increase=False)).astype(int) +
        (check_opposite(df['ce_buy_diff'].shift(1), df['ce_buy_diff'], should_increase=True)).astype(int) +
        (check_opposite(df['ce_sell_diff'].shift(1), df['ce_sell_diff'], should_increase=False)).astype(int) +
        (check_opposite(df['pe_buy_diff'].shift(1), df['pe_buy_diff'], should_increase=False)).astype(int) +
        (check_opposite(df['pe_sell_diff'].shift(1), df['pe_sell_diff'], should_increase=True)).astype(int)
    ) >= 3
)

prev_opposite_sell = (
    (
        (check_opposite(df['n_buy_diff'].shift(1), df['n_buy_diff'], should_increase=False)).astype(int) +
        (check_opposite(df['n_sell_diff'].shift(1), df['n_sell_diff'], should_increase=True)).astype(int) +
        (check_opposite(df['ce_buy_diff'].shift(1), df['ce_buy_diff'], should_increase=False)).astype(int) +
        (check_opposite(df['ce_sell_diff'].shift(1), df['ce_sell_diff'], should_increase=True)).astype(int) +
        (check_opposite(df['pe_buy_diff'].shift(1), df['pe_buy_diff'], should_increase=True)).astype(int) +
        (check_opposite(df['pe_sell_diff'].shift(1), df['pe_sell_diff'], should_increase=False)).astype(int)
    ) >= 3
)
valid_buy = satisfied_buy & prev_opposite_buy
valid_sell = satisfied_sell & prev_opposite_sell


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


def check_ratio(df, ratio1=2.5):
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
    # Ensure at least 1 pair satisfies 3x and a DIFFERENT pair satisfies 5x
    return pairs_3x > 0


three_x_series = check_ratio(df)
# Check for rows that satisfy all criteria

first_condition = (
    flow_sets & flow_sets_b_s & flow_sets_b_s_2 & 
     (valid_buy | valid_sell)
)

matching_rows = df[
    first_condition & three_x_series
]

if not matching_rows.empty:
    for index, row in matching_rows.iterrows():
        if satisfied_buy.iloc[index]:
            print(f"{row['last_traded_time']} - Buy")
        elif satisfied_sell.iloc[index]:
            print(f"{row['last_traded_time']} - Sell")
else:
    print("No timestamps matched the criteria.\n")
