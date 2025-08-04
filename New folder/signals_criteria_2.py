import pandas as pd
import filenames
import numpy as np

file_path = filenames.signals
df = pd.read_csv(file_path)
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], dayfirst=True, errors='coerce')
# Convert columns to numeric
cols = ['tot_buy_qty_1', 'tot_sell_qty_1', 'tot_buy_qty_2', 'tot_sell_qty_2', 'tot_buy_qty_3', 'tot_sell_qty_3']
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')



# First pattern: ++ -+
condition1 = (
    (df['tot_buy_qty_1'] > 0).astype(int) +
    (df['tot_sell_qty_1'] < 0).astype(int) +
    (df['tot_buy_qty_2'] > 0).astype(int) +
    (df['tot_sell_qty_2'] < 0).astype(int) +
    (df['tot_buy_qty_3'] < 0).astype(int) +
    (df['tot_sell_qty_3'] > 0).astype(int)
) >= 5

b_pair1 = ((df['tot_buy_qty_1'] > 0) & (df['tot_sell_qty_1'] < 0)).astype(int)
b_pair2 = ((df['tot_buy_qty_2'] > 0) & (df['tot_sell_qty_2'] < 0)).astype(int)
b_pair3 = ((df['tot_buy_qty_3'] < 0) & (df['tot_sell_qty_3'] > 0)).astype(int)
b_matched_pairs = b_pair1 + b_pair2 + b_pair3
b_condition = b_matched_pairs >= 2

# Second pattern: -- +-
condition2 = (
    (df['tot_buy_qty_1'] < 0).astype(int) +
    (df['tot_sell_qty_1'] > 0).astype(int) +
    (df['tot_buy_qty_2'] < 0).astype(int) +
    (df['tot_sell_qty_2'] > 0).astype(int) +
    (df['tot_buy_qty_3'] > 0).astype(int) +
    (df['tot_sell_qty_3'] < 0).astype(int)
) >= 5

s_pair1 = ((df['tot_buy_qty_1'] < 0) & (df['tot_sell_qty_1'] > 0)).astype(int)
s_pair2 = ((df['tot_buy_qty_2'] < 0) & (df['tot_sell_qty_2'] > 0)).astype(int)
s_pair3 = ((df['tot_buy_qty_3'] > 0) & (df['tot_sell_qty_3'] < 0)).astype(int)
s_matched_pairs = s_pair1 + s_pair2 + s_pair3
s_condition = s_matched_pairs >= 2

prev = df[cols].shift(1)

def num_digits(df):
    return df.abs().fillna(0).astype(int).astype(str).map(len)

curr_digits = num_digits(df[cols])
prev_digits = num_digits(prev)

def digit_comparing(len_a, len_b):
  min_len = np.minimum(len_a, len_b)
  max_len = np.maximum(len_a, len_b)
  return np.where(
      min_len < 5, max_len >= min_len + 2,
      np.where(min_len == 5, max_len > min_len,
      np.where(min_len >= 6, max_len >= 6, False))
  )

def for_6_digits(len_a, len_b):
  min_len = np.minimum(len_a, len_b)
  max_len = np.maximum(len_a, len_b)
  return np.where(
      min_len > 5, max_len > 5,
      np.where(min_len == 5, max_len > min_len, False)
  )

# ---- Direction-based checks for pattern 1: ↑ ↓ ↑ ↓ ↓ ↑ ----
dir1_checks = [
    ((df['tot_buy_qty_1'] > prev['tot_buy_qty_1']) &
     (((df['tot_buy_qty_1'] > 0) & (prev['tot_buy_qty_1'] < 0)) |
      (curr_digits['tot_buy_qty_1'] != prev_digits['tot_buy_qty_1']))),

    ((df['tot_sell_qty_1'] < prev['tot_sell_qty_1']) &
     (((df['tot_sell_qty_1'] < 0) & (prev['tot_sell_qty_1'] > 0)) |
      (curr_digits['tot_sell_qty_1'] != prev_digits['tot_sell_qty_1']))),

    ((df['tot_buy_qty_2'] > prev['tot_buy_qty_2']) &
     (((df['tot_buy_qty_2'] > 0) & (prev['tot_buy_qty_2'] < 0)) |
      (curr_digits['tot_buy_qty_2'] != prev_digits['tot_buy_qty_2']))),

    ((df['tot_sell_qty_2'] < prev['tot_sell_qty_2']) &
     (((df['tot_sell_qty_2'] < 0) & (prev['tot_sell_qty_2'] > 0)) |
      (curr_digits['tot_sell_qty_2'] != prev_digits['tot_sell_qty_2']))),

    ((df['tot_buy_qty_3'] < prev['tot_buy_qty_3']) &
     (((df['tot_buy_qty_3'] < 0) & (prev['tot_buy_qty_3'] > 0)) |
      (curr_digits['tot_buy_qty_3'] != prev_digits['tot_buy_qty_3']))),

    ((df['tot_sell_qty_3'] > prev['tot_sell_qty_3']) &
     (((df['tot_sell_qty_3'] > 0) & (prev['tot_sell_qty_3'] < 0)) |
      (curr_digits['tot_sell_qty_3'] != prev_digits['tot_sell_qty_3'])))
]
dir_mask1 = sum(check.fillna(False).astype(int) for check in dir1_checks) >= 3

# ---- Direction-based checks for pattern 2: ↓ ↑ ↓ ↑ ↑ ↓ ----
dir2_checks = [
    ((df['tot_buy_qty_1'] < prev['tot_buy_qty_1']) &
     (((df['tot_buy_qty_1'] < 0) & (prev['tot_buy_qty_1'] > 0)) |
      (curr_digits['tot_buy_qty_1'] != prev_digits['tot_buy_qty_1']))),

    ((df['tot_sell_qty_1'] > prev['tot_sell_qty_1']) &
     (((df['tot_sell_qty_1'] > 0) & (prev['tot_sell_qty_1'] < 0)) |
      (curr_digits['tot_sell_qty_1'] != prev_digits['tot_sell_qty_1']))),

    ((df['tot_buy_qty_2'] < prev['tot_buy_qty_2']) &
     (((df['tot_buy_qty_2'] < 0) & (prev['tot_buy_qty_2'] > 0)) |
      (curr_digits['tot_buy_qty_2'] != prev_digits['tot_buy_qty_2']))),

    ((df['tot_sell_qty_2'] > prev['tot_sell_qty_2']) &
     (((df['tot_sell_qty_2'] > 0) & (prev['tot_sell_qty_2'] < 0)) |
      (curr_digits['tot_sell_qty_2'] != prev_digits['tot_sell_qty_2']))),

    ((df['tot_buy_qty_3'] > prev['tot_buy_qty_3']) &
     (((df['tot_buy_qty_3'] > 0) & (prev['tot_buy_qty_3'] < 0)) |
      (curr_digits['tot_buy_qty_3'] != prev_digits['tot_buy_qty_3']))),

    ((df['tot_sell_qty_3'] < prev['tot_sell_qty_3']) &
     (((df['tot_sell_qty_3'] < 0) & (prev['tot_sell_qty_3'] > 0)) |
      (curr_digits['tot_sell_qty_3'] != prev_digits['tot_sell_qty_3'])))
]
dir_mask2 = sum(check.fillna(False).astype(int) for check in dir2_checks) >= 3

dir1_checks_vert = [
    ((df['tot_buy_qty_1'] > prev['tot_buy_qty_1']) &
     ((df['tot_buy_qty_1'] > 0) & (prev['tot_buy_qty_1'] < 0)) &
      (curr_digits['tot_buy_qty_1'] != prev_digits['tot_buy_qty_1'])),

    ((df['tot_sell_qty_1'] < prev['tot_sell_qty_1']) &
     ((df['tot_sell_qty_1'] < 0) & (prev['tot_sell_qty_1'] > 0)) &
      (curr_digits['tot_sell_qty_1'] != prev_digits['tot_sell_qty_1'])),

    ((df['tot_buy_qty_2'] > prev['tot_buy_qty_2']) &
     ((df['tot_buy_qty_2'] > 0) & (prev['tot_buy_qty_2'] < 0)) &
      (curr_digits['tot_buy_qty_2'] != prev_digits['tot_buy_qty_2'])),

    ((df['tot_sell_qty_2'] < prev['tot_sell_qty_2']) &
     ((df['tot_sell_qty_2'] < 0) & (prev['tot_sell_qty_2'] > 0)) &
      (curr_digits['tot_sell_qty_2'] != prev_digits['tot_sell_qty_2'])),

    ((df['tot_buy_qty_3'] < prev['tot_buy_qty_3']) &
     ((df['tot_buy_qty_3'] < 0) & (prev['tot_buy_qty_3'] > 0)) &
      (curr_digits['tot_buy_qty_3'] != prev_digits['tot_buy_qty_3'])),

    ((df['tot_sell_qty_3'] > prev['tot_sell_qty_3']) &
     ((df['tot_sell_qty_3'] > 0) & (prev['tot_sell_qty_3'] < 0)) &
      (curr_digits['tot_sell_qty_3'] != prev_digits['tot_sell_qty_3']))
]
dir_mask1_vert = sum(check.fillna(False).astype(int) for check in dir1_checks_vert) >= 2

# ---- Direction-based checks for pattern 2: ↓ ↑ ↓ ↑ ↑ ↓ ----
dir2_checks_vert = [
    ((df['tot_buy_qty_1'] < prev['tot_buy_qty_1']) &
     ((df['tot_buy_qty_1'] < 0) & (prev['tot_buy_qty_1'] > 0)) &
      (curr_digits['tot_buy_qty_1'] != prev_digits['tot_buy_qty_1'])),

    ((df['tot_sell_qty_1'] > prev['tot_sell_qty_1']) &
     ((df['tot_sell_qty_1'] > 0) & (prev['tot_sell_qty_1'] < 0)) &
      (curr_digits['tot_sell_qty_1'] != prev_digits['tot_sell_qty_1'])),

    ((df['tot_buy_qty_2'] < prev['tot_buy_qty_2']) &
     ((df['tot_buy_qty_2'] < 0) & (prev['tot_buy_qty_2'] > 0)) &
      (curr_digits['tot_buy_qty_2'] != prev_digits['tot_buy_qty_2'])),

    ((df['tot_sell_qty_2'] > prev['tot_sell_qty_2']) &
     ((df['tot_sell_qty_2'] > 0) & (prev['tot_sell_qty_2'] < 0)) &
      (curr_digits['tot_sell_qty_2'] != prev_digits['tot_sell_qty_2'])),

    ((df['tot_buy_qty_3'] > prev['tot_buy_qty_3']) &
     ((df['tot_buy_qty_3'] > 0) & (prev['tot_buy_qty_3'] < 0)) &
      (curr_digits['tot_buy_qty_3'] != prev_digits['tot_buy_qty_3'])),

    ((df['tot_sell_qty_3'] < prev['tot_sell_qty_3']) &
     ((df['tot_sell_qty_3'] < 0) & (prev['tot_sell_qty_3'] > 0)) &
      (curr_digits['tot_sell_qty_3'] != prev_digits['tot_sell_qty_3']))
]
dir_mask2_vert = sum(check.fillna(False).astype(int) for check in dir2_checks_vert) >= 2


dir1_checks_vert_with_digits = [
    ((df['tot_buy_qty_1'] > prev['tot_buy_qty_1']) &
     ((df['tot_buy_qty_1'] > 0) & (prev['tot_buy_qty_1'] < 0)) &
      (digit_comparing(curr_digits['tot_buy_qty_1'], prev_digits['tot_buy_qty_1']))),

    ((df['tot_sell_qty_1'] < prev['tot_sell_qty_1']) &
     ((df['tot_sell_qty_1'] < 0) & (prev['tot_sell_qty_1'] > 0)) &
      (digit_comparing(curr_digits['tot_sell_qty_1'], prev_digits['tot_sell_qty_1']))),

    ((df['tot_buy_qty_2'] > prev['tot_buy_qty_2']) &
     ((df['tot_buy_qty_2'] > 0) & (prev['tot_buy_qty_2'] < 0)) &
      (digit_comparing(curr_digits['tot_buy_qty_2'], prev_digits['tot_buy_qty_2']))),

    ((df['tot_sell_qty_2'] < prev['tot_sell_qty_2']) &
     ((df['tot_sell_qty_2'] < 0) & (prev['tot_sell_qty_2'] > 0)) &
      (digit_comparing(curr_digits['tot_sell_qty_2'], prev_digits['tot_sell_qty_2']))),

    ((df['tot_buy_qty_3'] < prev['tot_buy_qty_3']) &
     ((df['tot_buy_qty_3'] < 0) & (prev['tot_buy_qty_3'] > 0)) &
      (digit_comparing(curr_digits['tot_buy_qty_3'], prev_digits['tot_buy_qty_3']))),

    ((df['tot_sell_qty_3'] > prev['tot_sell_qty_3']) &
     ((df['tot_sell_qty_3'] > 0) & (prev['tot_sell_qty_3'] < 0)) &
      (digit_comparing(curr_digits['tot_sell_qty_3'], prev_digits['tot_sell_qty_3'])))
]
dir_mask1_vert_with_dig = sum(check.fillna(False).astype(int) for check in dir1_checks_vert_with_digits) >= 1

dir2_checks_vert_with_digits = [
    ((df['tot_buy_qty_1'] < prev['tot_buy_qty_1']) &
     ((df['tot_buy_qty_1'] < 0) & (prev['tot_buy_qty_1'] > 0)) &
      (digit_comparing(curr_digits['tot_buy_qty_1'], prev_digits['tot_buy_qty_1']))),

    ((df['tot_sell_qty_1'] > prev['tot_sell_qty_1']) &
     ((df['tot_sell_qty_1'] > 0) & (prev['tot_sell_qty_1'] < 0)) &
      (digit_comparing(curr_digits['tot_sell_qty_1'], prev_digits['tot_sell_qty_1']))),

    ((df['tot_buy_qty_2'] < prev['tot_buy_qty_2']) &
     ((df['tot_buy_qty_2'] < 0) & (prev['tot_buy_qty_2'] > 0)) &
      (digit_comparing(curr_digits['tot_buy_qty_2'], prev_digits['tot_buy_qty_2']))),

    ((df['tot_sell_qty_2'] > prev['tot_sell_qty_2']) &
     ((df['tot_sell_qty_2'] > 0) & (prev['tot_sell_qty_2'] < 0)) &
      (digit_comparing(curr_digits['tot_sell_qty_2'], prev_digits['tot_sell_qty_2']))),

    ((df['tot_buy_qty_3'] > prev['tot_buy_qty_3']) &
     ((df['tot_buy_qty_3'] > 0) & (prev['tot_buy_qty_3'] < 0)) &
      (digit_comparing(curr_digits['tot_buy_qty_3'], prev_digits['tot_buy_qty_3']))),

    ((df['tot_sell_qty_3'] < prev['tot_sell_qty_3']) &
     ((df['tot_sell_qty_3'] < 0) & (prev['tot_sell_qty_3'] > 0)) &
      (digit_comparing(curr_digits['tot_sell_qty_3'], prev_digits['tot_sell_qty_3'])))
]
dir_mask2_vert_with_dig = sum(check.fillna(False).astype(int) for check in dir2_checks_vert_with_digits) >= 1


dir1_checks_vert_6_digits = [
    ((df['tot_buy_qty_1'] > prev['tot_buy_qty_1']) &
      (for_6_digits(curr_digits['tot_buy_qty_1'], prev_digits['tot_buy_qty_1']))),

    ((df['tot_sell_qty_1'] < prev['tot_sell_qty_1']) &
      (for_6_digits(curr_digits['tot_sell_qty_1'], prev_digits['tot_sell_qty_1']))),

    ((df['tot_buy_qty_2'] > prev['tot_buy_qty_2']) &
      (for_6_digits(curr_digits['tot_buy_qty_2'], prev_digits['tot_buy_qty_2']))),

    ((df['tot_sell_qty_2'] < prev['tot_sell_qty_2']) &
      (for_6_digits(curr_digits['tot_sell_qty_2'], prev_digits['tot_sell_qty_2']))),

    ((df['tot_buy_qty_3'] < prev['tot_buy_qty_3']) &
      (for_6_digits(curr_digits['tot_buy_qty_3'], prev_digits['tot_buy_qty_3']))),

    ((df['tot_sell_qty_3'] > prev['tot_sell_qty_3']) &
      (for_6_digits(curr_digits['tot_sell_qty_3'], prev_digits['tot_sell_qty_3'])))
]
dir_mask1_vert_6_dig = sum(check.fillna(False).astype(int) for check in dir1_checks_vert_6_digits) >= 2

dir2_checks_vert_6_digits = [
    ((df['tot_buy_qty_1'] < prev['tot_buy_qty_1']) &
      (for_6_digits(curr_digits['tot_buy_qty_1'], prev_digits['tot_buy_qty_1']))),

    ((df['tot_sell_qty_1'] > prev['tot_sell_qty_1']) &
      (for_6_digits(curr_digits['tot_sell_qty_1'], prev_digits['tot_sell_qty_1']))),

    ((df['tot_buy_qty_2'] < prev['tot_buy_qty_2']) &
      (for_6_digits(curr_digits['tot_buy_qty_2'], prev_digits['tot_buy_qty_2']))),

    ((df['tot_sell_qty_2'] > prev['tot_sell_qty_2']) &
      (for_6_digits(curr_digits['tot_sell_qty_2'], prev_digits['tot_sell_qty_2']))),

    ((df['tot_buy_qty_3'] > prev['tot_buy_qty_3']) &
      (for_6_digits(curr_digits['tot_buy_qty_3'], prev_digits['tot_buy_qty_3']))),

    ((df['tot_sell_qty_3'] < prev['tot_sell_qty_3']) &
      (for_6_digits(curr_digits['tot_sell_qty_3'], prev_digits['tot_sell_qty_3'])))
]
dir_mask2_vert_6_dig = sum(check.fillna(False).astype(int) for check in dir2_checks_vert_6_digits) >= 2

# --------- Combine value-based and direction-based masks ---------
final_mask = ((condition1 | b_condition) & (dir_mask1 | dir_mask1_vert_6_dig)) | ((condition2 | s_condition) & (dir_mask2  | dir_mask2_vert_6_dig))

#final_mask = (condition1) | (condition2)

# Output the matching timestamps
with pd.option_context('display.max_rows', None):
    print(df.loc[final_mask, 'last_traded_time'])

