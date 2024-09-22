[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10115151.svg)](https://doi.org/10.5281/zenodo.10115151)

# ChatAFL Artifact

<img align="right" src="https://github.com/ChatAFLndss/ChatAFL/assets/7456946/266f7d4f-c0af-4846-9e13-064e79c812b0">


ChatAFL is a protocol fuzzer guided by large language models (LLMs). It is built on top of [AFLNet](https://github.com/aflnet/aflnet) but integrates with three concrete components. Firstly, the fuzzer uses the LLM to extract a machine-readable grammar for a protocol that is used for structure-aware mutation. Secondly, the fuzzer uses the LLM to increase the diversity of messages in the recorded message sequences that are used as initial seeds. Lastly, the fuzzer uses the LLM to break out of a coverage plateau, where the LLM is prompted to generate messages to reach new states. 

The ChatAFL artifact is configured within [ProfuzzBench](https://github.com/profuzzbench/profuzzbench), a widely-used benchmark for stateful fuzzing of network protocols. This allows for smooth integration with an already established format.

## Folder structure

```
ChatAFL-Artifact
├── aflnet: a modified version of AFLNet which outputs states and state transitions 
├── analyse.sh: analysis script 
├── benchmark: a modified version of ProfuzzBench, containing only text-based protocols with the addition of Lighttpd 1.4 
├── clean.sh: clean script
├── ChatAFL: the source code of ChatAFL, with all strategies proposed in the paper
├── ChatAFL-CL1: ChatAFL, which only uses the structure-aware mutations (c.f. Ablation study) 
├── ChatAFL-CL2: ChatAFL, which only uses the structure-aware and initial seed enrichment (c.f. Ablation study)
├── deps.sh: the script to install dependencies, asks for the password when executed
├── README: this file
├── run.sh: the execution script to run fuzzers on subjects and collect data
└── setup.sh: the preparation script to set up docker images
```

## Citing ChatAFL

ChatAFL has been accepted for publication at the 31st Annual Network and Distributed System Security Symposium (NDSS) 2024. The paper is also available [here](https://mengrj.github.io/files/chatafl.pdf). If you use this code in your scientific work, please cite the paper as follows:

```
@inproceedings{chatafl,
author={Ruijie Meng and Martin Mirchev and Marcel B\"{o}hme and Abhik Roychoudhury},
title={Large Language Model guided Protocol Fuzzing},
booktitle={Proceedings of the 31st Annual Network and Distributed System Security Symposium (NDSS)},
year={2024},}
```

## 1. Setup and Usage

### 1.1. Installing Dependencies

`Docker`, `Bash`, `Python3` with `pandas` and `matplotlib` libraries. We provide a helper script `deps.sh` which runs the required steps to ensure that all dependencies are provided:

```bash
./deps.sh
```

### 1.2. Preparing Docker Images [~40 minutes]

Run the following command to set up all docker images, including the subjects with all fuzzers:

```bash
KEY=<OPENAI_API_KEY> ./setup.sh
```

The process is estimated to take about 40 minutes. OPENAI_API_KEY is your OpenAI key and please refer to [this](https://openai.com/) about how to obtain a key.

### 1.3. Running Experiments

Utilize the `run.sh` script to run experiments. The command is as follows:

```bash
 ./run.sh <container_number> <fuzzed_time> <subjects> <fuzzers>
```

Where `container_number` specifies how many containers are created to run a single fuzzer on a particular subject (each container runs one fuzzer on one subject). `fuzzed_time` indicates the fuzzing time in minutes. `subjects` is the list of subjects under test, and `fuzzers` is the list of fuzzers that are utilized to fuzz subjects. For example, the command (`run.sh 1 5 pure-ftpd chatafl`) would create 1 container for the fuzzer ChatAFL to fuzz the subject pure-ftpd for 5 minutes. In a short cut, one can execute all fuzzers and all subjects by using the writing `all` in place of the subject and fuzzer list.

When the script completes, in the `benchmark` directory a folder `result-<name of subject>` will be created, containing fuzzing results for each run.

### 1.4. Analyzing Results

The `analyze.sh` script is used to analyze data and construct plots illustrating the average code and state coverage over time for fuzzers on each subject. The script is executed using the following command:

```bash
./analyze.sh <subjects> <fuzzed_time> 
```

The script takes in 2 arguments - `subjects` is the list of subjects under test and `fuzzed_time` is the duration of the run to be analyzed. Note that, the second argument is optional and the script by default will assume that the execution time is 1440 minutes, which is equal to 1 day. For example, the command (`analyze.sh exim 240`) will analyze the first 4 hours of the execution results of the exim subject.

Upon completion of execution, the script will process the archives by construcing csv files, containing the covered number of branches, states, and state transitions over time. Furthermore, these csv files will be processed into PNG files which are plots, illustrating the average code and state coverage over time for fuzzers on each subject (`cov_over_time...` for the code and branch coverage, `state_over_time...` for the state and state transition coverage). All of this information is moved to a `res_<subject name>` folder in the root directory with a timestamp.

### 1.5. Cleaning Up

When the evaluation of the artifact is completed, running the `clean.sh` script will ensure that the only leftover files are in this directory:

```bash
./clean.sh
```

## 2. Functional Analysis

### 2.1. Examining LLM-generated Grammars

The source code for the grammar generation is located in the function `setup_llm_grammars` in `afl-fuzz.c` with helper functions in `chat-llm.c`.

The responses of the LLM for the grammar generation can be found in the `protocol-grammars` directory in the resulting archive of a run.

### 2.2. Examining Enriched Seeds

The source code for the seed enrichment is located in the function `get_seeds_with_messsage_types` in `afl-fuzz.c` with helper functions in `chat-llm.c`.

The enriched seeds can be found in the seed `queue` directory in the resulting archive of a run. These files have the name `id:...,orig:enriched_`.

### 2.3. Examining State-stall Responses

The source code for the state stall processing is located in the function `fuzz_one` and starts at line 6846 (`if (uninteresting_times >= UNINTERESTING_THRESHOLD && chat_times < CHATTING_THRESHOLD){`).

The state stall prompts and their corresponding responses can be found in the `stall-interactions` directory in the resulting archive of a run. The files are of the form `request-<id>` and `response-<id>`, containing the request we have constructed and the response from the LLM.


## 3. Reproduction Results

To conduct the experiments outlined in the paper, we utilized a vast amount of resources. It is impractical to replicate all the experiments within a single day using a standard desktop machine. To facilitate the evaluation of the artifact, we downsized our experiments, employing fewer fuzzers, subjects, and iterations.

### 3.1. Comparison with Baselines [5 human-minutes + 180 compute-hours]

ChatAFL can cover more states and code, and achieve the same state and code coverage faster than the baseline tool AFLNet. We run the following commands to support these claims:

```bash
./run.sh 5 240 kamailio,pure-ftpd,live555 chatafl,aflnet
./analyze.sh kamailio,pure-ftpd,live555 240
```

Upon completion of the commands, a folder prefixed with `res_` will be generated. This folder contains PNG files illustrating the state and code covered by two fuzzers over time as well as the output archives from all the runs. It will be placed in the root directory of the artifact.

### 3.2. Ablation Study [5 human-minutes + 180 compute-hours]

Each strategy proposed in ChatAFL contributes to varying degrees of improvement in code coverage. We run the following commands to support this claim:

```bash
./run.sh 5 240 proftpd,exim chatafl,chatafl-cl1,chatafl-cl2
./analyze.sh proftpd,exim 240
```

Upon completion of the commands, a folder prefixed with `res_` will be generated. This folder contains PNG files illustrating the code covered by three fuzzers over time as well as the output archives from all the runs. It will be placed in the root directory of the artifact.

## 4. Customization

### 4.1. Enhancing or experimenting with ChatAFL

If a modification is done to any of the fuzzers, re-executing `setup.sh` will rebuild all the images with the modified version. All provided versions of ChatAFL contain a Dockerfile, allowing for the checking of build failures in the same environment as the one for the subjects and having a clean image, where one can setup different subjects.

### 4.2. Tuning fuzzer parameters

All parameters, used in the experiments are located in `config.h` and `chat-llm.h`. The parameters, specific to ChatAFL are:

In `config.h`:

* EPSILON_CHOICE
* UNINTERESTING_THRESHOLD
* CHATTING_THRESHOLD  

In `chat-llm.h`:

* STALL_RETRIES
* GRAMMAR_RETRIES
* MESSAGE_TYPE_RETRIES
* ENRICHMENT_RETRIES
* MAX_ENRICHMENT_MESSAGE_TYPES
* MAX_ENRICHMENT_CORPUS_SIZE

### 4.3. Adding new subjects

To add an extra subject, we refer to [the instructions, provied by ProfuzzBench](https://github.com/profuzzbench/profuzzbench#1-how-do-i-extend-profuzzbench) for adding a new benchmark subject. As an example, we have added Lighttpd 1.4 as a new subject to the benchmark.

### 4.4. Troubleshooting

If the fuzzer terminates with an error, a premature "I am done" message will be displayed. To examine this issue, running `docker logs <containerID>` will display the logs of the failing container.

### 4.5. Working on GPT-4

We have released a new version of ChatAFL utilizing GPT-4: [gpt4-version](https://github.com/ChatAFLndss/ChatAFL/tree/gpt4-version). However, it hasn't been extensively tested yet. Please feel free to reach out if you encounter any issues during use.

## 5. Limitations

The current artifact interacts with OpenAI's Large Language Models (`gpt-3.5-turbo-instruct` and `gpt-3.5-turbo`). This puts a third-party limit to the degree of parallelization. The models used in this artifact have a hard limit of 150,000 tokens per minute.

## 6. Special Thanks

We would like to thank the creators of [AFLNet](https://github.com/aflnet/aflnet) and [ProFuzzBench](https://github.com/profuzzbench/profuzzbench) for the tooling and infrastructure they have provided to the community.

## 7. License

This artifact is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.
