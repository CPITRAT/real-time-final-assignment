import subprocess
import numpy as np
import pandas as pd

N_SAMPLES = 200
HYPERPERIOD = 80

# ============================================================
# Measure execution time of task 1
# ============================================================

print("Compiling task1...")
subprocess.run(["gcc", "task1.c", "-O2", "-o", "task1.out"], check=True)

samples = [
    float(subprocess.run(
        ["./task1.out"], capture_output=True, text=True, check=True
    ).stdout.strip())
    for _ in range(N_SAMPLES)
]

samples_ms = np.array(samples) / 1000.0

C1_measured = np.max(samples_ms)
C1 = np.ceil(C1_measured)

print("\n=== TASK 1 EXECUTION TIME (ms) ===")
print(f"Min           : {samples_ms.min():.3f}")
print(f"Q1            : {np.percentile(samples_ms, 25):.3f}")
print(f"Median        : {np.percentile(samples_ms, 50):.3f}")
print(f"Q3            : {np.percentile(samples_ms, 75):.3f}")
print(f"Measured WCET : {C1_measured:.3f}")
print(f"Rounded C1    : {C1:.0f}")

# ============================================================
# Task set
# ============================================================

tasks = [
    (1, C1, 10),
    (2, 3, 10),
    (3, 2, 20),
    (4, 2, 20),
    (5, 2, 40),
    (6, 2, 40),
    (7, 3, 80),
]

# ============================================================
# Job generation
# ============================================================

jobs = []

for task, C, T in tasks:
    for k in range(HYPERPERIOD // T):
        jobs.append({
            "job": f"T{task}_{k + 1}",
            "task": task,
            "C": C,
            "release": k * T,
            "deadline": (k + 1) * T
        })

# ============================================================
# Scheduler
# ============================================================

def schedule(jobs, penalize_t5=False):
    remaining = [j.copy() for j in jobs]
    time = 0
    result = []

    while remaining:
        available = [j for j in remaining if j["release"] <= time]

        if not available:
            time = min(j["release"] for j in remaining)
            continue

        if penalize_t5:
            job = min(
                available,
                key=lambda j: j["deadline"] + (1000 if j["task"] == 5 else 0)
            )
        else:
            job = min(available, key=lambda j: j["deadline"])

        start = time
        finish = start + job["C"]

        result.append({
            "job": job["job"],
            "start": start,
            "finish": finish,
            "deadline": job["deadline"],
            "waiting": start - job["release"],
            "response": finish - job["release"],
            "miss": finish > job["deadline"]
        })

        time = finish
        remaining.remove(job)

    return pd.DataFrame(result)

# ============================================================
# Display
# ============================================================

def show(df, title):
    df["interval"] = df.apply(
        lambda r: f"[{r['start']:.0f}, {r['finish']:.0f}]",
        axis=1
    )
    df["status"] = df["miss"].map({False: "OK", True: "MISS"})

    print("\n====================================================")
    print(title)
    print("====================================================")

    print(
        df[[
            "job",
            "interval",
            "deadline",
            "waiting",
            "response",
            "status"
        ]].to_string(index=False)
    )

    print("\nSummary:")
    print(f"Total waiting time : {df['waiting'].sum():.0f}")
    print(f"Deadline misses    : {df['miss'].sum()}")

# ============================================================
# Run
# ============================================================

normal_schedule = schedule(jobs)
t5_penalized_schedule = schedule(jobs, penalize_t5=True)

show(normal_schedule, "NORMAL NON-PREEMPTIVE EDF")
show(t5_penalized_schedule, "EDF WITH T5 PENALIZED")