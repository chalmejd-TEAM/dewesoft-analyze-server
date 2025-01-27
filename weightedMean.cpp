#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <limits>
#include <future>
#include <omp.h>  // For parallelization in calculateExp

namespace py = pybind11;

// Optimized Moving Average Function
py::array_t<double> movingAverage(py::array_t<double> signal, int window) {
    auto buf = signal.request();
    auto ptr = static_cast<double *>(buf.ptr);
    size_t size = buf.shape[0];

    std::vector<double> result(size, 0.0);
    double running_sum = 0.0;
    int half_window = window / 2;

    for (size_t i = 0; i < size; ++i) {
        running_sum += ptr[i];
        if (i >= window) {
            running_sum -= ptr[i - window];
        }
        if (i >= half_window) {
            result[i] = running_sum / window;
        }
    }

    return py::array_t<double>(result.size(), result.data());
}

// Optimized Exponential Weighted Mean Calculation
std::tuple<double, double, int> calculateExp(
    double exp,
    const std::vector<double> &revCountAbs,
    const std::vector<double> &torqueSmoothed,
    int maxRev
) {
    double sumTorque = 0.0;
    double epsilon = 1e4 * std::numeric_limits<double>::epsilon();

    // Bucket indices by rounded values of revCountAbs
    std::vector<std::vector<size_t>> buckets(maxRev + 1);
    for (size_t k = 0; k < revCountAbs.size(); ++k) {
        int rounded_value = static_cast<int>(std::round(revCountAbs[k]));
        if (rounded_value <= maxRev) {
            buckets[rounded_value].push_back(k);
        }
    }

    #pragma omp parallel for reduction(+:sumTorque)
    for (int j = 1; j < maxRev; ++j) {
        double torqueSum = 0.0;
        int count = 0;

        for (size_t k : buckets[j]) {
            torqueSum += torqueSmoothed[k];
            ++count;
        }

        double torque = (count > 0) ? (torqueSum / count) : std::nan("");
        if (!std::isnan(torque)) {
            sumTorque += std::pow(torque, exp);
        }
    }

    double divTorque = sumTorque / maxRev;
    double eWM = std::pow(divTorque, 1.0 / exp);

    return {exp, eWM, maxRev};
}

// Optimized Main Calculation Function
py::list calculate(
    py::array_t<double> torqueSmoothedArr,
    py::array_t<double> revCountArr,
    std::vector<double> expList
) {
    auto torqueBuf = torqueSmoothedArr.request();
    auto revCountBuf = revCountArr.request();

    auto torqueSmoothed = static_cast<double *>(torqueBuf.ptr);
    auto revCount = static_cast<double *>(revCountBuf.ptr);
    size_t size = revCountBuf.shape[0];

    std::vector<double> torqueSmoothedVec(torqueSmoothed, torqueSmoothed + size);
    std::vector<double> revCountVec(revCount, revCount + size);

    double minRev = *std::min_element(revCountVec.begin(), revCountVec.end());
    for (double &val : revCountVec) {
        val -= minRev;
    }

    int maxRev = static_cast<int>(*std::max_element(revCountVec.begin(), revCountVec.end()));
    std::vector<double> revCountAbs(revCountVec.size());
    std::transform(revCountVec.begin(), revCountVec.end(), revCountAbs.begin(), [](double x) {
        return std::abs(x);
    });

    // Multithreaded computation
    std::vector<std::future<std::tuple<double, double, int>>> futures;
    for (double exp : expList) {
        futures.emplace_back(std::async(std::launch::async, calculateExp, exp, revCountAbs, torqueSmoothedVec, maxRev));
    }

    py::list results;
    for (auto &future : futures) {
        auto result = future.get();
        results.append(py::make_tuple(std::get<0>(result), std::get<1>(result), std::get<2>(result)));
    }

    return results;
}

// Pybind11 Module Definition
PYBIND11_MODULE(weightedMean, m) {
    m.def("movingAverage", &movingAverage, "Calculate moving average");
    m.def("calculate", &calculate, "Perform calculations",
          py::arg("torqueSmoothedArr"),
          py::arg("revCountArr"),
          py::arg("expList"));
}
