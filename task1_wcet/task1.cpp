#include <random>
#include <cstdint>

int main() {
    std::random_device rd;
    std::mt19937_64 gen(rd());

    std::uniform_int_distribution<unsigned long long> dist(
        1000000000ULL,
        9999999999ULL
    );

    volatile unsigned long long result = 0;

    unsigned long long a = dist(gen);
    unsigned long long b = dist(gen);

    result = a * b;

    return 0;
}