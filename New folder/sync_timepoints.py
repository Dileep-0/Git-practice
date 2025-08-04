import subprocess
import re

# Define the script paths
script1 = "correlation_signals2.py"
script2 = "split_correlation.py"
script3 = "signals.py"
script4 = 'signals_criteria.py'
'''script4 = "bid_ask_pattern.py"
script5 = "bid_ask_pattern2.py"'''

# Run all scripts simultaneously
p1 = subprocess.Popen(["python", script1], stdout=subprocess.PIPE, text=True)
p2 = subprocess.Popen(["python", script2], stdout=subprocess.PIPE, text=True)
p3 = subprocess.Popen(["python", script3], stdout=subprocess.PIPE, text=True)
p4 = subprocess.Popen(["python", script4], stdout=subprocess.PIPE, text=True)
'''p5 = subprocess.Popen(["python", script5], stdout=subprocess.PIPE, text=True)'''

# Read the output from all scripts
output1, _ = p1.communicate()
output2, _ = p2.communicate()
output3, _ = p3.communicate()
output4, _ = p4.communicate()
'''output5, _ = p5.communicate()'''

# Function to extract timepoints from script output
def extract_timepoints(output):
    # Use regex to find all datetime-like patterns (e.g., '2024-11-07 12:10:00')
    timepoints = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', output)
    return set(timepoints) # Split lines and convert to a set

# Extract timepoints from each script's output
times1 = extract_timepoints(output1)
times2 = extract_timepoints(output2)
times3 = extract_timepoints(output3)
times4 = extract_timepoints(output4)
'''times5 = extract_timepoints(output5)'''

'''print("full correlation", sorted(times1))
print("half correlation", sorted(times2))
print("signals", sorted(times3))'''
'''print("bid_ask_4", sorted(times4))
print("bid_ask_6", sorted(times5))'''


# Find common timepoints
#common_timepoints_fhcorr = times1 & times2 & times3 & times4# Set intersection
#common_timepoints_1corr = times3 & times4
common_timepoints_1corr = (times1 | times2) & times3 & times4

# Print common timepoints
'''if common_timepoints_fhcorr:
    for timepoint in sorted(common_timepoints_fhcorr):
        print("both correlations",timepoint)
else:
    print("No common timepoints found.")'''

if common_timepoints_1corr:
    for timepoint in sorted(common_timepoints_1corr):
        print("single correlation", timepoint)
else:
    print("No common timepoints found.")