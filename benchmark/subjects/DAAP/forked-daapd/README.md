Please carefully read the [main README.md](../../../README.md), which is stored in the benchmark's root folder, before following this subject-specific guideline.

# Note on multithreading in forked-daapd
A challenge in fuzzing a complete network server is the extensive use of threads and event-based I/O. When the same input is applied to the target software, its non-determinism causes variations of the coverage of program paths, which in turn hinders coverage-driven fuzzing. For this reason, the AFL fuzzer performs a ``calibration'' on every new input that expands the coverage, in order to assess whether the execution is deterministic, and to report the percentage of anomalous new inputs (the ``stability'' metrics).

By default, the forked-daapd project uses PThreads as threading library (kernel-level threads). As suggested by the AFL documentation, to improve the stability, we provide a second configuration that replaces PThreads with GNU Pth (user-level threads). To use GNU Pth, you can refer to ``Dockerfile-Pth'' instead of the default ``Dockerfile''.

User-level threads increase the complexity of the testing setup. There are known issues related to UNIX signal handling, which hinder the saving of coverage data.


# Fuzzing forked-daapd server with AFLNet and AFLnwe
Please follow the steps below to run and collect experimental results for forked-daapd.

## Step-1. Build a docker image
The following commands create a docker image tagged forked-daapd. The image should have everything available for fuzzing and code coverage calculation.

```bash
cd $PFBENCH
cd subjects/DAAP/forked-daapd
docker build . -t forked-daapd
```

## Step-2. Run fuzzing
The following commands run 4 instances of AFLNet and 4 instances of AFLnwe to simultaenously fuzz the target in 60 minutes.

```bash
cd $PFBENCH
mkdir results-forked-daapd

profuzzbench_exec_common.sh forked-daapd 4 results-forked-daapd aflnet out-forked-daapd-aflnet "-P HTTP -D 200000 -m none -t 3000 -q 3 -s 3 -E -K" 3600 5 &
profuzzbench_exec_common.sh forked-daapd 4 results-forked-daapd aflnwe out-forked-daapd-aflnwe "-D 200000 -m 1000 -t 3000 -K" 3600 5
```

## Step-3. Collect the results
The following commands collect the  code coverage results produced by AFLNet and AFLnwe and save them to results.csv.

```bash
cd $PFBENCH/results-forked-daapd

profuzzbench_generate_csv.sh forked-daapd 4 aflnet results.csv 0
profuzzbench_generate_csv.sh forked-daapd 4 aflnwe results.csv 1
```

## Step-4. Analyze the results
The results collected in step 3 (i.e., results.csv) can be used for plotting. Use the following command to plot the coverage over time and save it to a file.

```
cd $PFBENCH/results-forked-daapd

profuzzbench_plot.py -i results.csv -p forked-daapd -r 4 -c 60 -s 1 -o cov_over_time.png
```
