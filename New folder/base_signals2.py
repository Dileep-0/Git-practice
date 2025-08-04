import subprocess
import re
import pandas as pd


script4 = 'signals_criteria.py'
script5 = 'base_ohlc.py'

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



if base_signals:
    for timepoint in sorted(base_signals):
        #print(timepoint)
        #print(timepoint, matched_rows.loc[matched_rows['last_traded_time'] ==  timepoint, 'result'].values)
        print(timepoint)
else:
    print("No common timepoints found.")