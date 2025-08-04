import pandas as pd

def append_difference_column(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Check if required columns exist
    if 'n_bid_ask_diff' not in df.columns or 'ce_bid_ask_diff' not in df.columns:
        print("Error: Required columns not found in the file.")
        return
    
    # Compute the difference
    df['nce_ba_size'] = df['n_bid_ask_diff'] - df['ce_bid_ask_diff']
    df['nce_ba_pr'] = df['n_bid_ask_pr_diff'] - df['ce_bid_ask_pr_diff']
    df['npe_ba_size'] = df['n_bid_ask_diff'] - df['pe_bid_ask_diff']
    df['npe_ba_pr'] = df['n_bid_ask_pr_diff'] - df['pe_bid_ask_pr_diff']
    df['cepe_ba_size'] = df['ce_bid_ask_diff'] - df['pe_bid_ask_diff']
    df['cepe_ba_pr'] = df['ce_bid_ask_pr_diff'] - df['pe_bid_ask_pr_diff']
    

    
    # Save back to the same file
    df.to_csv(file_path, index=False)
    print("Column 'diff' appended successfully.")

# Example usage
file_name = "02-01-2025_05m_NIFTY25JANFUT.csv"
append_difference_column(file_name)