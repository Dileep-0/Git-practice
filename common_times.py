import subprocess
import re

def run_script(script_name, file_name):
    """Runs a script after modifying the file_name variable inside it."""
    cmd = f"python {script_name} {file_name}"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()
    if error:
        print(f"Error in {script_name}: {error}")
    return output

def extract_timestamps(output):
    """Extract timestamps from script output."""
    return set(re.findall(r'\d{2}:\d{2}:\d{2}', output))

def main():
    file_names = input("Enter CSV filenames (comma-separated): ").split(',')
    file_names = [f.strip() for f in file_names]
    
    for file_name in file_names:
        print(f"\nProcessing {file_name}...\n")
        
        output1 = run_script("split_correlation.py", file_name)
        output2 = run_script("correlation_signals2.py", file_name)
        #run_script("symbols.py", file_name)  # This writes to a file
        
        timestamps1 = extract_timestamps(output1)
        timestamps2 = extract_timestamps(output2)
        
        # Read timestamps from script3 output file
        '''with open("20-03-2025_signals.txt", "r") as f:
            output3 = f.read()
        timestamps3 = extract_timestamps(output3)'''
        
        # Find common timestamps
        common_timestamps = timestamps1 & timestamps2
        
        print(f"Common timestamps for {file_name}: {sorted(common_timestamps)}")

if __name__ == "__main__":
    main()
