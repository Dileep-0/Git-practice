import subprocess
import re
import pandas as pd


script4 = 'signals_criteria.py'
script5 = 'previous_signals.py'

csv_file = 'Months_data_july.csv'

df = pd.read_csv(csv_file)

# Run all scripts simultaneously

p4 = subprocess.Popen(["python", script4], stdout=subprocess.PIPE, text=True)
p5 = subprocess.Popen(["python", script5], stdout=subprocess.PIPE, text=True)

# Read the output from all scripts

output4, _ = p4.communicate()
output5, _ = p5.communicate()

# Function to extract timepoints from script output
def extract_timepoints(output):
    # Use regex to find all datetime-like patterns (e.g., '2024-11-07 12:10:00')
    timepoints = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', output)
    return set(timepoints) # Split lines and convert to a set

# Extract timepoints from each script's output

times4 = extract_timepoints(output4)
times5 = extract_timepoints(output5)



base_signals = sorted(times4 & times5)
file_name = 'results_onex.csv'

base_signals_dt = pd.to_datetime(sorted(base_signals))
df['last_traded_time'] = pd.to_datetime(df['last_traded_time'], dayfirst=True)
print(base_signals_dt)

# Filter dataframe where time matches base signals
matched_rows = df[df['last_traded_time'].isin(base_signals_dt)][['last_traded_time','final_signal','result']]
print(matched_rows)

# Save to CSV and print
matched_rows.to_csv(file_name, index=False)

'''if base_signals:
    for timepoint in sorted(base_signals):
        #print(timepoint)
        #print(timepoint, matched_rows.loc[matched_rows['last_traded_time'] ==  timepoint, 'result'].values)
        print(timepoint)
else:
    print("No common timepoints found.")'''

if not matched_rows.empty:
    for _, row in matched_rows.iterrows():
        print(row['last_traded_time'], row['result'])
else:
    print("No common timepoints found.")