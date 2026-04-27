#include <iostream>
#include <vector>
#include <chrono>
#include <algorithm>
#include <random>
#include <cstdint>

using namespace std;
using namespace std::chrono;

volatile uint64_t sink = 0;

uint64_t task1_work()
{
    random_device rd;
    mt19937_64 gen(rd());
    uniform_int_distribution<uint64_t> dist(100000, 999999);

    uint64_t a = dist(gen);
    uint64_t b = dist(gen);

    uint64_t result = a * b;
    sink = result;

    return result;
}

int main()
{
    const int N = 10000;
    vector<double> times_ns;

    times_ns.reserve(N);

    for (int i = 0; i < N; i++)
    {
        auto start = high_resolution_clock::now();

        task1_work();

        auto end = high_resolution_clock::now();

        double duration_ns =
            duration_cast<nanoseconds>(end - start).count();

        times_ns.push_back(duration_ns);
    }

    sort(times_ns.begin(), times_ns.end());

    double min_time = times_ns.front();
    double max_time = times_ns.back();
    double q1 = times_ns[N / 4];
    double q2 = times_ns[N / 2];
    double q3 = times_ns[(3 * N) / 4];
    double wcet = max_time;

    cout << "========== TASK 1 EXECUTION TIME MEASUREMENTS ==========" << endl;
    cout << "Number of executions: " << N << endl;
    cout << "Time unit: nanoseconds (ns)" << endl;
    cout << "Min:  " << min_time << " ns" << endl;
    cout << "Q1:   " << q1 << " ns" << endl;
    cout << "Q2:   " << q2 << " ns" << endl;
    cout << "Q3:   " << q3 << " ns" << endl;
    cout << "Max:  " << max_time << " ns" << endl;
    cout << "WCET: " << wcet << " ns" << endl;
    cout << "========================================================" << endl;

    return 0;
}