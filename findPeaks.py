# import numpy as np
# import pandas as pd
# import json
# import matplotlib.pyplot as plt
# import dwdatareader as dw
# from concurrent.futures import ProcessPoolExecutor
# import findPeaks  # Import the C++ module

# def find_peak_data(load, cycles, prominence=1, min_distance=50, window_length=51):
#     # Check if load is empty or too small for filtering
#     if len(load) < window_length:
#         return np.array([]), np.array([]), load, cycles

#     # Apply Savitzky-Golay filter
#     smoothed_load = findPeaks.savgol_filter(load, window_length, 3)
#     peak_indices, peak_values = findPeaks.find_peaks(smoothed_load, prominence)

#     # Extract peak cycles
#     peak_cycles = cycles[peak_indices]
#     return peak_cycles, peak_values, smoothed_load, cycles


# def loadFile(file):
#     try:
#         with dw.open(file) as dataFile:
#             channelList = [channel for channel in dataFile if 'CAN' not in dataFile[channel].channel_index]
#             df = dataFile.dataframe(channelList)
#         return df
#     except ValueError:
#         return None

# def process_data_chunk(chunk, prominence):
#     load = chunk['Combined Load'].to_numpy()
#     revs = chunk['CNT 1/Raw_Count'].to_numpy()

#     torque_smoothed = np.nan_to_num(abs(load), nan=0.0)
#     rev_count = np.nan_to_num(revs, nan=0.0)

#     # Check if the arrays have valid data
#     if len(torque_smoothed) == 0 or len(rev_count) == 0:
#         print("Warning: Empty data in chunk.")
#         return np.array([]), np.array([]), torque_smoothed, rev_count

#     # Use fast C++ decimation
#     torque_smoothed = findPeaks.decimate(torque_smoothed, 1000)
#     rev_count = findPeaks.decimate(rev_count, 1000)

#     # Check after decimation
#     if len(torque_smoothed) == 0 or len(rev_count) == 0:
#         print("Warning: Empty data after decimation.")
#         return np.array([]), np.array([]), torque_smoothed, rev_count

#     return find_peak_data(torque_smoothed, rev_count, prominence)



# def main(file_path, prominence=75, min_distance=50):
#     df = loadFile(file_path)

#     # Split data into chunks
#     chunk_size = 100000
#     chunks = np.array_split(df, len(df) // chunk_size)
    
#     results = []
#     with ProcessPoolExecutor() as executor:
#         futures = [executor.submit(process_data_chunk, chunk, prominence) for chunk in chunks]
#         for future in futures:
#             try:
#                 results.append(future.result())
#             except Exception as e:
#                 print(f"Error processing chunk: {e}")
    
#     # Flatten results
#     peak_cycles = np.concatenate([result[0] for result in results])
#     peak_values = np.concatenate([result[1] for result in results])
#     load = np.concatenate([result[2] for result in results])
#     cycles = np.concatenate([result[3] for result in results])

#     print(peak_cycles)
#     print(peak_values)

#     # Plot results
#     plt.plot(cycles, load)
#     plt.plot(peak_cycles, peak_values, "x")
#     plt.show()

# if __name__ == "__main__":
#     file_path = "C:/Users/jacobchalmers/OneDrive - TEAM Industries/Documents/TestRequests/TR_15372/Kodiak-Front-Duty-Cycle/15372_8K_Duty_Cycle_11_26_2024_SN_14212_BWD.dxd"
#     main(file_path)


import numpy as np
from scipy.signal import find_peaks, decimate
import dwdatareader as dw
import pandas
import weightedMean
import json
import sys


def find_peak_data(load, cycles, prominence=1, threshold=None):
    prominence = int(prominence)
    threshold = int(threshold)
    
    # Find peaks using scipy's find_peaks function
    peaks, _ = find_peaks(load, threshold=prominence, height=threshold)
    
    # Extract peak values
    peak_values = load[peaks]
    peak_cycles = cycles[peaks]
    
    return peak_cycles, peak_values, load, cycles


# Load the target file and perform calculations
def loadFile(file):
    try:
        with dw.open(file) as dataFile:
            channelList = [channel for channel in dataFile
                        if not 'CAN' in dataFile[channel].channel_index]
            df = dataFile.dataframe(channelList)
        return df
        
    except ValueError:
        pass

if __name__ == "__main__":
    # Get command-line arguments
    file_path = sys.argv[1]
    load_channel = sys.argv[2]
    rev_channel = sys.argv[3]
    threshold = sys.argv[4]
    prominence = sys.argv[5]

    # Load the file data
    df = loadFile(file_path)

    # Perform calculations
    load = df[load_channel].to_numpy()
    revs = df[rev_channel].to_numpy()

    torque_smoothed = abs(np.array(load))  
    rev_count = np.array(revs)   

    torque_smoothed = np.nan_to_num(torque_smoothed, nan=0.0)
    rev_count = np.nan_to_num(rev_count, nan=0.0)

    torque_smoothed = decimate(torque_smoothed, 1000)
    rev_count = decimate(rev_count, 1000)    

    results = find_peak_data(torque_smoothed, rev_count, prominence, threshold)

    # Convert results to a JSON serializable format (e.g., convert arrays to lists)
    results_json = {
        "peak_cycles": results[0].tolist(),  # Convert peak_cycles (ndarray) to list
        "peak_values": results[1].tolist(),  # Convert peak_values (ndarray) to list
        "load": results[2].tolist(),         # Convert load (ndarray) to list
        "cycles": results[3].tolist()        # Convert cycles (ndarray) to list
    }

    # Print the results as JSON for Flask to capture
    print(json.dumps(results_json))



