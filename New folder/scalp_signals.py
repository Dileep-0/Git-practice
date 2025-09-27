import subprocess
import re
import pandas as pd

script3 = 'scatter.py'
script4 = 'signals_criteria.py'
script5 = 'scalping.py'

# Run all scripts simultaneously

p3 = subprocess.Popen(["python", script3], stdout=subprocess.PIPE, text=True)
p4 = subprocess.Popen(["python", script4], stdout=subprocess.PIPE, text=True)
p5 = subprocess.Popen(["python", script5], stdout=subprocess.PIPE, text=True)

# Read the output from all scripts
output3, _ = p3.communicate()
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



common_times = sorted(times4 & times5)


r2_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]\s+R²=([0-9.]+)\s+\|\s+R²=([0-9.]+)')

# Create a dictionary mapping timepoints to R² values
r2_dict = {}
for match in r2_pattern.finditer(output3):
    timepoint, r2_1, r2_2 = match.groups()
    # Convert to format matching script4/script5 timepoints if necessary (add seconds as :00)
    full_timepoint = timepoint + ":00"
    r2_dict[full_timepoint] = (r2_1, r2_2)

# Print only common timepoints with R² values
if common_times:
    for t in common_times:
        if t in r2_dict:
            r2_1, r2_2 = r2_dict[t]
            print(f"{t} | R²={r2_1} | R²={r2_2}")
else:
    print("No common timepoints found.")