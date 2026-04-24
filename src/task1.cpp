#include <iostream>
#include <chrono>
#include <random>
#include <vector>
#include <algorithm>

int main() {
    using namespace std::chrono;

    const int RUNS = 1000;
    const int ITERATIONS = 1000000;

    std::vector<double> times;

    std::mt19937_64 gen(0);
    std::uniform_int_distribution<unsigned long long> dist(
        1000000000ULL,
        9999999999ULL
    );

    for (int r = 0; r < RUNS; r++) {
        volatile unsigned long long result = 0;

        auto start = high_resolution_clock::now();

        for (int i = 0; i < ITERATIONS; i++) {
            unsigned long long a = dist(gen);
            unsigned long long b = dist(gen);
            result = a * b;
        }

        auto end = high_resolution_clock::now();

        double duration_ns =
            duration_cast<nanoseconds>(end - start).count();

        double time_per_iteration_ns = duration_ns / ITERATIONS;
        times.push_back(time_per_iteration_ns);
    }

    std::sort(times.begin(), times.end());

    double min_time = times.front();
    double max_time = times.back();
    double q1 = times[RUNS * 25 / 100];
    double q2 = times[RUNS * 50 / 100];
    double q3 = times[RUNS * 75 / 100];

    double wcet = max_time * 1.2;

    std::cout << "Task tau1 WCET analysis" << std::endl;
    std::cout << "All values are in nanoseconds per multiplication" << std::endl;
    std::cout << "Min: " << min_time << " ns" << std::endl;
    std::cout << "Max: " << max_time << " ns" << std::endl;
    std::cout << "Q1: " << q1 << " ns" << std::endl;
    std::cout << "Q2 Median: " << q2 << " ns" << std::endl;
    std::cout << "Q3: " << q3 << " ns" << std::endl;
    std::cout << "WCET: " << wcet << " ns" << std::endl;

    return 0;
}