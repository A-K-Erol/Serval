import re
import ast

def parse_satellite_data(filename):
    ids = []
    avg_compute_to_prioritize = []
    avg_capture_to_transmit = []
    avg_hi_pri_to_transmit = []
    avg_hi_pri = []
    avg_capture_to_compute = []

    with open(filename, 'r') as file:
        lines = file.readlines()

    # Regular expression to match IDs (lines with only numbers)
    id_pattern = re.compile(r"^\d+$")
    
    # Temporary storage for current data
    current_id = None
    current_data = {}

    for line in lines:
        line = line.strip()
        
        # Check if the line is an ID
        if id_pattern.match(line):
            # Process previous entry if it exists
            if current_id is not None:
                if current_data.get('avg hi pri to transmit', 0) > 0:
                    ids.append(current_id)
                    avg_compute_to_prioritize.append(current_data.get('avg compute to prioritize', 0))
                    avg_capture_to_transmit.append(current_data.get('avg capture to transmit', 0))
                    avg_hi_pri_to_transmit.append(current_data.get('avg hi pri to transmit', 0))
                    avg_hi_pri.append(current_data.get('num hi', 0))
                    avg_capture_to_compute.append(current_data.get('avg capture to compute', 0))

            # Start a new entry
            current_id = line
            current_data = {}
        
        # Otherwise, assume it's the dictionary line
        else:
            # Parse the dictionary safely
            try:
                current_data = ast.literal_eval(line)
            except (SyntaxError, ValueError) as e:
                print(f"Error parsing line: {line}")
                continue


    return ids, avg_hi_pri, avg_capture_to_compute, avg_compute_to_prioritize, avg_capture_to_transmit, avg_hi_pri_to_transmit

# Example usage:
filename = 'log_24.txt'
ids, avg_hi_pri, avg_capture_to_compute, avg_compute_to_prioritize, avg_capture_to_transmit, avg_hi_pri_to_transmit = parse_satellite_data(filename)

print("IDs with avg hi pri to transmit > 0:", ids)
print("Avg compute to prioritize:", avg_compute_to_prioritize)
print("Avg capture to transmit:", avg_capture_to_transmit)
print("Avg hi pri to transmit:", avg_hi_pri_to_transmit)
print("Avg capture to compute:", avg_capture_to_compute)
print("Avg hi pri:", avg_hi_pri)

# mean, median and quartiles
import numpy as np


# same analytics for other lists
print("Mean avg capture to transmit:", np.mean(avg_capture_to_transmit))
print("Median avg capture to transmit:", np.median(avg_capture_to_transmit))
print("25th percentile avg capture to transmit:", np.percentile(avg_capture_to_transmit, 25))
print("75th percentile avg capture to transmit:", np.percentile(avg_capture_to_transmit, 75))
print("90th percentile avg capture to transmit:", np.percentile(avg_capture_to_transmit, 90))

print("Mean avg hi pri to transmit:", np.mean(avg_hi_pri_to_transmit))
print("Median avg hi pri to transmit:", np.median(avg_hi_pri_to_transmit))
print("25th percentile avg hi pri to transmit:", np.percentile(avg_hi_pri_to_transmit, 25))
print("75th percentile avg hi pri to transmit:", np.percentile(avg_hi_pri_to_transmit, 75))
print("90th percentile avg hi pri to transmit:", np.percentile(avg_hi_pri_to_transmit, 90))

print("Mean avg capture to compute:", np.mean(avg_capture_to_compute))
print("Median avg capture to compute:", np.median(avg_capture_to_compute))
print("25th percentile avg capture to compute:", np.percentile(avg_capture_to_compute, 25))
print("75th percentile avg capture to compute:", np.percentile(avg_capture_to_compute, 75))
print("90th percentile avg capture to compute:", np.percentile(avg_capture_to_compute, 90))

# weight by avg hi priority, median and mean
# print("Weighted median avg compute to prioritize:", np.median(avg_compute_to_prioritize, weights=avg_hi_pri))
print("Weighted mean avg compute to prioritize:", np.average(avg_compute_to_prioritize, weights=avg_hi_pri))
# same for other lists
#print("Weighted median avg capture to transmit:", np.median(avg_capture_to_transmit, weights=avg_hi_pri))  
print("Weighted mean avg capture to transmit:", np.average(avg_capture_to_transmit, weights=avg_hi_pri))
# print("Weighted median avg hi pri to transmit:", np.median(avg_hi_pri_to_transmit, weights=avg_hi_pri))
print("Weighted mean avg hi pri to transmit:", np.average(avg_hi_pri_to_transmit, weights=avg_hi_pri))
# print("Weighted median avg capture to compute:", np.median(avg_capture_to_compute, weights=avg_hi_pri))
print("Weighted mean avg capture to compute:", np.average(avg_capture_to_compute, weights=avg_hi_pri))

