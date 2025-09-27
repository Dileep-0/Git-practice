import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

def save_ce_pe_scatter(ce_file, pe_file):
    # Main folder name
    main_folder = "CE_vs_PE_Scatter"
    os.makedirs(main_folder, exist_ok=True)

    # Load CE & PE CSVs
    df_ce = pd.read_csv(ce_file)
    df_pe = pd.read_csv(pe_file)

    # Convert time columns
    df_ce["last_traded_time"] = pd.to_datetime(df_ce["last_traded_time"])
    df_pe["last_traded_time"] = pd.to_datetime(df_pe["last_traded_time"])

    # Set index for resampling
    df_ce = df_ce.set_index("last_traded_time")
    df_pe = df_pe.set_index("last_traded_time")

    # Resample into 5-minute groups
    grouped_ce = df_ce.resample("5T")
    grouped_pe = df_pe.resample("5T")

    # Iterate over matching groups
    for (time_ce, group_ce), (time_pe, group_pe) in zip(grouped_ce, grouped_pe):
        if group_ce.empty or group_pe.empty:
            continue

        # Ensure same timestamp
        if time_ce != time_pe:
            continue

        # Trim to equal length
        min_len = min(len(group_ce), len(group_pe))
        group_ce = group_ce.iloc[:min_len]
        group_pe = group_pe.iloc[:min_len]

        # Subfolder for this time point
        time_folder = os.path.join(main_folder, time_ce.strftime("%Y%m%d_%H%M"))
        os.makedirs(time_folder, exist_ok=True)
        r2_results = {}

        # Scatter pairs: (CE.buy vs PE.sell) and (CE.sell vs PE.buy)
        pairs = [
            ("tot_buy_qty", "tot_sell_qty", "CE.buy vs PE.sell"),
            ("tot_sell_qty", "tot_buy_qty", "CE.sell vs PE.buy")
        ]

        for ce_col, pe_col, label in pairs:
            plt.figure()

            X = group_ce[ce_col].values.reshape(-1, 1)
            Y = group_pe[pe_col].values

            plt.scatter(X, Y, alpha=0.6, label="Data")
            r2 = None

            if len(X) > 1:
                model = LinearRegression()
                model.fit(X, Y)
                Y_pred = model.predict(X)
                slope = model.coef_[0]
                intercept = model.intercept_
                r2 = model.score(X, Y)

                # Plot regression line
                plt.plot(X, Y_pred, color="red", label="Fit")

                # Equation & R²
                eq_text = f"y = {slope:.2f}x + {intercept:.2f}\nR² = {r2:.3f}"
                plt.text(0.05, 0.95, eq_text, transform=plt.gca().transAxes,
                         fontsize=10, verticalalignment='top',
                         bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
                
            r2_results[label] = f"{r2:.3f}" if r2 is not None else "N/A"

            plt.xlabel(f"CE {ce_col}")
            plt.ylabel(f"PE {pe_col}")
            plt.title(f"CE {ce_col} vs PE {pe_col} ({time_ce.strftime('%Y-%m-%d %H:%M')})")
            plt.legend()

            # Save plot
            filename = os.path.join(time_folder, f"CE_{ce_col}_vs_PE_{pe_col}.png")
            plt.savefig(filename)
            plt.close()

        '''if (
            (float(r2_results['CE.buy vs PE.sell']) > 0.4 and float(r2_results['CE.sell vs PE.buy']) > 0.4) or
            (float(r2_results['CE.buy vs PE.sell']) > 0.6 and 0.1 < float(r2_results['CE.sell vs PE.buy']) < 0.4) or
            (0.1 < float(r2_results['CE.buy vs PE.sell']) < 0.4 and float(r2_results['CE.sell vs PE.buy']) > 0.6) or
            (float(r2_results['CE.buy vs PE.sell']) < 0.065 and float(r2_results['CE.sell vs PE.buy']) < 0.065)
        ):print(f"[{time_ce.strftime('%Y-%m-%d %H:%M')}] R²={r2_results['CE.buy vs PE.sell']} | "
              f"R²={r2_results['CE.sell vs PE.buy']}")'''
            
        print(f"[{time_ce.strftime('%Y-%m-%d %H:%M')}] R²={r2_results['CE.buy vs PE.sell']} | "
              f"R²={r2_results['CE.sell vs PE.buy']}")

    print(f"All CE vs PE scatter plots saved in: {main_folder}")


# Example usage
save_ce_pe_scatter("04-09-2025_NIFTY2590924900CE.csv",
                   "04-09-2025_NIFTY2590924900PE.csv")
