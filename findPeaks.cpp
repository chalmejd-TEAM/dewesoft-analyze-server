#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>
#include <cmath>
#include <algorithm>
#include <omp.h>  // OpenMP for parallelization

namespace py = pybind11;

// Decimate function (reduces data size)
py::array_t<double> decimate(py::array_t<double> data, int factor) {
    auto buf = data.request();
    double *ptr = static_cast<double *>(buf.ptr);
    int size = static_cast<int>(buf.size);  // Use signed int

    if (size < factor) {
        throw std::runtime_error("Decimation factor too large for input size.");
    }

    std::vector<double> result(size / factor);

    #pragma omp parallel for
    for (int i = 0; i < size / factor; i++) {
        result[i] = ptr[i * factor];
    }

    return py::array_t<double>(result.size(), result.data());  // Directly return array_t
}

// Savitzky-Golay filter (Moving Average for noise reduction)
py::array_t<double> savgol_filter(py::array_t<double> data, int window_length) {
    auto buf = data.request();
    double *ptr = static_cast<double *>(buf.ptr);
    int size = static_cast<int>(buf.size);  // Use signed int

    if (size < window_length) return data;  // Skip if too small

    std::vector<double> smoothed(size);
    int half_window = window_length / 2;

    // Handle edges
    for (int i = 0; i < half_window; i++) {
        smoothed[i] = ptr[i];
        smoothed[size - i - 1] = ptr[size - i - 1];
    }

    #pragma omp parallel for
    for (int i = half_window; i < size - half_window; i++) {
        double sum = 0.0;
        for (int j = -half_window; j <= half_window; j++) {
            sum += ptr[i + j];
        }
        smoothed[i] = sum / window_length;
    }

    return py::array_t<double>(smoothed.size(), smoothed.data());  // Directly return array_t
}

// Peak detection with local prominence check
py::tuple find_peaks(py::array_t<double> data, double prominence, int window) {
    auto buf = data.request();
    double *ptr = static_cast<double *>(buf.ptr);
    int size = static_cast<int>(buf.size);  // Use signed int

    if (size < 3) throw std::runtime_error("Data size too small for peak detection.");

    std::vector<int> peak_indices;
    std::vector<double> peak_values;

    #pragma omp parallel
    {
        std::vector<int> local_peak_indices;
        std::vector<double> local_peak_values;

        #pragma omp for nowait
        for (int i = window; i < size - window; i++) {
            double local_max = *std::max_element(ptr + i - window, ptr + i + window + 1);
            if (ptr[i] == local_max && ptr[i] > prominence) {
                local_peak_indices.push_back(i);
                local_peak_values.push_back(ptr[i]);
            }
        }

        #pragma omp critical
        {
            peak_indices.insert(peak_indices.end(), local_peak_indices.begin(), local_peak_indices.end());
            peak_values.insert(peak_values.end(), local_peak_values.begin(), local_peak_values.end());
        }
    }

    // Return a tuple of arrays (no .copy() needed here)
    return py::make_tuple(py::array_t<int>(peak_indices.size(), peak_indices.data()), 
                          py::array_t<double>(peak_values.size(), peak_values.data()));
}

// Pybind11 module definition
PYBIND11_MODULE(findPeaks, m) {
    m.def("decimate", &decimate, "Decimate signal");
    m.def("savgol_filter", &savgol_filter, "Savitzky-Golay filter (Moving Average)");
    m.def("find_peaks", &find_peaks, "Find peaks with local prominence");
    m.doc() = "C++ accelerated peak finding module";
}
