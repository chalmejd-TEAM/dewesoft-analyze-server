import dwdatareader as dw
import numpy as np
import pandas
import fast_calculations
import json
import sys

# Load target dewesoft file and all data
def loadFile(file):
    try:
        with dw.open(file) as dataFile:
            channelList = [channel for channel in dataFile
                        if not 'CAN' in dataFile[channel].channel_index]
            df = dataFile.dataframe(channelList)
        return df

    except ValueError:
        pass

inputJson = sys.argv[1]

# Open testFile.json and load into variables
with open(inputJson, 'r') as file:
    data = json.load(file)
    fileName = data["fileName"]
    exponents = data["exponents"]
    loadChannel = data["loadChannel"]
    revChannel = data["revChannel"]

# Run loadFile function on target file
df = loadFile(fileName)

# Convert load and rev channels to numpy arrays
load = df[loadChannel].to_numpy()
revs = df[revChannel].to_numpy()

# Convert negative torque to positive torque and remove NaN values from arrays
torque_smoothed = abs(np.array(load))  
rev_count = np.array(revs)       

torque_smoothed = np.nan_to_num(torque_smoothed, nan=0.0)  # Replace NaN with 0
rev_count = np.nan_to_num(rev_count, nan=0.0)             # Replace NaN with 0

# Run EWM calculations on arrays using exponents
results = fast_calculations.calculate(torque_smoothed, rev_count, exponents)

# Convert "results" into JSON
# File name is results.json
with open("results.json", "w") as final:
	json.dump(results, final)
     
print(results)
