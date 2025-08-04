import os
import pandas as pd

import filenames

file_path = filenames.signals
# Load the CSV file
df = pd.read_csv(file_path)
date, file_name = file_path.split("_", 1)
output_file = f"{date}_signals.txt"
columns = pd.Series(df.columns)

# Check if the required columns exist
required_columns = ['last_traded_time']
if all(column in df.columns for column in required_columns):
    with open(output_file, "w") as f:
    # Iterate through rows starting from the second row
        for i in range(1, len(df)):
            previous_row = df.iloc[i-1]

            prev_buy, prev_sell = previous_row['tot_buy_qty'], previous_row['tot_sell_qty']
            prev_buy_ce, prev_sell_ce = previous_row['tot_buy_qty.1'], previous_row['tot_sell_qty.1']
            prev_buy_pe, prev_sell_pe = previous_row['tot_buy_qty.2'], previous_row['tot_sell_qty.2']

            prev_open, prev_close = previous_row['Open_NSE:NIFTY50-INDEX'], previous_row['Close_9']
            prev_body = abs(prev_open-prev_close)

            prev_buy_sum = sum([prev_buy, prev_buy_ce, prev_sell_pe])
            prev_sell_sum = sum([prev_sell, prev_sell_ce, prev_buy_pe])

            current_row = df.iloc[i]

            curr_buy, curr_sell = current_row['tot_buy_qty'], current_row['tot_sell_qty']
            curr_buy_ce, curr_sell_ce = current_row['tot_buy_qty.1'], current_row['tot_sell_qty.1']
            curr_buy_pe, curr_sell_pe = current_row['tot_buy_qty.2'], current_row['tot_sell_qty.2']

            curr_open, curr_close = current_row['Open_NSE:NIFTY50-INDEX'], current_row['Close_9']
            curr_body = abs(curr_open-curr_close)
            

            tot_buy_sig, tot_sell_sig = current_row['tot_buy_sig'], current_row['tot_sell_sig']
            buy_sig, sell_sig = current_row['tot_buy_sig.1'], current_row['tot_sell_sig.1']
            buy_sig2, sell_sig2 = current_row['tot_buy_sig.2'], current_row['tot_sell_sig.2']

            avg_trade = current_row['avg_trade_price']
            ce_avg_trade = current_row['avg_trade_price.1']
            pe_avg_trade = current_row['avg_trade_price.2']
            #bank_avg_trade = current_row['avg_trade_price.3']

            n_bid_ask_size, n_bid_ask_pr =  current_row['n_bid_ask_diff'], current_row['n_bid_ask_pr_diff']
            ce_bid_ask_size, ce_bid_ask_pr =  current_row['ce_bid_ask_diff'], current_row['ce_bid_ask_pr_diff']
            pe_bid_ask_size, pe_bid_ask_pr =  current_row['pe_bid_ask_diff'], current_row['pe_bid_ask_pr_diff']

            bid_ask_data = {
                "nba" : float(n_bid_ask_size),
                "nbap" : float(n_bid_ask_pr),
                "cba" : float(ce_bid_ask_size),
                "cbap" : float(ce_bid_ask_pr),
                "pba" : float(pe_bid_ask_size),
                "pbap" : float(pe_bid_ask_pr)
            }
            print(current_row['last_traded_time'], "bid_ask_data", bid_ask_data)

            cond1 = {
                "nba": lambda x: x < 0,
                "nbap": lambda x: x > 0,
                "cba": lambda x: x < 0,
                "cbap": lambda x: x > -0.09,
                "pba": lambda x: x < 0,
                "pbap": lambda x: x > -0.09,
            }
            cond2 = {
                "nba": lambda x: x > 0,
                "nbap": lambda x: x < 0,
                "cba": lambda x: x > 0,
                "cbap": lambda x: x < 0.09,
                "pba": lambda x: x > 0,
                "pbap": lambda x: x < 0.09,
            }
            def bid_ask_flow(bid_ask_data, condition):
                return sum(1 for key, val in bid_ask_data.items() if condition[key](val)) >= 4
            

            '''bid = current_row['bid_size']
            ask = current_row['ask_size']'''

            buy_sum = sum([curr_buy, curr_buy_ce, curr_sell_pe])
            sell_sum = sum([curr_sell, curr_sell_ce, curr_buy_pe])


            if i==1:
                p_change_in_buy = prev_buy_sum
                p_change_in_sell = prev_sell_sum
                change_in_buy = buy_sum - prev_buy_sum
                change_in_sell = sell_sum - prev_sell_sum
            else:
                change_in_buy = buy_sum - prev_buy_sum
                change_in_sell = sell_sum - prev_sell_sum

            if i==1:
                b_len_prev = len(str(abs(prev_buy_sum)))
                s_len_prev = len(str(abs(prev_sell_sum)))
                b_len_curr = len(str(abs(change_in_buy)))
                s_len_curr = len(str(abs(change_in_sell)))
            else:
                b_len_curr = len(str(abs(change_in_buy)))
                s_len_curr = len(str(abs(change_in_sell)))

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
            
            signals = [
                    (tot_buy_sig, abs(curr_buy)),
                    (tot_sell_sig, abs(curr_sell)),
                    (buy_sig, abs(curr_buy_ce)),
                    (sell_sig, abs(curr_sell_ce)),
                    (buy_sig2, abs(curr_buy_pe)),
                    (sell_sig2, abs(curr_sell_pe)),
                ]
            lakh_set = {0}

                # Check conditions for 'Y' and 'YES'
            if count_Y >= 3 :
                for signal_value, threshold in signals:
                    if signal_value == 'Y' and threshold > 100000:
                        lakh_set.add(1)
                        break  # Exit loop once condition is met

            if count_YES >= 3 :
                for signal_value, threshold in signals:
                    if signal_value == 'YES' and threshold > 100000:
                        lakh_set.add(1)
                        break

            check_lakh = 1 in lakh_set
            lakh_set.discard(1)

            buy_flag = False

            if ce_avg_trade < 0 and pe_avg_trade < 0:
                ce_avg_trade = abs(ce_avg_trade)
                pe_avg_trade = abs(pe_avg_trade)

            bid_ask_buy_signal = bid_ask_flow(bid_ask_data, cond1)
            bid_ask_sell_signal = bid_ask_flow(bid_ask_data, cond2)
            print(current_row['last_traded_time'], "bid_ask_data", bid_ask_data, bid_ask_buy_signal, bid_ask_sell_signal)
            
            if (bid_ask_buy_signal or bid_ask_sell_signal) and count_Y > 3 and (buy_sum > prev_buy_sum) and (sell_sum < prev_sell_sum) and (buy_sum > 0 and sell_sum < 0) \
                and ((buy_sum * prev_buy_sum < 0) or (len(str(prev_buy_sum)) < len(str(buy_sum))) or 
                (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))):
                
                buy_flag = True
                f.write(f"{current_row['last_traded_time']} - buy\n")
                
                
            elif (bid_ask_buy_signal or bid_ask_sell_signal) and count_Y == 3 and count_N >= 1 and  (buy_sum > prev_buy_sum) and (sell_sum < prev_sell_sum) and (buy_sum > 0 and sell_sum < 0) \
                and ((buy_sum * prev_buy_sum < 0) or (len(str(prev_buy_sum)) < len(str(buy_sum))) or 
                (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))) :
                buy_flow_res =  buy_flow(data, conditions)
                if buy_flow_res > 3:
                    buy_flag = True
                    f.write(f"{current_row['last_traded_time']} - buy\n")

                else:
                    buy_flag=False
            else:
                buy_flag = False

            if not buy_flag:
                if (bid_ask_buy_signal or bid_ask_sell_signal) and count_YES > 3  and (buy_sum < prev_buy_sum) and (sell_sum > prev_sell_sum) and (buy_sum < 0 and sell_sum > 0) \
                    and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
                        (sell_sum * prev_sell_sum < 0) or (len(str(prev_sell_sum)) < len(str(sell_sum)))) :
                    f.write(f"{current_row['last_traded_time']} - sell\n")

                elif (bid_ask_buy_signal or bid_ask_sell_signal) and count_YES == 3 and count_N >= 1  and  (buy_sum < prev_buy_sum) and (sell_sum > prev_sell_sum) and (buy_sum < 0 and sell_sum > 0) \
                    and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
                        (sell_sum * prev_sell_sum < 0) or (len(str(prev_sell_sum)) < len(str(sell_sum)))) :
                    sell_flow_res =  sell_flow(data, conditions2)
                    if sell_flow_res > 3:
                        f.write(f"{current_row['last_traded_time']} - sell\n")

            b_len_prev, s_len_prev = b_len_curr, s_len_curr
            p_change_in_buy, p_change_in_sell = change_in_buy, change_in_sell

else:
    print(f"Error: The file must contain the following columns: {', '.join(required_columns)}")

print(f"Output written to {output_file}")