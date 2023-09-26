Please carefully read the [main README.md](../../../README.md), which is stored in the benchmark's root folder, before following this subject-specific guideline.

# Fuzzing Kamailio server with AFLNet and AFLnwe
Please follow the steps below to run and collect experimental results for Kamailio, which is a SIP server.

## Step-1. Build a docker image
The following commands create a docker image tagged kamailio. The image should have everything available for fuzzing and code coverage calculation.

```bash
cd $PFBENCH
cd subjects/SIP/Kamailio
docker build . -t kamailio
```

## Step-2. Run fuzzing
The following commands run 4 instances of AFLNet and 4 instances of AFLnwe to simultaenously fuzz Kamailio in 60 minutes.

```bash
cd $PFBENCH
mkdir results-kamailio

profuzzbench_exec_common.sh kamailio 4 results-kamailio aflnet out-kamailio-aflnet "-m 200 -t 3000+ -P SIP -l 5061 -D 50000 -q 3 -s 3 -E -K" 3600 5 &
profuzzbench_exec_common.sh kamailio 4 results-kamailio aflnwe out-kamailio-aflnwe "-m 200 -t 3000+ -D 50000 -K" 3600 5
```

## Step-3. Collect the results
The following commands collect the  code coverage results produced by AFLNet and AFLnwe and save them to results.csv.

```bash
cd $PFBENCH/results-kamailio

profuzzbench_generate_csv.sh kamailio 4 aflnet results.csv 0
profuzzbench_generate_csv.sh kamailio 4 aflnwe results.csv 1
```

## Step-4. Analyze the results
The results collected in step 3 (i.e., results.csv) can be used for plotting. Use the following command to plot the coverage over time and save it to a file.

```
cd $PFBENCH/results-kamailio

profuzzbench_plot.py -i results.csv -p kamailio -r 4 -c 60 -s 1 -o cov_over_time.png
```
