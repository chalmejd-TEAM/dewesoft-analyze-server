import fast_calculations
import json

print(fast_calculations.movingAverage([1, 2, 3, 4, 5], 3))

with open('testFile.json', 'r') as file:
    data = json.load(file)
    fileName = data["fileName"]
    exponents = data["exponents"]
    forward = data["forward"]

print(fileName)
print(exponents)
print(forward)
