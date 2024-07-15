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
RUN git clone https://github.com/profuzzbench/aflnet.git && \
    cd aflnet && \
    make clean all $MAKE_OPT && \
    cd llvm_mode && make $MAKE_OPT

RUN git clone https://github.com/profuzzbench/aflnwe.git && \
    cd aflnwe && \
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

COPY --chown=ubuntu:ubuntu key.pem ${WORKDIR}/key.pem
COPY --chown=ubuntu:ubuntu cert.pem ${WORKDIR}/cert.pem
COPY --chown=ubuntu:ubuntu rand.patch ${WORKDIR}/rand.patch

# Set up environment variables for ASAN
env ASAN_OPTIONS='abort_on_error=1:symbolize=0:detect_leaks=0:detect_stack_use_after_return=1:detect_container_overflow=0:poison_array_cookie=0:malloc_fill_byte=0:max_malloc_fill_size=16777216'

# Download and compile OpenSSL for fuzzing
RUN cd ${WORKDIR} && \
    git clone https://github.com/openssl/openssl.git && \
    cd openssl && \
    cp ${WORKDIR}/*.pem ./ && \
    git checkout 0437435a && \
    patch -p1 < ${WORKDIR}/rand.patch && \
    CC=afl-clang-fast ./config no-shared --with-rand-seed=none && \
    CC=afl-clang-fast make include/openssl/configuration.h include/openssl/opensslv.h include/crypto/bn_conf.h include/crypto/dso_conf.h && \
    AFL_USE_ASAN=1 CC=afl-clang-fast make apps/openssl $MAKE_OPT


# Download and compile OpenSSL for coverage analysis
RUN cd ${WORKDIR} && \
    git clone https://github.com/openssl/openssl.git openssl-gcov && \
    cd openssl-gcov && \
    cp ${WORKDIR}/*.pem ./ && \
    git checkout 0437435a && \
    patch -p1 < ${WORKDIR}/rand.patch && \
    CFLAGS="-fprofile-arcs -ftest-coverage" LDFLAGS="-fprofile-arcs -ftest-coverage" ./config no-shared --with-rand-seed=none && \
    CFLAGS="-fprofile-arcs -ftest-coverage" LDFLAGS="-fprofile-arcs -ftest-coverage" make include/openssl/configuration.h include/openssl/opensslv.h include/crypto/bn_conf.h include/crypto/dso_conf.h && \
    CFLAGS="-fprofile-arcs -ftest-coverage" LDFLAGS="-fprofile-arcs -ftest-coverage" make apps/openssl $MAKE_OPT

COPY --chown=ubuntu:ubuntu in-tls ${WORKDIR}/in-tls
COPY --chown=ubuntu:ubuntu tls.dict ${WORKDIR}/tls.dict
COPY --chown=ubuntu:ubuntu cov_script.sh ${WORKDIR}/cov_script
COPY --chown=ubuntu:ubuntu run.sh ${WORKDIR}/run
