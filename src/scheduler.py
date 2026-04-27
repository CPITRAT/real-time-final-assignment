import subprocess
import re
import math
from pathlib import Path
from math import gcd
from functools import reduce


# ============================================================
# TIME UNITS
# ============================================================
# task1.cpp → WCET en nanosecondes (ns)
# scheduler → unités abstraites
#
# Conversion :
# C1 = ceil(WCET_ns / SCHEDULER_UNIT_NS)
# ============================================================

SCHEDULER_UNIT_NS = 100.0


# ============================================================
# RUN TASK1 AND EXTRACT WCET
# ============================================================

def get_c1_from_task1():
    current_file = Path(__file__).resolve()
    src_dir = current_file.parent
    project_root = src_dir.parent

    task1_cpp = src_dir / "task1.cpp"
    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)

    task1_exe = results_dir / "task1.exe"

    print("\n========== COMPILING TASK 1 ==========")

    subprocess.run(
        ["g++", str(task1_cpp), "-O2", "-o", str(task1_exe)],
        check=True
    )

    print("Compilation successful.")
    print("\n========== RUNNING TASK 1 ==========")

    result = subprocess.run(
        [str(task1_exe)],
        check=True,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    match = re.search(r"WCET:\s*([0-9.]+)\s*ns", result.stdout)

    if not match:
        raise ValueError("WCET not found in task1 output")

    wcet_ns = float(match.group(1))

    c1 = math.ceil(wcet_ns / SCHEDULER_UNIT_NS)
    c1 = max(1, c1)

    print("========== WCET TO C1 CONVERSION ==========")
    print(f"WCET: {wcet_ns:.2f} ns")
    print(f"1 scheduler unit = {SCHEDULER_UNIT_NS:.2f} ns")
    print(f"C1 = ceil(WCET / unit) = {c1}")
    print("===========================================")

    return c1, wcet_ns


C1, WCET_NS = get_c1_from_task1()


# ============================================================
# TASK SET
# ============================================================

tasks = [
    ("tau1", C1, 10),
    ("tau2", 3, 10),
    ("tau3", 2, 20),
    ("tau4", 2, 20),
    ("tau5", 2, 40),
    ("tau6", 2, 40),
    ("tau7", 3, 80),
]


# ============================================================
# UTILS
# ============================================================

def lcm(a, b):
    return a * b // gcd(a, b)


def lcm_list(numbers):
    return reduce(lcm, numbers)


# ============================================================
# HYPERPERIOD + UTILIZATION
# ============================================================

periods = [T for _, _, T in tasks]
H = lcm_list(periods)

utilization = sum(C / T for _, C, T in tasks)

print("\n========== TASK SET ==========")
print(f"Scheduler unit = {SCHEDULER_UNIT_NS:.2f} ns\n")

for name, C, T in tasks:
    print(f"{name} : C={C}, T={T}")

print("\n========== GLOBAL ==========")
print(f"Hyperperiod: {H} units ({H * SCHEDULER_UNIT_NS:.2f} ns)")
print(f"Utilization: {utilization:.4f}")
print("Schedulable (U<=1):", "YES" if utilization <= 1 else "NO")


# ============================================================
# JOB GENERATION
# ============================================================

def generate_jobs():
    jobs = []

    for name, C, T in tasks:
        for k in range(H // T):
            release = k * T
            deadline = release + T

            jobs.append({
                "id": f"{name}_{k}",
                "task": name,
                "C": C,
                "release": release,
                "deadline": deadline
            })

    return jobs


# ============================================================
# EDF NON-PREEMPTIVE
# ============================================================

def schedule_jobs(jobs, allow_tau5_miss=False):
    time = 0
    schedule = []
    done = []
    idle_time = 0

    jobs = sorted(jobs, key=lambda j: j["release"])
    remaining = jobs.copy()

    while time < H and remaining:
        ready = [j for j in remaining if j["release"] <= time]

        if not ready:
            next_release = min(j["release"] for j in remaining)

            schedule.append(("IDLE", time, next_release))
            idle_time += next_release - time

            time = next_release
            continue

        ready.sort(key=lambda j: j["deadline"])
        job = ready[0]

        start = time
        finish = start + job["C"]

        waiting = start - job["release"]
        response = finish - job["release"]

        if finish <= job["deadline"]:
            status = "OK"
        elif allow_tau5_miss and job["task"] == "tau5":
            status = "MISS_ALLOWED"
        else:
            status = "MISS"

        schedule.append((job["id"], start, finish, job["deadline"], status))

        done.append({
            "id": job["id"],
            "release": job["release"],
            "start": start,
            "finish": finish,
            "deadline": job["deadline"],
            "waiting": waiting,
            "response": response,
            "status": status
        })

        time = finish
        remaining.remove(job)

    total_wait = sum(j["waiting"] for j in done)
    misses = sum(1 for j in done if j["status"] == "MISS")
    allowed = sum(1 for j in done if j["status"] == "MISS_ALLOWED")

    return schedule, done, total_wait, idle_time, misses, allowed


# ============================================================
# PRINTS
# ============================================================

def print_schedule(schedule):
    print("\n========== TIMELINE ==========")
    for item in schedule:
        if item[0] == "IDLE":
            print(f"IDLE  {item[1]} -> {item[2]}")
        else:
            print(f"{item[0]} : {item[1]} -> {item[2]} | D={item[3]} | {item[4]}")


def print_analysis(done):
    print("\n========== RESPONSE TIMES ==========")

    for j in done:
        print(
            f"{j['id']} | r={j['release']} "
            f"s={j['start']} f={j['finish']} "
            f"D={j['deadline']} "
            f"W={j['waiting']} R={j['response']} | {j['status']}"
        )


def print_summary(wait, idle, misses, allowed):
    print("\n========== SUMMARY ==========")

    print(f"Total waiting: {wait} units ({wait * SCHEDULER_UNIT_NS:.2f} ns)")
    print(f"Total idle: {idle} units ({idle * SCHEDULER_UNIT_NS:.2f} ns)")
    print(f"Deadline misses: {misses}")
    print(f"Allowed tau5 misses: {allowed}")


# ============================================================
# RUN NORMAL
# ============================================================

print("\n" + "="*60)
print("NORMAL EDF NON-PREEMPTIVE")
print("="*60)

jobs = generate_jobs()
sched, done, wait, idle, miss, allow = schedule_jobs(jobs)

print_schedule(sched)
print_analysis(done)
print_summary(wait, idle, miss, allow)


# ============================================================
# RUN TAU5 ALLOWED
# ============================================================

print("\n" + "="*60)
print("EDF WITH TAU5 ALLOWED TO MISS")
print("="*60)

jobs = generate_jobs()
sched, done, wait, idle, miss, allow = schedule_jobs(jobs, True)

print_schedule(sched)
print_analysis(done)
print_summary(wait, idle, miss, allow)