import pandas as pd
import numpy as np
import os
import re
from collections import OrderedDict

# Sort the grouped dictionary chronologically based on the datekey


folder_path = r'C:\Users\dilee\Fyers_copy\New folder'
all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# === Group by date prefix ===
grouped = {}
pattern = r"(\d{2}-\d{2}-\d{4})_(NIFTY|BANKNIFTY).*?(FUT|CE|PE)"

for file in all_files:
    match = re.match(pattern, file)
    if match:
        date_key = match.group(1)
        grouped.setdefault(date_key, []).append(file)

sorted_grouped = OrderedDict(
    sorted(grouped.items(), key=lambda x: pd.to_datetime(x[0], dayfirst=True))
)

print(sorted_grouped)


# === Set the interval ===
interval = '5min'

def aggregate_file(df, file_id):
    aggregated_data = []
    df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], errors='coerce')

    for name, group in df.groupby(pd.Grouper(key='last_traded_time', freq=interval)):
        #print(name)
        if group.empty:
            continue

        selected_column = 'last_traded_time'
        differ = group.columns.difference([selected_column])
        numeric_columns = group[differ].select_dtypes(include=[np.number]).columns
        group_diff = group[numeric_columns].diff()
        group_sum = group.drop(columns=[selected_column]).sum()
        total_diff_size = (group['bid_size'] - group['ask_size']).sum()
        total_diff_price = (group['bid_price'] - group['ask_price']).sum()

        # === Common aggregations ===
        ltp = group_diff['ltp'].sum()
        bid_price = group_diff['bid_price'].sum()
        ask_price = group_diff['ask_price'].sum()
        bid_ask_pr_diff = abs(bid_price - ask_price)
        volume = group_diff['vol_traded_today'].sum()
        bid = group_sum['bid_size']
        ask = group_sum['ask_size']
        bid_pr = group_sum['bid_price']
        ask_pr = group_sum['ask_price']
        bid_ask_diff = bid - ask
        last_trade = group_diff['last_traded_qty'].sum()
        buy_qty = group_diff['tot_buy_qty'].sum()
        sell_qty = group_diff['tot_sell_qty'].sum()
        avg_trade = group_diff['avg_trade_price'].sum()
        ch = group_diff['ch'].sum()
        chp = group_diff['chp'].sum()
        h_bid = group['bid_price'].max()
        l_bid = group['bid_price'].min()
        h_ask = group['ask_price'].max()
        l_ask = group['ask_price'].min()
        
        high = group['ltp'].max()
        low = group['ltp'].min()
        if 'ltp' in group and not group['ltp'].empty:
            close = group['ltp'].iloc[-1]
        else:
            close = 0 
        if 'ltp' in group and not group['ltp'].empty:
            open = group['ltp'].iloc[0]
        else:
            open = 0 


        # === Signals ===
        tot_buy_sig = 'N'
        tot_sell_sig = 'N'
        if aggregated_data:
            previous = aggregated_data[-1]
            prev_buy = previous[f'tot_buy_qty_{file_id}']
            prev_sell = previous[f'tot_sell_qty_{file_id}']
            #prev_trade = previous[f'last_traded_qty_{file_id}']

            # File-specific condition logic
            if file_id == 1:
                if (buy_qty - prev_buy) > 20000 and buy_qty > prev_buy:
                    tot_buy_sig = 'Y'
                elif buy_qty < 3000 and prev_buy > buy_qty:
                    tot_buy_sig = 'YES'
                if sell_qty < 3000 and prev_sell > sell_qty:
                    tot_sell_sig = 'Y'
                elif (sell_qty - prev_sell) > 20000 and sell_qty > prev_sell:
                    tot_sell_sig = 'YES'

            elif file_id == 2:
                if (buy_qty - prev_buy) > 20000 and buy_qty > prev_buy:
                    tot_buy_sig = 'Y'
                elif buy_qty < 3000 and prev_buy > buy_qty:
                    tot_buy_sig = 'YES'
                if sell_qty < 3000 and prev_sell > sell_qty:
                    tot_sell_sig = 'Y'
                elif (sell_qty - prev_sell) > 20000 and sell_qty > prev_sell:
                    tot_sell_sig = 'YES'

            elif file_id == 3:
                if buy_qty < 3000 and prev_buy > buy_qty:
                    tot_buy_sig = 'Y'
                elif (buy_qty - prev_buy) > 20000 and prev_buy < buy_qty:
                    tot_buy_sig = 'YES'
                if (sell_qty - prev_sell) > 20000 and sell_qty > prev_sell:
                    tot_sell_sig = 'Y'
                elif sell_qty < 3000 and sell_qty < prev_sell:
                    tot_sell_sig = 'YES'

        row = {
            'last_traded_time': name,
            #f'group_size_{file_id}': len(group),
            f'ltp_{file_id}': ltp,
            f'bid_price_{file_id}': bid_price,
            f'ask_price_{file_id}': ask_price,
            f'bid_ask_pr_diff_{file_id}': bid_ask_pr_diff,
            #f'price_diff{file_id}': total_diff_price,
            f'bid_size{file_id}': bid,
            f'ask_size{file_id}': ask,
            #f'size_diff{file_id}': total_diff_size,
            #f'h_bid_{file_id}': h_bid,
            #f'l_bid_{file_id}': l_bid,
            #f'h_ask_{file_id}': h_ask,
            #f'l_ask_{file_id}': l_ask,
            f'volume_{file_id}': volume,
            #f'last_traded_qty_{file_id}': last_trade,
            f'tot_buy_qty_{file_id}': buy_qty,
            f'tot_buy_sig_{file_id}': tot_buy_sig,
            f'tot_sell_qty_{file_id}': sell_qty,
            f'tot_sell_sig_{file_id}': tot_sell_sig,
            #f'avg_trade_price_{file_id}': avg_trade,
            #f'ch_{file_id}': ch,
            #f'chp_{file_id}': chp,

            f'high_{file_id}': high,
            f'low_{file_id}': low,
            f'open_{file_id}': open,
            f'close_{file_id}': close
        }
        aggregated_data.append(row)

    return pd.DataFrame(aggregated_data)

all_dfs = []

for datekey, files in sorted_grouped.items():
    fut = next((f for f in files if f.endswith("FUT.csv") and "BANKNIFTY" not in f), None)
    CE = next((f for f in files if f.endswith("CE.csv")), None)
    PE = next((f for f in files if f.endswith("PE.csv")), None)
    bank = next((f for f in files if f.endswith("FUT.csv") and "BANKNIFTY" in f), None)

    if not (fut and CE and PE and bank):
        print(f"skipping {datekey}, missing one of fut/ce/pe")
        continue
    df1 = pd.read_csv(os.path.join(folder_path, fut))
    df2 = pd.read_csv(os.path.join(folder_path, CE))
    df3 = pd.read_csv(os.path.join(folder_path, PE))
    df4 = pd.read_csv(os.path.join(folder_path, bank))

    # === Aggregate each file with its logic ===
    agg1 = aggregate_file(df1, file_id=1)
    agg2 = aggregate_file(df2, file_id=2)
    agg3 = aggregate_file(df3, file_id=3)
    agg4 = aggregate_file(df4, file_id=4)


    # === Merge on common 5-min intervals ===
    common_times = set(agg1['last_traded_time']) & set(agg2['last_traded_time']) & set(agg3['last_traded_time']) & set(agg4['last_traded_time'])

    agg1 = agg1[agg1['last_traded_time'].isin(common_times)]
    agg2 = agg2[agg2['last_traded_time'].isin(common_times)]
    agg3 = agg3[agg3['last_traded_time'].isin(common_times)]
    agg4 = agg4[agg4['last_traded_time'].isin(common_times)]

# Merge on time
    final_df = agg1.merge(agg2, on='last_traded_time').merge(agg3, on='last_traded_time').merge(agg4, on='last_traded_time')
    formatted_date = pd.to_datetime(datekey, dayfirst=True).strftime('%Y-%m-%d')
    #final_df.insert(1, 'date', formatted_date)

    signals = []
    for i, row in final_df.iterrows():
        ignore_2_values = list(row.values)[:-10]
        y_count = sum(1 for v in ignore_2_values if v == 'Y')
        yes_count = sum(1 for v in ignore_2_values if v == 'YES')
        n_count = sum(1 for v in ignore_2_values if v == 'N')

        pattern = []
        prev = final_df.iloc[i-1]

        for file_id in [1,2,3]:
            buy_key = f'tot_buy_qty_{file_id}'
            sell_key = f'tot_sell_qty_{file_id}'
            if buy_key in row and sell_key in row:
                if file_id == 3:
                    pattern.append('dec' if prev[buy_key] > row[buy_key] else 'inc')
                    pattern.append('inc' if prev[sell_key] < row[sell_key] else 'dec')    
                else:
                    pattern.append('inc' if prev[buy_key] < row[buy_key] else 'dec')
                    pattern.append('dec' if prev[sell_key] > row[sell_key] else 'inc')

        buy_pattern = ['inc', 'dec', 'inc', 'dec', 'dec', 'inc']
        sell_pattern = ['dec', 'inc', 'dec', 'inc', 'inc', 'dec']

        final_signal = 'no signal'

        if y_count > 3:
            final_signal = "BUY"
        elif yes_count > 3:
            final_signal = "SELL"
        elif y_count == 3 and n_count >= 1 and i>0:
            if compare_sig(pattern, buy_pattern) >= 4:
                final_signal = 'BUY'
        elif yes_count == 3 and n_count >= 1 and i>0:
            if compare_sig(pattern, sell_pattern) >= 4:
                final_signal = 'SELL'

        signals.append(final_signal)

        def compare_sig(p1, p2):
            return sum(a == b for a,b in zip(p1,p2))
        
    final_df['final_signal'] = signals
    

    results = []
    for i in range(len(final_df)):
        row = final_df.iloc[i]
        signal = row['final_signal']
        ltp = row['ltp_1']

        '''if signal not in ['BUY', 'SELL']:
            results.append('neutral')
            continue'''
        

        if signal == 'BUY':
            lookahead = final_df.iloc[i+1:i+6]  # next 5 rows
            ltp_diff = row['high_2'] - row['low_2']
            target = ltp_diff*1 + row['high_2']
            loss = row['high_2'] - ltp_diff 
            trigger = row['high_2']+2

            touched_high = False
            result = 'not_triggered'
            execution_low = None
            trigger_hit_index = None
            for _, r in lookahead.iterrows():
                if not touched_high:

                    if r['high_2'] >= trigger:
                        touched_high = True  # Only mark after touching current high
                        execution_low = r['low_2']
                        trigger_hit_index = _ #index
                        
                        if r['low_2'] <= loss:
                            result = 'im_loss'
                            break
                    if not touched_high and r['close_2'] <= loss:
                        result = 'reverse'
                        break

                    continue

                if touched_high:
                    # Check if executed candle's low is breached
                    if r['low_2'] <= execution_low:
                        result = 'exc_loss'
                        break
                        
                    elif r['low_2'] <= loss:
                        result = 'loss'
                        break

                    elif r['high_2'] >= target:
                        result = 'win'
                        break
                    
            if touched_high and result == 'not_triggered':
                last_candle = lookahead.iloc[-1]
                if 'close_2' in last_candle:
                    if last_candle['close_2'] > trigger:
                        result = 'open_win'
                    elif last_candle['close_2'] < trigger:
                        result = 'open_loss'
                    else:
                        result = 'open_neut'
                else:
                    result = 'open'
        
        elif signal == 'SELL':
            lookahead = final_df.iloc[i+1:i+6]  # next 5 rows
            ltp_diff = row['high_3'] - row['low_3']
            target = ltp_diff*1 + row['high_3']
            loss = row['high_3'] - ltp_diff 
            trigger = row['high_3']+2

            touched_high1 = False
            result = 'not_triggered'
            execution_low = None
            trigger_hit_index = None
            for _, r in lookahead.iterrows():
                if not touched_high1:
                    
                    if r['high_3'] >= trigger:
                        touched_high1 = True 
                        execution_low = r['low_3']
                        trigger_hit_index = _ #index

                        if r['low_3'] <= loss:
                            result = 'im_loss'
                            break

                    if not touched_high1 and r['close_3'] <= loss:
                        result = 'reverse'
                        break
                    
                    continue

                if touched_high1:
                    # Check if executed candle's low is breached
                    if r['low_3'] <= execution_low:
                        result = 'exc_loss'
                        break

                    elif r['low_3'] <= loss:
                        result = 'loss'
                        break

                    elif r['high_3'] >= target:
                        result = 'win'
                        break
            if touched_high1 and result == 'not_triggered':
                last_candle = lookahead.iloc[-1]
                if 'close_3' in last_candle:
                    if last_candle['close_3'] > trigger:
                        result = 'open_win'
                    elif last_candle['close_3'] < trigger:
                        result = 'open_loss'
                    else:
                        result = 'open_neut'
                else:
                    result = 'open'
        
        elif signal == 'no signal':
            touched_high2 = False
            result = 'not_triggered'
            execution_low = None
            trigger_hit_index = None

            if ltp > 0:
                lookahead = final_df.iloc[i+1:i+6]  # next 5 rows
                ltp_diff = row['high_2'] - row['low_2']
                target = ltp_diff*1 + row['high_2']
                loss = row['high_2'] - ltp_diff 
                trigger = row['high_2']+2

                for _, r in lookahead.iterrows():
                    if not touched_high2:
                        
                        if r['high_2'] >= trigger:
                            touched_high2 = True
                            execution_low = r['low_2']
                            trigger_hit_index = _ #index

                            if r['low_2'] <= loss:
                                result = 'im_loss'
                                break
                        
                        if not touched_high2 and r['close_2'] <= loss:
                            result = 'reverse'
                            break
                        
                        continue
                    
                    if touched_high2:
                        if r['low_2'] <= execution_low:
                            result = 'exc_loss'
                            break
                            
                        elif r['low_2'] <= loss:
                            result = 'loss'
                            break

                        elif r['high_2'] >= target:
                            result = 'win'
                            break

                if touched_high2 and result == 'not_triggered':
                    last_candle = lookahead.iloc[-1]
                    if 'close_2' in last_candle:
                        if last_candle['close_2'] > trigger:
                            result = 'open_win'
                        elif last_candle['close_2'] < trigger:
                            result = 'open_loss'
                        else:
                            result = 'open_neut'
                    else:
                        result = 'open'
            elif ltp < 0:
                lookahead = final_df.iloc[i+1:i+6]  # next 5 rows
                ltp_diff = row['high_3'] - row['low_3']
                target = ltp_diff*1 + row['high_3']
                loss = row['high_3'] - ltp_diff 
                trigger = row['high_3']+2

                for _, r in lookahead.iterrows():
                    if not touched_high2:

                        if r['high_3'] >= trigger:
                            touched_high2 = True
                            execution_low = r['low_3']
                            trigger_hit_index = _ #index

                            if r['low_3'] <= loss:
                                result = 'im_loss'
                                break

                        if not touched_high2 and r['close_3'] <= loss:
                            result = 'reverse'
                            break
                        
                        continue
                    
                    if touched_high2:
                        # Check if executed candle's low is breached
                        if r['low_3'] <= execution_low:
                            result = 'exc_loss'
                            break

                        elif r['low_3'] <= loss:
                            result = 'loss'
                            break

                        elif r['high_3'] >= target:
                            result = 'win'
                            break
                if touched_high2 and result == 'not_triggered':
                    last_candle = lookahead.iloc[-1]
                    if 'close_3' in last_candle:
                        if last_candle['close_3'] > trigger:
                            result = 'open_win'
                        elif last_candle['close_3'] < trigger:
                            result = 'open_loss'
                        else:
                            result = 'open_neut'
                    else:
                        result = 'open'
            
            elif ltp == 0:
                result = 'neutral'
        
        results.append(result)

    final_df['result'] = results
    all_dfs.append(final_df)

    combined_df = pd.concat(all_dfs, ignore_index=True)

    combined_df.to_csv(os.path.join(folder_path, "all_aggregated_1x.csv"), index=False)

    # === Save result ===
print("Aggregation completed and saved as aggregated_master")
