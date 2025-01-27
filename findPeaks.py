import numpy as np
from scipy.signal import find_peaks
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



