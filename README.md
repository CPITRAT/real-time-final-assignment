# Real-Time Final Assignment

Final assignment for the **Real-Time Embedded Systems** course.

This project studies the scheduling of a periodic real-time task set using **non-preemptive Earliest Deadline First (EDF)** scheduling. It also includes a simple C workload used to estimate the execution time of Task 1 and a Python scheduler that builds the task jobs over one hyperperiod, simulates the schedules, and reports waiting times, response times, and deadline misses.

## Project overview

The repository contains:

* a C program used to measure the execution time of Task 1;
* a Python script that compiles and executes the C program several times;
* a WCET-style estimation based on the maximum measured execution time;
* a non-preemptive EDF scheduler;
* a second scheduling scenario where Task 5 is intentionally penalized;
* a PDF report documenting the analysis.

## Repository structure

```text
real-time-final-assignment/
├── README.md
├── report/
│   └── report\\\_real\\\_time\\\_final\\\_assignment.pdf
└── src/
    ├── scheduler.py
    └── task1.c
```

## Requirements

Make sure the following tools are installed:

* Python 3
* GCC
* Python packages:

  * `numpy`
  * `pandas`

Install the Python dependencies with:

```bash
pip install numpy pandas
```

On Linux/macOS, GCC is usually available through the system package manager. For example:

```bash
sudo apt install gcc
```

## How to run

Clone the repository:

```bash
git clone https://github.com/CPITRAT/real-time-final-assignment.git
cd real-time-final-assignment/src
```

Run the scheduler:

```bash
python3 scheduler.py
```

The script automatically compiles `task1.c` before running the scheduling simulation:

```bash
gcc task1.c -O2 -o task1.out
```

## What the program does

### 1\. Execution-time measurement

The C program `task1.c` performs a repeated floating-point computation and prints its execution time in microseconds.

The Python script runs this executable several times and computes:

* minimum execution time;
* first quartile;
* median;
* third quartile;
* maximum measured execution time;
* rounded execution time used as `C1`.

The maximum measured value is used as a conservative estimate for the execution time of Task 1.

### 2\. Task set

The scheduler uses the following task set:

|Task|Execution time|Period / deadline|
|-|-:|-:|
|T1|measured from `task1.c`|10 ms|
|T2|3 ms|10 ms|
|T3|2 ms|20 ms|
|T4|2 ms|20 ms|
|T5|2 ms|40 ms|
|T6|2 ms|40 ms|
|T7|3 ms|80 ms|

The hyperperiod is set to **80 ms**.

### 3\. Scheduling simulation

The Python script generates all jobs released during the hyperperiod and simulates two cases:

1. **Normal non-preemptive EDF**  
The ready job with the earliest absolute deadline is selected.
2. **EDF with Task 5 penalized**  
Task 5 receives an artificial deadline penalty in the selection rule, which delays its execution and allows the impact on waiting time, response time, and deadline misses to be observed.

## Output

The script prints two scheduling tables.

Each table includes:

* job name;
* execution interval;
* absolute deadline;
* waiting time;
* response time;
* deadline status (`OK` or `MISS`).

It also prints a summary with:

* total waiting time;
* number of deadline misses.

Example output format:

```text
====================================================
NORMAL NON-PREEMPTIVE EDF
====================================================
 job interval  deadline  waiting  response status
T1\\\_1   \\\[0, 1]        10        0         1     OK
...

Summary:
Total waiting time : ...
Deadline misses : ...
```

## Report

The full analysis is available in:

```text
report/report\\\_real\\\_time\\\_final\\\_assignment.pdf
```

## Notes

* Execution-time measurements depend on the machine, operating system, compiler, and current CPU load.
* The measured value is rounded up before being used in the scheduler.
* The scheduler is non-preemptive: once a job starts, it runs until completion.

## Author

CPITRAT



