import pandas as pd

# Load the CSV file
file_path = "03-01-2025_05m_NIFTY25JANFUT.csv"  # Replace with your actual file path
df = pd.read_csv(file_path)

columns = pd.Series(df.columns)

# Check if the required columns exist
required_columns = ['last_traded_time', 'bid_size', 'ask_size']
if all(column in df.columns for column in required_columns):
    # Iterate through rows starting from the second row
    for i in range(1, len(df)):
        previous_row = df.iloc[i-1]

        prev_buy, prev_sell = previous_row['tot_buy_qty'], previous_row['tot_sell_qty']
        prev_buy_ce, prev_sell_ce = previous_row['tot_buy_qty.1'], previous_row['tot_sell_qty.1']
        prev_buy_pe, prev_sell_pe = previous_row['tot_buy_qty.2'], previous_row['tot_sell_qty.2']

        current_row = df.iloc[i]

        curr_buy, curr_sell = current_row['tot_buy_qty'], current_row['tot_sell_qty']
        curr_buy_ce, curr_sell_ce = current_row['tot_buy_qty.1'], current_row['tot_sell_qty.1']
        curr_buy_pe, curr_sell_pe = current_row['tot_buy_qty.2'], current_row['tot_sell_qty.2']

        tot_buy_sig, tot_sell_sig = current_row['tot_buy_sig'], current_row['tot_sell_sig']
        buy_sig, sell_sig = current_row['tot_buy_sig.1'], current_row['tot_sell_sig.1']
        buy_sig2, sell_sig2 = current_row['tot_buy_sig.2'], current_row['tot_sell_sig.2']

        avg_trade = current_row['avg_trade_price']
        ce_avg_trade = current_row['avg_trade_price.1']
        pe_avg_trade = current_row['avg_trade_price.2']

        data = {
            "nb": (prev_buy, curr_buy),  
            "ns": (prev_sell, curr_sell),  
            "cb": (prev_buy_ce, curr_buy_ce),  
            "cs": (prev_sell_ce, curr_sell_ce),  
            "pb": (prev_buy_pe, curr_buy_pe),  
            "ps": (prev_sell_pe, curr_sell_pe),  
        }
        conditions = {
            "nb": lambda x, y: x < y,
            "ns": lambda x, y: x > y,
            "cb": lambda x, y: x < y,
            "cs": lambda x, y: x > y,
            "pb": lambda x, y: x > y,
            "ps": lambda x, y: x < y,
        }
        conditions2 = {
            "nb": lambda x, y: x > y,
            "ns": lambda x, y: x < y,
            "cb": lambda x, y: x > y,
            "cs": lambda x, y: x < y,
            "pb": lambda x, y: x < y,
            "ps": lambda x, y: x > y,
        }

        pair1 = (tot_buy_sig, tot_sell_sig)
        pair2 = (buy_sig, sell_sig)
        pair3 = (buy_sig2, sell_sig2)
        pairs = [pair1, pair2, pair3]

        def count_values(pairs, value):
            """Counts occurrences of a specific value across all pairs."""
            return sum(pair.count(value) for pair in pairs)

        count_Y = count_values(pairs, 'Y')
        count_YES = count_values(pairs, 'YES')
        count_N = count_values(pairs, 'N')

        def buy_flow(data, conditions):
            flow_res = 0
            for key, (val1, val2) in data.items():
                if conditions[key](val1, val2):
                    flow_res += 1
            return flow_res
        
        def sell_flow(data, conditions2):
            flow_res = 0
            for key, (val1, val2) in data.items():
                if conditions2[key](val1, val2):
                    flow_res += 1
            return flow_res

        buy_flag = False

        if count_Y > 3 and avg_trade > 0 and abs(ce_avg_trade) > abs(pe_avg_trade) and \
         (current_row['ask_size'] > current_row['bid_size']):
            buy_flag = True
            print(f"Condition met at time_stamp: {current_row['last_traded_time']}")
        elif count_Y == 3 and count_N >= 1 and avg_trade > 0 and abs(ce_avg_trade) > abs(pe_avg_trade) and \
            (current_row['ask_size'] > current_row['bid_size']):
            buy_flow_res =  buy_flow(data, conditions)
            print('buy_flow_res', buy_flow_res)
            if buy_flow_res > 3:
                buy_flag = True
                print(f"Condition met at time_stamp: {current_row['last_traded_time']}")
            else:
                buy_flag=False
        else:
            buy_flag = False

        if not buy_flag:
            if count_YES > 3 and avg_trade < 0 and abs(ce_avg_trade) < abs(pe_avg_trade) and \
             (current_row['bid_size'] > current_row['ask_size']):
                print(f"Condition met at time_stamp: {current_row['last_traded_time']}")
            elif count_YES == 3 and count_N >= 1 and avg_trade < 0 and abs(ce_avg_trade) < abs(pe_avg_trade) and \
             (current_row['bid_size'] > current_row['ask_size']):
                sell_flow_res =  sell_flow(data, conditions2)
                print('sell_flow_res', sell_flow_res)
                if sell_flow_res > 3:
                    print(f"Condition met at time_stamp: {current_row['last_traded_time']}")

else:
    print(f"Error: The file must contain the following columns: {', '.join(required_columns)}")
