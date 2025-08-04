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

        prev_ltq_n, prev_ltq_ce, prev_ltq_pe = previous_row['last_traded_qty'], previous_row['last_traded_qty.1'], previous_row['last_traded_qty.2']

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

        prev_ltp_price = previous_row['ltp']

        ltp_price, bid_pr, ask_pr = current_row['ltp'], current_row['bid_price'], current_row['ask_price']
        ltp_price_ce, bid_pr_ce, ask_pr_ce = current_row['ltp.1'], current_row['bid_price.1'], current_row['ask_price.1']
        ltp_price_pe, bid_pr_pe, ask_pr_pe = current_row['ltp.2'], current_row['bid_price.2'], current_row['ask_price.2']

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

        '''if sum(l) >= 2:'''
        if (abs(ltp_price) > 15 or abs(prev_ltp_price) > 20) and sum(l) >= 2:
            ltp_check = sum([ltp_ni_check, ltp_ce_check, ltp_pe_check]) >= 1
            ltp_check_2 = sum([ltp_ni_check_2, ltp_ce_check_2, ltp_pe_check_2]) >= 2
        else:
            ltp_ni_check, ltp_ce_check, ltp_pe_check = False, False, False
            ltp_check = 0
            ltp_check_2 = 0
            #ltp_ni_second_check = False

        ltp = current_row['ltp']

        ltq_n, ltq_ce, ltq_pe = current_row['last_traded_qty'], current_row['last_traded_qty.1'], current_row['last_traded_qty.2']
        
        ltq_ni_check = prev_ltq_n < ltq_n
        ltq_ce_check = prev_ltq_ce < ltq_ce
        ltq_pe_check = prev_ltq_pe < ltq_pe
    
        bid_ask_data = {
            "nba" : float(n_bid_ask_size),
            "nbap" : float(n_bid_ask_pr),
            "cba" : float(ce_bid_ask_size),
            "cbap" : float(ce_bid_ask_pr),
            "pba" : float(pe_bid_ask_size),
            "pbap" : float(pe_bid_ask_pr)
        }
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
            return sum(1 for key, val in bid_ask_data.items() if condition[key](val)) >= 6
        

        '''bid = current_row['bid_size']
        ask = current_row['ask_size']'''

        buy_sum = sum([curr_buy, curr_buy_ce, curr_sell_pe])
        sell_sum = sum([curr_sell, curr_sell_ce, curr_buy_pe])
        buy_ratio = buy_sum/sell_sum
        sell_ratio = sell_sum/buy_sum


        if i==1:
            p_change_in_buy = prev_buy_sum
            p_change_in_sell = prev_sell_sum
            change_in_buy = buy_sum - prev_buy_sum
            change_in_sell = sell_sum - prev_sell_sum
        else:
            change_in_buy = buy_sum - prev_buy_sum
            change_in_sell = sell_sum - prev_sell_sum
        
        ch_b_rtio = change_in_buy/change_in_sell
        ch_s_rtio = change_in_sell/change_in_buy
        
        buy_add = change_in_buy + buy_sum
        sel_add = change_in_sell + sell_sum
        buy_len = len(str(abs(buy_add)))
        sell_len = len(str(abs(sel_add)))
        min_len = min(buy_len, sell_len) >= 6

        diff_of_hor = abs(abs(buy_ratio) - abs(sell_ratio))
        diff_of_ver = abs(abs(ch_b_rtio) - abs(ch_s_rtio))

        
        

        #same flow
        for_buy  = abs(buy_ratio) > abs(sell_ratio) and abs(ch_b_rtio) > abs(ch_s_rtio) and ((abs(buy_ratio) > 1.48 and abs(sell_ratio) < 0.4) or diff_of_hor < 0.3) and ((abs(ch_b_rtio) > 1.48 and abs(ch_s_rtio) < 0.4) or diff_of_ver < 0.3) and (abs(sell_ratio)*0.9 > abs(ch_s_rtio))
        for_sell = abs(sell_ratio) > abs(buy_ratio) and abs(ch_s_rtio) > abs(ch_b_rtio) and ((abs(sell_ratio) > 1.48 and abs(buy_ratio) < 0.4) or diff_of_hor < 0.3) and ((abs(ch_s_rtio) > 1.48 and abs(ch_b_rtio) < 0.4) or diff_of_ver < 0.3) and (abs(buy_ratio)*0.9 > abs(ch_b_rtio))
        #opposite flow
        buy_2 = (abs(buy_ratio) < abs(sell_ratio) and abs(ch_b_rtio) < abs(ch_s_rtio)) and abs(buy_ratio) > 0.3 and abs(ch_b_rtio) > 0.3 and abs(buy_ratio)*0.9 < abs(ch_b_rtio) and (diff_of_hor >= 1 or diff_of_ver >= 1)
        sell_2 = (abs(sell_ratio) < abs(buy_ratio) and abs(ch_s_rtio) < abs(ch_b_rtio)) and abs(sell_ratio) > 0.3 and abs(ch_s_rtio) > 0.3 and abs(sell_ratio)*0.9 < abs(ch_s_rtio) and (diff_of_hor >= 1 or diff_of_ver >= 1)

        """buy_3 = (abs(buy_ratio) > abs(sell_ratio) and abs(ch_b_rtio) < abs(ch_s_rtio)) and ((abs(buy_ratio) > 1.48 and abs(sell_ratio) > 0.1) or diff_of_hor < 0.5) and ((abs(ch_b_rtio) > 0.1 and abs(ch_s_rtio) > 1.48) or diff_of_ver < 0.5)
        sell_3 = (abs(sell_ratio) > abs(buy_ratio) and abs(ch_s_rtio) < abs(ch_b_rtio)) and ((abs(buy_ratio) > 0.1 and abs(sell_ratio) > 1.48) or diff_of_hor < 0.5) and (((abs(ch_b_rtio) > 1.48 and abs(ch_s_rtio) > 0.1 )) or diff_of_ver < 0.5)"""

        buy_3 = (abs(buy_ratio) < abs(sell_ratio) and abs(ch_b_rtio) > abs(ch_s_rtio)) and ((abs(buy_ratio) > 0.1 and abs(sell_ratio) > 1.48) or diff_of_hor < 0.5)and ((abs(ch_b_rtio) > 1.48 and abs(ch_s_rtio) > 0.1) or diff_of_ver < 0.5)
        sell_3 = (abs(sell_ratio) < abs(buy_ratio) and abs(ch_s_rtio) > abs(ch_b_rtio)) and ((abs(buy_ratio) > 1.48 and abs(sell_ratio) > 0.1) or diff_of_hor < 0.5) and ((abs(ch_b_rtio) > 0.1 and abs(ch_s_rtio) > 1.48) or diff_of_ver < 0.5)

        list = [float(abs(buy_ratio)), float(abs(sell_ratio)), float(abs(ch_b_rtio)), float(abs(ch_s_rtio))]
        list.sort()
        
        buy_5 = (abs(buy_ratio) < 0.1 or abs(sell_ratio) < 0.1 or abs(ch_b_rtio) < 0.1 or abs(ch_s_rtio) < 0.1) and list[1] > 0.2
        sell_5 = (abs(buy_ratio) < 0.1 or abs(sell_ratio) < 0.1 or abs(ch_b_rtio) < 0.1 or abs(ch_s_rtio) < 0.1) and list[1] > 0.2

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

        if ltp == 0 or ltp is None:
            delta_contract_ch_buy = 0
            delta_contract_ch_sell = 0
        else:
            delta_contract_ch_buy = change_in_buy / ltp
            delta_contract_ch_sell = change_in_sell / ltp

        contract_signal = -1 if abs(delta_contract_ch_buy) > abs(delta_contract_ch_sell) else 1
        if min(abs(delta_contract_ch_buy), abs(delta_contract_ch_sell)) == 0:
            signal_power = 0  # or maybe float('inf'), depending on what you want
        else:
            signal_power = max(abs(delta_contract_ch_buy), abs(delta_contract_ch_sell))/ min(abs(delta_contract_ch_buy), abs(delta_contract_ch_sell))

        contract_signal_power_b = (contract_signal == 1 and signal_power > 1) or signal_power > 1.5
        contract_signal_power_s = (contract_signal == -1 and signal_power > 1) or signal_power > 1.5



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

        #print(ltp_check, sum([ltp_ni_check, ltp_ce_check, ltp_pe_check]))
        '''ltp_check_less = sum([ltp_ni_check_less, ltp_ce_check_less, ltp_pe_check_less]) >= 3'''
        ltq_check = ltq_ni_check or ltq_ce_check or ltq_pe_check
        
        if (ltp_check or ltp_check_2) and count_Y > 3 and (for_buy or buy_2 or buy_3 ) and contract_signal_power_b and (((buy_sum > prev_buy_sum) and (sell_sum < prev_sell_sum)) or (buy_sum > 0 and sell_sum < 0)) \
            and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
            (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))) :
            buy_flag = True
            print(f"{current_row['last_traded_time']} - buy")
            print(ltp_price_ce/ltp_price_pe)

        elif (ltp_check or ltp_check_2) and count_Y == 3 and count_N >= 1 and (for_buy or buy_2 or buy_3 ) and contract_signal_power_b and (((buy_sum > prev_buy_sum) and (sell_sum < prev_sell_sum)) or (buy_sum > 0 and sell_sum < 0)) \
            and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
            (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))) :
            buy_flow_res =  buy_flow(data, conditions)
            if buy_flow_res > 3:
                buy_flag = True
                print(f"{current_row['last_traded_time']} - buy")
                print(ltp_price_ce/ltp_price_pe)

            else:
                buy_flag=False
        else:
            buy_flag = False

        if not buy_flag:
            if (ltp_check or ltp_check_2) and count_YES > 3  and (for_sell or sell_2 or sell_3 ) and contract_signal_power_s and (((buy_sum < prev_buy_sum) and (sell_sum > prev_sell_sum)) or (buy_sum < 0 and sell_sum > 0)) \
                and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
                    (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))) :
                print(f"{current_row['last_traded_time']} - sell")
                print(ltp_price_ce/ltp_price_pe)

            elif (ltp_check or ltp_check_2) and count_YES == 3 and count_N >= 1  and (for_sell or sell_2 or sell_3 ) and contract_signal_power_s and (((buy_sum < prev_buy_sum) and (sell_sum > prev_sell_sum)) or (buy_sum < 0 and sell_sum > 0)) \
                and ((buy_sum * prev_buy_sum < 0) or (len(str(abs(prev_buy_sum))) < len(str(abs(buy_sum)))) or 
                    (sell_sum * prev_sell_sum < 0) or (len(str(abs(prev_sell_sum))) < len(str(abs(sell_sum))))) :
                sell_flow_res =  sell_flow(data, conditions2)
                if sell_flow_res > 3:
                    print(f"{current_row['last_traded_time']} - sell")
                    print(ltp_price_ce/ltp_price_pe)

        b_len_prev, s_len_prev = b_len_curr, s_len_curr
        p_change_in_buy, p_change_in_sell = change_in_buy, change_in_sell

else:
    print(f"Error: The file must contain the following columns: {', '.join(required_columns)}")
