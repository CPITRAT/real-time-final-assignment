import subprocess
import time
import statistics

times = []

for _ in range(1000):
    start = time.perf_counter()
    subprocess.run(["task1.exe"], stdout=subprocess.DEVNULL)
    end = time.perf_counter()
    times.append(end - start)

times = sorted(times)

print("Min:", min(times))
print("Max:", max(times))
print("Q1:", times[int(len(times)*0.25)])
print("Q2 (Median):", statistics.median(times))
print("Q3:", times[int(len(times)*0.75)])

wcet = max(times) * 1.2
print("WCET:", wcet)