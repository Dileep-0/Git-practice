from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, normalize
import os
import matplotlib.pyplot as plt
import re
from scipy.stats import f
import time

# Load the CSV file
file_path = "05-11-2024_05_min_NIFTY24NOVFUT.csv" 


# Regular expression to capture the date in the format DD-MM-YYYY
match = re.match(r"(\d{2}-\d{2}-\d{4})", file_path)
if match:
    date_str = match.group(1)

# Output directory for results

#output_dir = "pca_two"
output_dir = f"pca_{date_str}"
os.makedirs(output_dir, exist_ok=True)

last_row_processed = 0
last_plot_path = None

while True:
    data = pd.read_csv(file_path)
    #data = pd.read_csv(file_path, sep='\t')
    df = pd.DataFrame(data)
    rows_removed = False

# Check if the data has enough rows
    if df.shape[0] < 6 or df.shape[0] <= last_row_processed:
        print("Waiting for at least 6 rows...")
        time.sleep(60)  # Wait for 1 minute before checking again
        continue

# Preprocess the data
# Assuming the CSV contains numerical data

    '''columns_for_pca = ['tot_buy_qty', 'tot_sell_qty', 'bid_size', 'ask_size', 'bid1', 'bid2', 'ask1', 'ask2', 'c1', 'c2', 'p1', 'p2']  # Replace with your chosen column names'''

    if not rows_removed and df.shape[0] > 12:
        print("removing the first two rows")
        df = df.iloc[2:].reset_index(drop=True)
        rows_removed = True

    # Ensure that the selected columns exist in the data
    '''if not all(col in df.columns for col in columns_for_pca):
        missing_cols = [col for col in columns_for_pca if col not in df.columns]
        raise ValueError(f"The following columns are missing in the file: {missing_cols}")'''

    # Select only the specified columns for PCA
    last_traded_time = df['last_traded_time']
    numeric_data = df.select_dtypes(include=['float64', 'int64'])


    # Loop through rows starting from the 6th
    for start_row in range(max(5, last_row_processed), df.shape[0]):
        subset_data = numeric_data.iloc[:start_row+1]  # Include all rows up to the current row

        standardized_data = (subset_data - subset_data.mean()) / subset_data.std()
        pca = PCA(n_components=2, random_state=42)
        principal_components = pca.fit_transform(standardized_data)

        pca_df = pd.DataFrame(principal_components,columns= [f"PC{i + 1}" for i in range(2)])

        eigenvalues = pca.explained_variance_  # Variances of principal components
        t2_stats = np.sum((pca_df / np.sqrt(eigenvalues)) ** 2, axis=1)
        pca_df['Hotelling_T2'] = t2_stats
        pca_df.insert(0, 'last_traded_time', last_traded_time.iloc[:start_row+1].values)
        last_time_value = pca_df['last_traded_time'].iloc[-1]

        alpha = 0.1
        n, p = start_row, pca.n_components_
        control_limit = p * (n - 1) / (n - p) * f.ppf(1 - alpha, p, n - p)
        pca_df['control_limit'] = control_limit
        outliers = pca_df[pca_df['Hotelling_T2'] > control_limit]

        safe_time = last_time_value.replace(":", "-").replace(" ", "_")
        projections_path = os.path.join(output_dir, f"pca_results_{safe_time}.csv")
        pca_df.to_csv(projections_path, index=False)
        if (pca_df['control_limit'].iloc[-1] < pca_df['Hotelling_T2'].iloc[-1]) or (pca_df['Hotelling_T2'].iloc[-2]*5 < pca_df['Hotelling_T2'].iloc[-1]):
            if (pca_df['Hotelling_T2'].iloc[-1] > pca_df['Hotelling_T2'].iloc[-9:-1].max()) and (pca_df['Hotelling_T2'].iloc[-1] > (pca_df['Hotelling_T2'].iloc[-6:-1].max())*2):
                print("required time points: ",safe_time)
        
        #print(f"PCA projection plot updated and saved to {projections_path}")

    last_row_processed = df.shape[0]

    # Pause before next check
    time.sleep(60)