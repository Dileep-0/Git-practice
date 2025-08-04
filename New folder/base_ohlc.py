import os
import pandas as pd

import filenames

file_path = filenames.signals
# Load the CSV file
df = pd.read_csv(file_path)
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], dayfirst=True, errors='coerce')
date, file_name = file_path.split("_", 1)
output_file = f"{date}_signals.txt"
columns = pd.Series(df.columns)

# Check if the required columns exist
required_columns = ['last_traded_time']
if all(column in df.columns for column in required_columns):
    vertical_buys = []
    vertical_sells = []
    prev_5_buys, prev_5_sells = 0, 0
    # Iterate through rows starting from the second row
    for i in range(len(df)-1):
        '''if i < 5:
            previous_5_rows = df.iloc[:i+1]
        else:
            previous_5_rows = df.iloc[i-4:i+1]
        n_buy, n_sell = previous_5_rows['tot_buy_qty'],  previous_5_rows['tot_sell_qty']
        ce_buy, ce_sell = previous_5_rows['tot_buy_qty.1'], previous_5_rows['tot_sell_qty.1']
        pe_buy, pe_sell = previous_5_rows['tot_buy_qty.2'],previous_5_rows['tot_sell_qty.2']

        sum_of_5b = sum([sum(n_buy), sum(ce_buy), sum(pe_sell)])
        sum_of_5s = sum([sum(n_sell), sum(ce_sell), sum(pe_buy)])
        #print("hj", sum_of_5b, sum_of_5s)'''

        if i == 0:
            current_row = df.iloc[i]

            curr_buy, curr_sell = current_row['tot_buy_qty'], current_row['tot_sell_qty']
            curr_buy_ce, curr_sell_ce = current_row['tot_buy_qty.1'], current_row['tot_sell_qty.1']
            curr_buy_pe, curr_sell_pe = current_row['tot_buy_qty.2'], current_row['tot_sell_qty.2']

            tot_buy_sig, tot_sell_sig = current_row['tot_buy_sig'], current_row['tot_sell_sig']
            buy_sig, sell_sig = current_row['tot_buy_sig.1'], current_row['tot_sell_sig.1']
            buy_sig2, sell_sig2 = current_row['tot_buy_sig.2'], current_row['tot_sell_sig.2']

            ltp_price, bid_pr, ask_pr = current_row['ltp'], current_row['bid_price'], current_row['ask_price']
            ltp_price_ce, bid_pr_ce, ask_pr_ce = current_row['ltp.1'], current_row['bid_price.1'], current_row['ask_price.1']
            ltp_price_pe, bid_pr_pe, ask_pr_pe = current_row['ltp.2'], current_row['bid_price.2'], current_row['ask_price.2']

            ba_pr_dif = abs(bid_pr - ask_pr)

            buy_sum = sum([curr_buy, curr_buy_ce, curr_sell_pe])
            sell_sum = sum([curr_sell, curr_sell_ce, curr_buy_pe])

            prev_buy, prev_sell = current_row['tot_buy_qty'], current_row['tot_sell_qty']
            prev_buy_ce, prev_sell_ce = current_row['tot_buy_qty.1'], current_row['tot_sell_qty.1']
            prev_buy_pe, prev_sell_pe = current_row['tot_buy_qty.2'], current_row['tot_sell_qty.2']

            change_in_buy = buy_sum
            change_in_sell = sell_sum

            vertical_buys.append(buy_sum)
            vertical_sells.append(sell_sum)
            prev_ltp_price = current_row['ltp']

        else:
            current_row = df.iloc[i]
            future_row = df.iloc[i+1]

            curr_buy, curr_sell = current_row['tot_buy_qty'], current_row['tot_sell_qty']
            curr_buy_ce, curr_sell_ce = current_row['tot_buy_qty.1'], current_row['tot_sell_qty.1']
            curr_buy_pe, curr_sell_pe = current_row['tot_buy_qty.2'], current_row['tot_sell_qty.2']

            tot_buy_sig, tot_sell_sig = current_row['tot_buy_sig'], current_row['tot_sell_sig']
            buy_sig, sell_sig = current_row['tot_buy_sig.1'], current_row['tot_sell_sig.1']
            buy_sig2, sell_sig2 = current_row['tot_buy_sig.2'], current_row['tot_sell_sig.2']

            ltp_price, bid_pr, ask_pr = current_row['ltp'], current_row['bid_price'], current_row['ask_price']
            ltp_price_ce, bid_pr_ce, ask_pr_ce = current_row['ltp.1'], current_row['bid_price.1'], current_row['ask_price.1']
            ltp_price_pe, bid_pr_pe, ask_pr_pe = current_row['ltp.2'], current_row['bid_price.2'], current_row['ask_price.2']

            fut_n_open = current_row['nifty_cur_open']
            fut_ce_open = current_row['ce_cur_open']
            fut_pe_open = current_row['pe_cur_open']
            fut_ind_open = current_row['cur_open']

            n_open, n_close = current_row['nifty_prev_open'], current_row['nifty_prev_close']
            ce_open, ce_close = current_row['ce_prev_open'], current_row['ce_prev_close']
            pe_open, pe_close = current_row['pe_prev_open'], current_row['pe_prev_close']
            ind_open, ind_close = current_row['prev_open'], current_row['prev_close']
            previous_row = df.iloc[i-1]

            prev_n_close = current_row['nifty_pre_prev_close']
            prev_ce_close = current_row['ce_pre_prev_close']
            prev_pe_close = current_row['pe_pre_prev_close']
            ind_prev_close = current_row['pre_prev_close']

            ba_pr_dif = abs(bid_pr - ask_pr)

            buy_sum = sum([curr_buy, curr_buy_ce, curr_sell_pe])
            sell_sum = sum([curr_sell, curr_sell_ce, curr_buy_pe])

            prev_ltp_price = previous_row['ltp']

            prev_buy, prev_sell = previous_row['tot_buy_qty'], previous_row['tot_sell_qty']
            prev_buy_ce, prev_sell_ce = previous_row['tot_buy_qty.1'], previous_row['tot_sell_qty.1']
            prev_buy_pe, prev_sell_pe = previous_row['tot_buy_qty.2'], previous_row['tot_sell_qty.2']

            pre_ltp_price, pre_bid_pr, pre_ask_pr = previous_row['ltp'], previous_row['bid_price'], previous_row['ask_price']
            prev_ba_pr_diff = abs(pre_bid_pr - pre_ask_pr)

            prev_buy_sum = sum([prev_buy, prev_buy_ce, prev_sell_pe])
            prev_sell_sum = sum([prev_sell, prev_sell_ce, prev_buy_pe])
            
            

            change_in_buy = buy_sum + prev_buy_sum if buy_sum * prev_buy_sum > 0 else buy_sum - prev_buy_sum
            change_in_sell = sell_sum + prev_sell_sum if sell_sum * prev_sell_sum > 0 else sell_sum - prev_sell_sum

            vertical_buys.append(change_in_buy)
            vertical_sells.append(change_in_sell)

        bid_sum = bid_pr + bid_pr_ce + ask_pr_pe
        ask_sum = ask_pr + ask_pr_ce + bid_pr_pe
        #print(bid_sum, ask_sum)

        

        
        if i > 0:
            pr_diff = prev_ba_pr_diff - ba_pr_dif
            '''buy_candle = n_close < fut_n_open 
            sell_candle = n_close > fut_n_open'''
            b_fut = sum([ind_close <= fut_ind_open, n_close <= fut_n_open, ce_close <= fut_ce_open, pe_close >= fut_pe_open]) >= 3
            b_prev = sum([ind_prev_close <= ind_open, prev_n_close <= n_open, prev_ce_close <= ce_open, prev_pe_close > pe_open]) >= 3

            s_fut = sum([ind_close >= fut_ind_open, n_close >= fut_n_open, ce_close >= fut_ce_open, pe_close <= fut_pe_open]) >= 3
            s_prev = sum([ind_prev_close >= ind_open, prev_n_close >= n_open, prev_ce_close >= ce_open, prev_pe_close <= pe_open]) >= 3
            
            
            buy_candle = b_fut and b_prev
            sell_candle = s_fut and s_prev

        min_ltp = min(abs(ltp_price), abs(bid_pr), abs(ask_pr))
        max_ltp = max(abs(ltp_price), abs(bid_pr), abs(ask_pr))
        ltp_ni_check = abs(ltp_price) > max(abs(bid_pr), abs(ask_pr))

        ltp_diff = max_ltp - min_ltp
        if ltp_ni_check:
            ltp_ni_check_2 = 0.5 < ltp_diff
            ltp_ni_second_check = 0.5 < ltp_diff < 5
        else:
            ltp_ni_check_2 = 0.5 < ltp_diff
            ltp_ni_second_check = False

        ltp_ce_check = abs(ltp_price_ce) > max(abs(bid_pr_ce), abs(ask_pr_ce))
        min_ltp_ce = min(abs(ltp_price_ce), abs(bid_pr_ce), abs(ask_pr_ce))
        max_ltp_ce = max(abs(ltp_price_ce), abs(bid_pr_ce), abs(ask_pr_ce))
        
        ltp_diff_ce = max_ltp_ce - min_ltp_ce
        if ltp_ce_check:
            ltp_ce_check_2 = 0.25 <= ltp_diff_ce
        else:
            ltp_ce_check_2 = 0.4 < ltp_diff_ce
            
        ltp_pe_check = abs(ltp_price_pe) > max(abs(bid_pr_pe), abs(ask_pr_pe))
        min_ltp_pe = min(abs(ltp_price_pe), abs(bid_pr_pe), abs(ask_pr_pe))
        max_ltp_pe = max(abs(ltp_price_pe), abs(bid_pr_pe), abs(ask_pr_pe))
        
        ltp_diff_pe = max_ltp_pe - min_ltp_pe
        if ltp_pe_check:
            ltp_pe_check_2 = 0.25 < ltp_diff_pe
        else:
            ltp_pe_check_2 = 0.4 < ltp_diff_pe

        l=[]
        l.append(ltp_diff < 6.5)
        l.append(ltp_diff_ce < 4)
        l.append(ltp_diff_pe < 4)

        '''if (abs(ltp_price) > 15 or abs(prev_ltp_price) > 20) and sum(l) >= 2:
            ltp_check = True
            #ltp_check = sum([ltp_ni_check, ltp_ce_check, ltp_pe_check]) >= 1
            ltp_check_2 = sum([ltp_ni_check_2, ltp_ce_check_2, ltp_pe_check_2]) >= 2
        else:
            ltp_ni_check, ltp_ce_check, ltp_pe_check = False, False, False
            ltp_check = 0
            ltp_check_2 = 0'''
        if sum(l) >= 2:
            ltp_check = True
        else:
            ltp_check = False

        #print(i, vertical_buys[:i+1], vertical_sells[:i+1])

        if i < 5:
            previous_5_b_candles = vertical_buys[:i+1]
            previous_5_s_candles = vertical_sells[:i+1]
        else:
            previous_5_b_candles = vertical_buys[i-4:i+1]
            previous_5_s_candles = vertical_sells[i-4:i+1]

        curr_5_buys = sum(previous_5_b_candles)
        curr_5_sells =  sum(previous_5_s_candles)
        '''print("p", prev_5_buys, prev_5_sells)

        print("c", curr_5_buys, curr_5_sells)'''
        
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

        '''delta_contract_ch_buy = change_in_buy/ltp
        delta_contract_ch_sell = change_in_sell/ltp

        contract_signal = -1 if abs(delta_contract_ch_buy) > abs(delta_contract_ch_sell) else 1
        signal_power = max(abs(delta_contract_ch_buy), abs(delta_contract_ch_sell))/ min(abs(delta_contract_ch_buy), abs(delta_contract_ch_sell))

        contract_signal_power_b = contract_signal == 1 and signal_power > 1.5
        contract_signal_power_s = contract_signal == -1 and signal_power > 1.5'''



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

        '''if ce_avg_trade < 0 and pe_avg_trade < 0:
            ce_avg_trade = abs(ce_avg_trade)
            pe_avg_trade = abs(pe_avg_trade)'''

        '''bid_ask_buy_signal = bid_ask_flow(bid_ask_data, cond1)
        bid_ask_sell_signal = bid_ask_flow(bid_ask_data, cond2)'''

        #print(ltp_check, sum([ltp_ni_check, ltp_ce_check, ltp_pe_check]))
        '''ltp_check_less = sum([ltp_ni_check_less, ltp_ce_check_less, ltp_pe_check_less]) >= 3'''
        #and ((pr_diff>0) or (prev_ba_pr_diff < 1.5 and ba_pr_dif > 2.9) or (pr_diff<0 and prev_ba_pr_diff < 0.55))

        if ltp_check and count_Y > 3 and buy_candle \
            and (((buy_sum > prev_buy_sum) and (sell_sum < prev_sell_sum)) or (buy_sum > 0 and sell_sum < 0)) \
            and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
            (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))) :
            
            buy_flag = True
            print(f"{current_row['last_traded_time']} - buy")
            
            
        elif ltp_check and count_Y == 3 and count_N >= 1 and buy_candle \
            and (((buy_sum > prev_buy_sum) and (sell_sum < prev_sell_sum)) or (buy_sum > 0 and sell_sum < 0)) \
            and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
            (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))) :
            buy_flow_res =  buy_flow(data, conditions)
            if buy_flow_res > 3:
                buy_flag = True
                print(f"{current_row['last_traded_time']} - buy")

            else:
                buy_flag=False
        else:
            buy_flag = False

        if not buy_flag:
            if ltp_check and count_YES > 3  and sell_candle \
                and (((buy_sum < prev_buy_sum) and (sell_sum > prev_sell_sum)) or (buy_sum < 0 and sell_sum > 0)) \
                and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
                    (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))) :
                print(f"{current_row['last_traded_time']} - sell")

            elif ltp_check and count_YES == 3 and count_N >= 1 and sell_candle \
                and (((buy_sum < prev_buy_sum) and (sell_sum > prev_sell_sum)) or (buy_sum < 0 and sell_sum > 0)) \
                and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
                    (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))) :
                sell_flow_res =  sell_flow(data, conditions2)
                if sell_flow_res > 3:
                    print(f"{current_row['last_traded_time']} - sell")

        b_len_prev, s_len_prev = b_len_curr, s_len_curr
        p_change_in_buy, p_change_in_sell = change_in_buy, change_in_sell
        prev_5_buys  = curr_5_buys
        prev_5_sells = curr_5_sells

else:
    print(f"Error: The file must contain the following columns: {', '.join(required_columns)}")
