from math import gcd
from functools import reduce

# ----------------------------
# TASK SET
# ----------------------------
tasks = [
    ("tau1", 3, 10),
    ("tau2", 3, 10),
    ("tau3", 2, 20),
    ("tau4", 2, 20),
    ("tau5", 2, 40),
    ("tau6", 2, 40),
    ("tau7", 3, 80),
]

# ----------------------------
# UTILS
# ----------------------------
def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_list(numbers):
    return reduce(lcm, numbers)

# ----------------------------
# HYPERPERIOD
# ----------------------------
periods = [t[2] for t in tasks]
H = lcm_list(periods)

utilization = sum(C / T for _, C, T in tasks)

print(f"\nHyperperiod: {H}")
print(f"Utilization: {utilization:.4f}")

# ----------------------------
# JOB GENERATION
# ----------------------------
def generate_jobs():
    jobs = []
    for name, C, T in tasks:
        for k in range(H // T):
            release = k * T
            deadline = release + T
            jobs.append({
                "task": name,
                "C": C,
                "release": release,
                "deadline": deadline,
                "remaining": C
            })
    return jobs

# ----------------------------
# SCHEDULER
# ----------------------------
def schedule_jobs(jobs, allow_tau5_miss=False):
    time = 0
    ready = []
    schedule = []

    jobs = sorted(jobs, key=lambda x: x["release"])

    total_waiting = 0
    total_idle = 0
    deadline_misses = 0

    while time < H:
        for job in jobs:
            if job["release"] == time:
                ready.append(job)

        ready = [j for j in ready if j["remaining"] > 0]

        if ready:
            ready.sort(key=lambda x: x["deadline"])
            job = ready[0]

            start = time
            finish = time + job["remaining"]

            waiting = start - job["release"]
            total_waiting += waiting

            if finish > job["deadline"]:
                if not (allow_tau5_miss and job["task"] == "tau5"):
                    deadline_misses += 1

            schedule.append((job["task"], start, finish, job["deadline"]))

            time = finish
            job["remaining"] = 0

        else:
            time += 1
            total_idle += 1

    return schedule, total_waiting, total_idle, deadline_misses

# ----------------------------
# PRINT SCHEDULE
# ----------------------------
def print_schedule(schedule):
    print("\nTimeline:\n")
    for task, start, end, deadline in schedule:
        status = "OK" if end <= deadline else "MISS"
        print(f"{task:5} | start={start:3} -> end={end:3} | deadline={deadline:3} | {status}")

# ----------------------------
# NORMAL
# ----------------------------
print("\n" + "="*60)
print("NORMAL NON-PREEMPTIVE SCHEDULE")
print("="*60)

jobs = generate_jobs()
schedule, wait, idle, misses = schedule_jobs(jobs)

print_schedule(schedule)

print("\nSummary:")
print(f"Total waiting time: {wait}")
print(f"Total idle time: {idle}")
print(f"Deadline misses: {misses}")

# ----------------------------
# TAU5 ALLOWED
# ----------------------------
print("\n" + "="*60)
print("SCHEDULE WITH TAU5 ALLOWED TO MISS")
print("="*60)

jobs = generate_jobs()
schedule_tau5, wait_tau5, idle_tau5, misses_tau5 = schedule_jobs(
    jobs, allow_tau5_miss=True
)

print_schedule(schedule_tau5)

print("\nSummary:")
print(f"Total waiting time: {wait_tau5}")
print(f"Total idle time: {idle_tau5}")
print(f"Deadline misses: {misses_tau5}")