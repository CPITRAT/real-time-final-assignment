import csv
from math import lcm
from pathlib import Path

# -----------------------------
# Assumptions
# -----------------------------
# C1 is normalized for scheduling analysis.
# Raw measured values include process creation overhead.
C1 = 3

TASKS = [
    {"name": "tau1", "C": C1, "T": 10},
    {"name": "tau2", "C": 3,  "T": 10},
    {"name": "tau3", "C": 2,  "T": 20},
    {"name": "tau4", "C": 2,  "T": 20},
    {"name": "tau5", "C": 2,  "T": 40},
    {"name": "tau6", "C": 2,  "T": 40},
    {"name": "tau7", "C": 3,  "T": 80},
]


def compute_hyperperiod(tasks):
    return lcm(*[task["T"] for task in tasks])


def generate_jobs(tasks, hyperperiod):
    jobs = []

    for task in tasks:
        number_of_jobs = hyperperiod // task["T"]

        for j in range(number_of_jobs):
            release = j * task["T"]
            deadline = release + task["T"]

            jobs.append({
                "task": task["name"],
                "job": f"{task['name']}_{j + 1}",
                "C": task["C"],
                "T": task["T"],
                "release": release,
                "deadline": deadline,
            })

    return jobs


def schedule_jobs(jobs, hyperperiod, allow_tau5_miss=False):
    time = 0
    remaining_jobs = jobs.copy()
    schedule = []
    idle_time = 0

    while remaining_jobs:
        ready_jobs = [job for job in remaining_jobs if job["release"] <= time]

        if not ready_jobs:
            next_release = min(job["release"] for job in remaining_jobs)
            idle_time += next_release - time
            time = next_release
            continue

        if allow_tau5_miss:
            # In this mode, tau5 is given lowest priority.
            # This can allow tau5 to miss its deadline while preserving other tasks.
            non_tau5_ready = [job for job in ready_jobs if job["task"] != "tau5"]

            if non_tau5_ready:
                ready_jobs = non_tau5_ready

            selected_job = min(
                ready_jobs,
                key=lambda job: (job["deadline"], job["release"], job["task"])
            )

        else:
            # Normal case: non-preemptive EDF
            selected_job = min(
                ready_jobs,
                key=lambda job: (job["deadline"], job["release"], job["task"])
            )

        start = time
        finish = start + selected_job["C"]
        waiting = start - selected_job["release"]
        response = finish - selected_job["release"]
        deadline_missed = finish > selected_job["deadline"]

        schedule.append({
            "task": selected_job["task"],
            "job": selected_job["job"],
            "release": selected_job["release"],
            "C": selected_job["C"],
            "deadline": selected_job["deadline"],
            "start": start,
            "finish": finish,
            "waiting_time": waiting,
            "response_time": response,
            "deadline_missed": deadline_missed,
        })

        time = finish
        remaining_jobs.remove(selected_job)

    if time < hyperperiod:
        idle_time += hyperperiod - time

    return schedule, idle_time


def write_csv(schedule, idle_time, filename):
    results_dir = Path(__file__).resolve().parents[2] / "results"
    results_dir.mkdir(exist_ok=True)

    output_file = results_dir / filename

    with open(output_file, "w", newline="") as file:
        fieldnames = [
            "task",
            "job",
            "release",
            "C",
            "deadline",
            "start",
            "finish",
            "waiting_time",
            "response_time",
            "deadline_missed",
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in schedule:
            writer.writerow(row)

        writer.writerow({})
        writer.writerow({"task": "TOTAL_IDLE_TIME", "waiting_time": idle_time})
        writer.writerow({
            "task": "TOTAL_WAITING_TIME",
            "waiting_time": sum(job["waiting_time"] for job in schedule)
        })


def print_summary(schedule, idle_time, title):
    total_waiting = sum(job["waiting_time"] for job in schedule)
    missed_jobs = [job for job in schedule if job["deadline_missed"]]

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    print(f"Total waiting time: {total_waiting}")
    print(f"Total idle time: {idle_time}")
    print(f"Deadline misses: {len(missed_jobs)}")

    if missed_jobs:
        print("\nMissed jobs:")
        for job in missed_jobs:
            print(
                f"{job['job']} | finish={job['finish']} | deadline={job['deadline']}"
            )
    else:
        print("No deadlines missed.")


def main():
    hyperperiod = compute_hyperperiod(TASKS)
    jobs = generate_jobs(TASKS, hyperperiod)

    utilization = sum(task["C"] / task["T"] for task in TASKS)

    print(f"Hyperperiod: {hyperperiod}")
    print(f"Utilization: {utilization:.4f}")

    normal_schedule, normal_idle = schedule_jobs(
        jobs,
        hyperperiod,
        allow_tau5_miss=False
    )

    print_summary(
        normal_schedule,
        normal_idle,
        "NORMAL NON-PREEMPTIVE SCHEDULE"
    )

    write_csv(
        normal_schedule,
        normal_idle,
        "schedule_normal.csv"
    )

    tau5_schedule, tau5_idle = schedule_jobs(
        jobs,
        hyperperiod,
        allow_tau5_miss=True
    )

    print_summary(
        tau5_schedule,
        tau5_idle,
        "SCHEDULE WITH TAU5 ALLOWED TO MISS"
    )

    write_csv(
        tau5_schedule,
        tau5_idle,
        "schedule_tau5_allowed.csv"
    )


if __name__ == "__main__":
    main()