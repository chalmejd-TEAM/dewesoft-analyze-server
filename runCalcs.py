import dwdatareader as dw
import numpy as np
import pandas
import fast_calculations
import json
import sys

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
    exponents = json.loads(sys.argv[4])  # Parse exponents from JSON string

    # Load the file data
    df = loadFile(file_path)

    # Perform calculations
    load = df[load_channel].to_numpy()
    revs = df[rev_channel].to_numpy()

    torque_smoothed = abs(np.array(load))  
    rev_count = np.array(revs)       

    torque_smoothed = np.nan_to_num(torque_smoothed, nan=0.0)
    rev_count = np.nan_to_num(rev_count, nan=0.0)

    # Perform the EWM calculations with the exponents
    results = fast_calculations.calculate(torque_smoothed, rev_count, exponents)

    # Print the results as JSON for Flask to capture
    print(json.dumps(results))
