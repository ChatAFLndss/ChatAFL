Please carefully read the [main README.md](../../../README.md), which is stored in the benchmark's root folder, before following this subject-specific guideline.

# Fuzzing Dnsmasq server with AFLNet and AFLnwe
Please follow the steps below to run and collect experimental results for Dnsmasq, which is a lightweight DNS server.

## Step-1. Build a docker image
The following commands create a docker image tagged Dnsmasq. The image should have everything available for fuzzing and code coverage calculation.

```bash
cd $PFBENCH
cd subjects/DNS/Dnsmasq
docker build . -t dnsmasq
```

## Step-2. Run fuzzing
The following commands run 4 instances of AFLNet and 4 instances of AFLnwe to simultaenously fuzz Dnsmasq in 60 minutes.

```bash
cd $PFBENCH
mkdir results-dnsmasq

profuzzbench_exec_common.sh dnsmasq 4 results-dnsmasq aflnet out-dnsmasq-aflnet "-P DNS -D 10000 -K" 3600 5 &
profuzzbench_exec_common.sh dnsmasq 4 results-dnsmasq aflnwe out-dnsmasq-aflnwe "-D 10000 -K" 3600 5
```

## Step-3. Collect the results
The following commands collect the  code coverage results produced by AFLNet and AFLnwe and save them to results.csv.

```bash
cd $PFBENCH/results-dnsmasq

profuzzbench_generate_csv.sh dnsmasq 4 aflnet results.csv 0
profuzzbench_generate_csv.sh dnsmasq 4 aflnwe results.csv 1
```

## Step-4. Analyze the results
The results collected in step 3 (i.e., results.csv) can be used for plotting. Use the following command to plot the coverage over time and save it to a file.

```
cd $PFBENCH/results-dnsmasq

profuzzbench_plot.py -i results.csv -p dnsmasq -r 4 -c 60 -s 1 -o cov_over_time.png
```
