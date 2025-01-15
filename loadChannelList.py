import dwdatareader as dw
import json
import sys

# Load target dewesoft file channel list
def loadChannelList(file):
    try:
        with dw.open(file) as dataFile:
            channelList = [channel for channel in dataFile
                        if not 'CAN' in dataFile[channel].channel_index]
        return channelList

    except ValueError:
        pass

inputJson = json.loads(sys.stdin.read())

# Run loadChannelList function on target file
channelList = loadChannelList(inputJson)

# Convert channel list into JSON
# File name is channelList.json
with open("channelList.json", "w") as final:
	json.dump(channelList, final)
     
print(channelList)
