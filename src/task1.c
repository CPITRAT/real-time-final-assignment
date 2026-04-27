#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 200000  // Adjust this value to make execution slower/faster

int main() {
    volatile double x = 1.001;
    volatile double result = 1.0;

    clock_t start = clock();

    for (long long i = 0; i < N; i++) {
        result *= x;
        if (result > 1e6) result = 1.0; // prevent overflow
    }

    clock_t end = clock();

    double time_us = (double)(end - start) * 1e6 / CLOCKS_PER_SEC;

    printf("%.3f\n", time_us); // execution time in microseconds
    return 0;
}