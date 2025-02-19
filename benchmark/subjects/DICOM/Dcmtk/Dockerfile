FROM ubuntu:20.04

# Install common dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && \
    apt-get -y install sudo \ 
    apt-utils \
    build-essential \
    openssl \
    clang \
    graphviz-dev \
    git \
    autoconf \
    libgnutls28-dev \
    libssl-dev \
    llvm \
    python3-pip \
    nano \
    net-tools \
    vim \
    gdb \
    netcat \
    strace \
    libcap-dev \
    libpcre2-dev \
    libpcre2-8-0 \
    libcurl4-openssl-dev \
    libjson-c-dev \
    wget

# Add a new user ubuntu, pass: ubuntu
RUN groupadd ubuntu && \
    useradd -rm -d /home/ubuntu -s /bin/bash -g ubuntu -G sudo -u 1000 ubuntu -p "$(openssl passwd -1 ubuntu)"

RUN chmod 777 /tmp

RUN pip3 install gcovr==4.2

# Use ubuntu as default username
USER ubuntu
WORKDIR /home/ubuntu

# Import environment variable to pass as parameter to make (e.g., to make parallel builds with -j)
ARG MAKE_OPT

# Set up fuzzers
COPY --chown=ubuntu:ubuntu aflnet aflnet
RUN cd aflnet && \
    make clean all $MAKE_OPT && \
    cd llvm_mode && make $MAKE_OPT

COPY --chown=ubuntu:ubuntu chatafl chatafl
RUN cd chatafl && \
    make clean all $MAKE_OPT && \
    cd llvm_mode && make $MAKE_OPT

COPY --chown=ubuntu:ubuntu chatafl-cl1 chatafl-cl1
RUN cd chatafl-cl1 && \
    make clean all $MAKE_OPT && \
    cd llvm_mode && make $MAKE_OPT

COPY --chown=ubuntu:ubuntu chatafl-cl2 chatafl-cl2
RUN cd chatafl-cl2 && \
    make clean all $MAKE_OPT && \
    cd llvm_mode && make $MAKE_OPT

COPY --chown=ubuntu:ubuntu chatafl-seed chatafl-seed
RUN cd chatafl-seed && \
    make clean all $MAKE_OPT && \
    cd llvm_mode && make $MAKE_OPT

COPY --chown=ubuntu:ubuntu chatafl-bin chatafl-bin
RUN cd chatafl-bin && \
    make clean all $MAKE_OPT && \
    cd llvm_mode && make $MAKE_OPT

COPY --chown=ubuntu:ubuntu snetgen snetgen
RUN cd snetgen && \
    make clean all $MAKE_OPT && \
    cd llvm_mode && make $MAKE_OPT
        
# Set up environment variables for AFLNet
ENV WORKDIR="/home/ubuntu/experiments"
ENV AFLNET="/home/ubuntu/aflnet"
ENV PATH="${PATH}:${AFLNET}:/home/ubuntu/.local/bin:${WORKDIR}"
ENV AFL_PATH="${AFLNET}"
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 \
    AFL_SKIP_CPUFREQ=1 \
    AFL_NO_AFFINITY=1
ENV OPENAI_API_KEY="1"


RUN mkdir $WORKDIR

USER root
RUN apt-get -y install cmake

COPY --chown=ubuntu:ubuntu fuzzing.patch ${WORKDIR}/fuzzing.patch
COPY --chown=ubuntu:ubuntu normal.patch ${WORKDIR}/normal.patch

# Set up environment variables for ASAN
ENV ASAN_OPTIONS='abort_on_error=1:symbolize=0:detect_leaks=0:detect_stack_use_after_return=1:detect_container_overflow=0:poison_array_cookie=0:malloc_fill_byte=0:max_malloc_fill_size=16777216'

# Download and compile Dcmtk for fuzzing
RUN cd $WORKDIR && \
    git clone https://github.com/DCMTK/dcmtk && \
    cd dcmtk && \
    git checkout 7f8564c && \
    patch -p1 < $WORKDIR/fuzzing.patch && \
    mkdir build && cd build && \
    cmake .. && \
    AFL_USE_ASAN=1 make dcmqrscp $MAKE_OPT


# Download and compile Dcmtk for coverage analysis
RUN cd $WORKDIR && \
    git clone https://github.com/DCMTK/dcmtk dcmtk-gcov && \
    cd dcmtk-gcov && \
    git checkout 7f8564c && \
    patch -p1 < $WORKDIR/normal.patch && \
    mkdir build && cd build && \
    cmake -G"Unix Makefiles" .. -DCMAKE_C_FLAGS="-g -fprofile-arcs -ftest-coverage" -DCMAKE_CXX_FLAGS="-g -fprofile-arcs -ftest-coverage" && \
    make dcmqrscp $MAKE_OPT


# Setup server

COPY --chown=ubuntu:ubuntu dcmqrscp.cfg ${WORKDIR}/dcmqrscp.cfg
COPY --chown=ubuntu:ubuntu in-dicom ${WORKDIR}/in-dicom
COPY --chown=ubuntu:ubuntu cov_script.sh ${WORKDIR}/cov_script
COPY --chown=ubuntu:ubuntu run.sh ${WORKDIR}/run
COPY --chown=ubuntu:ubuntu clean.sh ${WORKDIR}/clean
COPY --chown=ubuntu:ubuntu dicom.dic ${WORKDIR}/dcmtk/dcmdata/data/dicom.dic
COPY --chown=ubuntu:ubuntu SNetGen.py ${WORKDIR}/SNetGen.py
COPY --chown=ubuntu:ubuntu utility ${WORKDIR}/utility
COPY --chown=ubuntu:ubuntu LLM ${WORKDIR}/LLM

ENV DCMDICTPATH=${WORKDIR}/dcmtk/dcmdata/data/dicom.dic

RUN cd $WORKDIR/dcmtk/build/bin && \
    mkdir ACME_STORE && \
    cp $WORKDIR/dcmqrscp.cfg ./

RUN cd $WORKDIR/dcmtk-gcov/build/bin && \
    mkdir ACME_STORE && \
    cp $WORKDIR/dcmqrscp.cfg ./
