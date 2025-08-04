
import os
import pandas as pd

# Path to your folder
folder_path = r'C:\Users\dilee\Fyers_copy\New folder'

# Required columns (original names preserved for final DataFrame)
required_columns = [
    "last_traded_time", "ltp", "bid_price", "ask_price", 
    "tot_buy_qty", "tot_buy_sig", "tot_sell_qty", "tot_sell_sig",
    "ltp.1", "bid_price.1", "ask_price.1", "tot_buy_qty.1", "tot_buy_sig.1", "tot_sell_qty.1", "tot_sell_sig.1",
    "ltp.2", "bid_price.2", "ask_price.2", "tot_buy_qty.2", "tot_buy_sig.2", "tot_sell_qty.2", "tot_sell_sig.2"
]

# Lowercased version for validation
required_columns_lower = list(dict.fromkeys([col.lower() for col in required_columns]))

merged_df = pd.DataFrame()

for filename in os.listdir(folder_path):
    lower_filename = filename.lower()
    if lower_filename.endswith("fut.csv") and "05m_nifty" in lower_filename:
        file_path = os.path.join(folder_path, filename)
        try:
            df = pd.read_csv(file_path)
            # Map original to lowercase for matching
            df_col_map = {col.lower(): col for col in df.columns}
            df_columns_lower = list(df_col_map.keys())

            if all(col in df_columns_lower for col in required_columns_lower):
                # Select only required columns, keeping original case
                selected_columns = [df_col_map[col] for col in required_columns_lower]
                df_selected = df[selected_columns]
                merged_df = pd.concat([merged_df, df_selected], ignore_index=True)
                print(f"Merged: {filename}")
            else:
                print(f"Skipped: {filename} (missing required columns)")
        except Exception as e:
            print(f"Error reading {filename}: {e}")

# Save the merged result
if not merged_df.empty:
    output_path = os.path.join(folder_path, 'merged_data.csv')
    merged_df.to_csv(output_path, index=False)
    print(f"\n✅ Merged CSV with only required columns saved to: {output_path}")
else:
    print("\n⚠️ No files matched all criteria. No output created.")
