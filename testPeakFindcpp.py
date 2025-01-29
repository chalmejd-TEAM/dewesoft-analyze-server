import findPeaks
import numpy as np
import matplotlib.pyplot as plt

# Example data
data = np.random.rand(1000000)  # Ensure data is non-empty
prominence = 0.5  # Example prominence threshold
max_peaks = 10  # Example value for the third argument

peak_indices, peak_values = findPeaks.find_peaks(data, prominence, max_peaks)

print("Peak Indices:", peak_indices)
print("Peak Values:", peak_values)


# Plot results
plt.plot(data)
plt.plot(peak_indices, peak_values, 'x')
plt.show()