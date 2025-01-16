import dwdatareader as dw
import json
import sys

# Load target dewesoft file channel list
def main(file_path):
    try:
        with dw.open(file_path) as dataFile:
            channelList = [channel for channel in dataFile
                        if not 'CAN' in dataFile[channel].channel_index]
        return channelList

    except ValueError:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
        sys.exit(1)

    file_path = sys.argv[1]
    result = main(file_path)
    print(json.dumps(result))