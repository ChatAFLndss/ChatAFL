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

RUN pip install gcovr==4.2

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

COPY --chown=ubuntu:ubuntu fuzzing.patch ${WORKDIR}/fuzzing.patch
COPY --chown=ubuntu:ubuntu gcov.patch ${WORKDIR}/gcov.patch

USER root
RUN apt -y install automake
USER ubuntu

# Set up environment variables for ASAN
env ASAN_OPTIONS='abort_on_error=1:symbolize=0:detect_leaks=0:detect_stack_use_after_return=1:detect_container_overflow=0:poison_array_cookie=0:malloc_fill_byte=0:max_malloc_fill_size=16777216'

# Set up PureFTPD for fuzzing
RUN cd ${WORKDIR} && \
    git clone https://github.com/jedisct1/pure-ftpd.git && \
    cd pure-ftpd && \
    git checkout 10122d9f && \
    patch -p1 < ${WORKDIR}/fuzzing.patch && \
    ./autogen.sh && \
    CC="afl-clang-fast" CXX="afl-clang-fast++" CFLAGS="-fsanitize=address -g -O0" CXXFLAGS="-fsanitize=address -g -O0" LDFLAGS="-fsanitize=address" ./configure --without-privsep -without-capabilities && \
    make $MAKE_OPT

# Set up PureFTPD for coverage analysis
RUN cd ${WORKDIR} && \
    git clone https://github.com/jedisct1/pure-ftpd.git pure-ftpd-gcov && \
    cd pure-ftpd-gcov && \
    git checkout 10122d9f && \
    patch -p1 < ${WORKDIR}/gcov.patch && \
    ./autogen.sh && \
    CC=cc CXX=c++ CFLAGS="-fprofile-arcs -ftest-coverage" CPPFLAGS="-fprofile-arcs -ftest-coverage" CXXFLAGS="-fprofile-arcs -ftest-coverage" LDFLAGS="-fprofile-arcs -ftest-coverage" ./configure --without-privsep -without-capabilities && \
    make $MAKE_OPT

COPY --chown=ubuntu:ubuntu in-ftp ${WORKDIR}/in-ftp
COPY --chown=ubuntu:ubuntu ftp.dict ${WORKDIR}/ftp.dict
COPY --chown=ubuntu:ubuntu run.sh ${WORKDIR}/run
COPY --chown=ubuntu:ubuntu clean.sh ${WORKDIR}/clean
COPY --chown=ubuntu:ubuntu cov_script.sh ${WORKDIR}/cov_script

# Switch default user to root
USER root
WORKDIR /home/ubuntu

RUN useradd -rm -d /home/fuzzing -s /bin/bash -g ubuntu -G sudo -u 1001 fuzzing -p "$(openssl passwd -1 fuzzing)"

# For debugging purposes
RUN apt-get -y install ftp
