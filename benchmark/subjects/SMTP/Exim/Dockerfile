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

# Set up environment variables for AFLNet
ENV WORKDIR="/home/ubuntu/experiments"
ENV AFLNET="/home/ubuntu/aflnet"
ENV PATH="${PATH}:${AFLNET}:/home/ubuntu/.local/bin:${WORKDIR}"
ENV AFL_PATH="${AFLNET}"
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 \
    AFL_SKIP_CPUFREQ=1 \
    AFL_NO_AFFINITY=1


RUN mkdir $WORKDIR

USER root

RUN apt-get install -y psmisc

RUN apt-get -y install \
    libpcre2-dev \
    pkg-config \
    libdb-dev \
    libgdbm-dev

COPY --chown=ubuntu:ubuntu exim.patch ${WORKDIR}/exim.patch
COPY --chown=ubuntu:ubuntu exim-response-code.patch ${WORKDIR}/exim-response-code.patch
COPY --chown=ubuntu:ubuntu exim-rand.patch ${WORKDIR}/exim-rand.patch
COPY --chown=ubuntu:ubuntu exim-log-bug.patch ${WORKDIR}/exim-log-bug.patch
COPY --chown=ubuntu:ubuntu exim.configure.patch ${WORKDIR}/exim.configure.patch

# Set up environment variables for ASAN
env ASAN_OPTIONS='abort_on_error=1:symbolize=0:detect_leaks=0:detect_stack_use_after_return=1:detect_container_overflow=0:poison_array_cookie=0:malloc_fill_byte=0:max_malloc_fill_size=16777216'

# Download, compile and install Exim for fuzzing
RUN cd ${WORKDIR} && \
    git clone https://github.com/Exim/exim && \
    cd exim && \
    git checkout d6a5a05b84 && \
    patch -p1 < ${WORKDIR}/exim-response-code.patch && \
    patch -p1 < ${WORKDIR}/exim-rand.patch && \
    patch -p1 < ${WORKDIR}/exim-log-bug.patch && \
    cd src; mkdir Local; cp src/EDITME Local/Makefile && \
    cd Local; patch -p1 < ${WORKDIR}/exim.patch; cd .. && \
    AFL_USE_ASAN=1 make CFLAGS="-DUSE_OPENSSL=1" LDFLAGS+="-lssl -lcrypto" CC=afl-clang-fast clean all install $MAKE_OPT

# Download and compile Exim for coverage analysis
RUN cd ${WORKDIR} && \
    git clone https://github.com/Exim/exim exim-gcov && \
    cd exim-gcov && \
    git checkout d6a5a05b84 && \
    patch -p1 < ${WORKDIR}/exim-rand.patch && \
    patch -p1 < ${WORKDIR}/exim-log-bug.patch && \
    cd src; mkdir Local; cp src/EDITME Local/Makefile && \
    cd Local; patch -p1 < ${WORKDIR}/exim.patch; cd .. && \
    make CFLAGS="-fprofile-arcs -ftest-coverage -DUSE_OPENSSL=1" LDFLAGS="-fprofile-arcs -ftest-coverage -lssl -lcrypto" LFLAGS+="-lgcov --coverage" clean all $MAKE_OPT

# Configure exim
RUN cd /usr/exim && \
    patch -p1 < ${WORKDIR}/exim.configure.patch && \
    chmod 1777 /var/mail

ENV PATH="/usr/exim/bin:${PATH}"

COPY --chown=ubuntu:ubuntu in-smtp ${WORKDIR}/in-smtp
COPY --chown=ubuntu:ubuntu smtp.dict ${WORKDIR}/smtp.dict
COPY --chown=ubuntu:ubuntu cov_script.sh ${WORKDIR}/cov_script
COPY --chown=ubuntu:ubuntu run.sh ${WORKDIR}/run
COPY --chown=ubuntu:ubuntu clean.sh ${WORKDIR}/clean
