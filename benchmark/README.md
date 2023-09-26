# ProFuzzBench - A Benchmark for Stateful Protocol Fuzzing
ProFuzzBench is a benchmark for stateful fuzzing of network protocols. It includes a suite of representative open-source network servers for popular protocols (e.g., TLS, SSH, SMTP, FTP, SIP), and tools to automate experimentation.

# Citing ProFuzzBench

ProFuzzBench has been accepted for publication as a [Tool Demonstrations paper](https://dl.acm.org/doi/pdf/10.1145/3460319.3469077) at the 30th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA) 2021.

```
@inproceedings{profuzzbench,
  title={ProFuzzBench: A Benchmark for Stateful Protocol Fuzzing},
  author={Roberto Natella and Van-Thuan Pham},
  booktitle={Proceedings of the 30th ACM SIGSOFT International Symposium on Software Testing and Analysis},
  year={2021}
}
```

# Folder structure
```
protocol-fuzzing-benchmark
├── subjects: this folder contains all protocols included in this benchmark and
│   │         each protocol may have more than one target server
│   └── RTSP
│   └── FTP
│   │   └── LightFTP
│   │       └── Dockerfile: subject-specific Dockerfile
│   │       └── run.sh: (subject-specific) main script to run experiment inside a container
│   │       └── cov_script.sh: (subject-specific) script to do code coverage analysis
│   │       └── other files (e.g., patches, other subject-specific scripts)
│   └── ...
└── scripts: this folder contains all scripts to run experiments, collect & analyze results
│   └── execution
│   │   └── profuzzbench_exec_common.sh: main script to spawn containers and run experiments on them
│   │   └── ...
│   └── analysis
│       └── profuzzbench_generate_csv.sh: this script collect code coverage results from different runs
│       └── profuzzbench_plot.py: sample script for plotting
└── README.md
```


# Fuzzers

ProFuzzBench provides automation scripts for fuzzing the targets with three fuzzers: [AFLnwe](https://github.com/aflnet/aflnwe) (a network-enabled version of AFL, which sends inputs over a TCP/IP sockets instead of files), [AFLNet](https://github.com/aflnet/aflnet) (a fuzzer tailored for stateful network servers), and [StateAFL](https://github.com/stateafl/stateafl) (another fuzzer for stateful network servers).

In the following tutorial, you can find instructions to run AFLnwe and AFLnet (the first two fuzzers supported by ProFuzzBench). For more information about StateAFL, please check out [README-StateAFL.md](README-StateAFL.md).


# Tutorial - Fuzzing LightFTP server with [AFLNet](https://github.com/aflnet/aflnet) and [AFLnwe](https://github.com/aflnet/aflnwe), a network-enabled version of AFL
Follow the steps below to run and collect experimental results for LightFTP, which is a lightweight File Transfer Protocol (FTP) server. The similar steps should be followed to run experiments on other subjects. Each subject program comes with a README.md file showing subject-specific commands to run experiments.

## Step-0. Set up environmental variables
```
git clone https://github.com/profuzzbench/profuzzbench.git
cd profuzzbench
export PFBENCH=$(pwd)
export PATH=$PATH:$PFBENCH/scripts/execution:$PFBENCH/scripts/analysis
```

## Step-1. Build a docker image
The following commands create a docker image tagged lightftp. The image should have everything available for fuzzing and code coverage collection.

```bash
cd $PFBENCH
cd subjects/FTP/LightFTP
docker build . -t lightftp
```

## Step-2. Run fuzzing
Run [profuzzbench_exec_common.sh script](scripts/execution/profuzzbench_exec_common.sh) to start an experiment. The script takes 8 arguments as listed below.

- ***1st argument (DOCIMAGE)*** : name of the docker image
- ***2nd argument (RUNS)***     : number of runs, one isolated Docker container is spawned for each run
- ***3rd argument (SAVETO)***   : path to a folder keeping the results
- ***4th argument (FUZZER)***   : fuzzer name (e.g., aflnet) -- this name must match the name of the fuzzer folder inside the Docker container (e.g., /home/ubuntu/aflnet)
- ***5th argument (OUTDIR)***   : name of the output folder created inside the docker container
- ***6th argument (OPTIONS)***  : all options needed for fuzzing in addition to the standard options written in the target-specific run.sh script
- ***7th argument (TIMEOUT)***  : time for fuzzing in seconds
- ***8th argument (SKIPCOUNT)***: used for calculating coverage over time. e.g., SKIPCOUNT=5 means we run gcovr after every 5 test cases because gcovr takes time and we do not want to run it after every single test case

The following commands run 4 instances of AFLNet and 4 instances of AFLnwe to simultaenously fuzz LightFTP in 60 minutes.

```bash
cd $PFBENCH
mkdir results-lightftp

profuzzbench_exec_common.sh lightftp 4 results-lightftp aflnet out-lightftp-aflnet "-P FTP -D 10000 -q 3 -s 3 -E -K" 3600 5 &
profuzzbench_exec_common.sh lightftp 4 results-lightftp aflnwe out-lightftp-aflnwe "-D 10000 -K" 3600 5
```

If the script runs successfully, its output should look similar to the text below.

```
AFLNET: Fuzzing in progress ...
AFLNET: Waiting for the following containers to stop:  f2da4b72b002 b7421386b288 cebbbc741f93 5c54104ddb86
AFLNET: Collecting results and save them to results-lightftp
AFLNET: Collecting results from container f2da4b72b002
AFLNET: Collecting results from container b7421386b288
AFLNET: Collecting results from container cebbbc741f93
AFLNET: Collecting results from container 5c54104ddb86
AFLNET: I am done!
```

## Step-3. Collect the results
All results (in tar files) should be stored in the folder created in Step-2 (results-lightftp). Specifically, these tar files are the compressed version of output folders produced by all fuzzing instances. If the fuzzer is afl based (e.g., AFLNet, AFLnwe) each folder should contain sub-folders like crashes, hangs, queue and so on. Use [profuzzbench_generate_csv.sh script](scripts/analysis/profuzzbench_generate_csv.sh) to collect results in terms of code coverage over time. The script takes 5 arguments as listed below.

- ***1st argument (PROG)***   : name of the subject program (e.g., lightftp)
- ***2nd argument (RUNS)***   : number of runs
- ***3rd argument (FUZZER)*** : fuzzer name (e.g., aflnet)
- ***4th argument (COVFILE)***: CSV-formatted output file keeping the results
- ***5th argument (APPEND)*** : append mode; set this to 0 for the first fuzzer and 1 for the subsequent fuzzer(s).

The following commands collect the  code coverage results produced by AFLNet and AFLnwe and save them to results.csv.

```bash
cd $PFBENCH/results-lightftp

profuzzbench_generate_csv.sh lightftp 4 aflnet results.csv 0 states.csv
profuzzbench_generate_csv.sh lightftp 4 aflnwe results.csv 1 states.csv
```

The results.csv file should look similar to text below. The file has six columns showing the timestamp, subject program, fuzzer name, run index, coverage type and its value. The file contains both line coverage and branch coverage over time information. Each coverage type comes with two values, in percentage (*_per) and in absolute number (*_abs).

```
time,subject,fuzzer,run,cov_type,cov
1600905795,lightftp,aflnwe,1,l_per,25.9
1600905795,lightftp,aflnwe,1,l_abs,292
1600905795,lightftp,aflnwe,1,b_per,13.3
1600905795,lightftp,aflnwe,1,b_abs,108
1600905795,lightftp,aflnwe,1,l_per,25.9
1600905795,lightftp,aflnwe,1,l_abs,292
```

## Step-4. Analyze the results
The results collected in step 3 (i.e., results.csv) can be used for plotting. For instance, we provide [a sample Python script](scripts/analysis/profuzzbench_plot.py) to plot code coverage over time. Use the following command to plot the results and save it to a file.

```
cd $PFBENCH/results-lightftp

profuzzbench_plot.py -i results.csv -p lightftp -r 4 -c 60 -s 1 -o cov_over_time.png
```

```
cd $PFBENCH/results-lightftp
profuzzbench_state.py -i states.csv -p lightftp -r 4 -c 60 -s 1 -o state_over_time.png
```

This is a sample code coverage report generated by the script. ![Sample report](figures/cov_over_time.png)

# Utility scripts

ProFuzzBench also includes scripts for running all fuzzers on all targes, with pre-configured parameters. To build all targets for all fuzzers, you can run the script [profuzzbench_build_all.sh](scripts/execution/profuzzbench_build_all.sh). To run the fuzzers, you can use the script [profuzzbench_exec_all.sh](scripts/execution/profuzzbench_exec_all.sh).


# Parallel builds

To speed-up the build of Docker images, you can pass the option "-j" to `make`, using the `MAKE_OPT` environment variable and the `--build-arg` option of `docker build`. Example:

```
export MAKE_OPT="-j4"
docker build . -t lightftp --build-arg MAKE_OPT
```

# FAQs

## 1. How do I extend ProFuzzBench?

If you want to add a new protocol and/or a new target server (of a supported protocol), please follow the above folder structure and complete the steps below. We use LightFTP as an example.

### Step-1. Create a new folder containing the protocol/target server

The folder for LightFTP server is [subjects/FTP/LightFTP](subjects/FTP/LightFTP).

### Step-2. Write a Docker file for the new target server and prepare all the subject-specific scripts/files (e.g., target-specific patch, seed corpus)

The following folder structure shows all files we have prepared for fuzzing LightFTP server. Please read [our paper](https://arxiv.org/pdf/2101.05102.pdf) to understand the purposes of these files.

```
subjects/FTP/LightFTP
├── Dockerfile (required): based on this, a target-specific Docker image is built (See Step-1 in the tutorial)
├── run.sh (required): main script to run experiment inside a container
├── cov_script.sh (required): script to do code coverage analysis
├── clean.sh (optional): script to clean server states before fuzzing to improve the stability
├── fuzzing.patch (optional): code changes needed to improve fuzzing results (e.g., remove randomness)
├── gcov.patch (required): code changes needed to support code coverage analysis (e.g., enable gcov, add a signal handler)
├── ftp.dict (optional): a dictionary containing protocol-specific tokens/keywords to support fuzzing
└── in-ftp (required): a seed corpus capturing sequences of client requests sent to the server under test.
│   │       To prepare these seeds, please follow the AFLNet tutorial at https://github.com/aflnet/aflnet.
│   │       Please use ".raw" extension for all seed inputs.
│   │
│   └── ftp_requests_full_anonymous.raw
│   └── ftp_requests_full_normal.raw
└── README.md (optional): a target-specific README containing commands to run experiments
```
All the required files (i.e., Dockerfile, run.sh, cov_script.sh, gcov.patch, and the seed corpus) follow some templates so that one can easily follow them to prepare files for a new target.

### Step-3. Test your new target server

Once a Docker image is successfully built, you should test your commands, as written in a target-specific [README.md](subjects/FTP/LightFTP/README.md), inside a single Docker container. For example, we run the following commands to check if everything is working for LightFTP.

```
//start a container
docker run -it lightftp /bin/bash

//inside the docker container
//run a 60-min fuzzing experiment using AFLNet
cd experiments
run aflnet out-lightftp-aflnet "-P FTP -D 10000 -q 3 -s 3 -E -K -c ./ftpclean.sh" 3600 5
```

If everything works, there should be no error messages and all the results are stored inside the out-lightftp-aflnet folder.

## 2. My experiment "hangs". What could be the reason(s)?

Each experiment has two parts: fuzzing and code coverage analysis. The fuzzing part should complete after the specified timeout; however, the code coverage analysis time is subject-specific and it could take several hours if the generated corpus is large or the target server is slow. You can log into the running containers to check the progress if you think your experiment hangs.


## 3. How do I add another fuzzer to ProFuzzBench?

To add support for an additional fuzzer, we suggest to add a new Dockerfile in the folder of the target, and build the fuzzer on top of the image for the target. For example, the StateAFL fuzzer as been added as an extension to ProFuzzBench. For each supported target, you will find the file `Dockerfile-stateafl` to build the fuzzer in the same container image of the other fuzzers. In that Dockerfile, you can add fuzzer-specific directives. For example, StateAFL also re-builds the target for adding more compile-time instrumentation.

Additionally, you can include a `run-${FUZZER}.sh` script in the target folder, such as `run-stateafl.sh`. The file will be sourced by the `run.sh` script when running a fuzzing experiment. In this script, you can include fuzzer-specific commands, such as to setup environment variables (e.g., the folder for the instrumented build of the target).


