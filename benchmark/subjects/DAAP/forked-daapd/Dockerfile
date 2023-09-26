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
RUN apt-get -y update && \
    apt-get -y install \
    bison \
    flex \
    autotools-dev autoconf automake libtool gettext gawk \
    gperf antlr3 libantlr3c-dev libconfuse-dev libunistring-dev libsqlite3-dev \
    libavcodec-dev libavformat-dev libavfilter-dev libswscale-dev libavutil-dev \
    libasound2-dev libmxml-dev libgcrypt20-dev libavahi-client-dev zlib1g-dev \
    libevent-dev libplist-dev libsodium-dev libjson-c-dev libwebsockets-dev \
    libcurl4-openssl-dev avahi-daemon
USER ubuntu

COPY --chown=ubuntu:ubuntu forked-daapd.patch ${WORKDIR}/forked-daapd.patch
COPY --chown=ubuntu:ubuntu forked-daapd-gcov.patch ${WORKDIR}/forked-daapd-gcov.patch


# Set up environment variables for ASAN
env ASAN_OPTIONS='abort_on_error=1:symbolize=0:detect_leaks=0:detect_stack_use_after_return=1:detect_container_overflow=0:poison_array_cookie=0:malloc_fill_byte=0:max_malloc_fill_size=16777216'

# Download and compile forked-daapd for fuzzing
RUN cd $WORKDIR && \
    git clone https://github.com/ejurgensen/forked-daapd.git && \
    cd forked-daapd && \
    git checkout 2ca10d9 && \
    patch -p1 < $WORKDIR/forked-daapd.patch && \
    autoreconf -i && \
    CC=$AFLNET/afl-clang-fast CFLAGS="-DSQLITE_CORE" ./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var  --disable-mpd --disable-itunes --disable-lastfm --disable-spotify --disable-verification  --disable-shared --enable-static && \
    AFL_USE_ASAN=1 make -C src/ SMARTPL2SQL.c SMARTPL.c DAAP2SQL.c DAAPLexer.c RSPLexer.c RSP2SQL.c && \
    AFL_USE_ASAN=1 make clean all $MAKE_OPT

# Download and compile forked-daapd for code coverage analysis
RUN cd $WORKDIR && \
    git clone https://github.com/ejurgensen/forked-daapd.git forked-daapd-gcov && \
    cd forked-daapd-gcov && \
    git checkout 2ca10d9 && \
    patch -p1 < $WORKDIR/forked-daapd.patch && \
    patch -p1 < $WORKDIR/forked-daapd-gcov.patch && \
    autoreconf -i && \
    CFLAGS="-DSQLITE_CORE -fprofile-arcs -ftest-coverage" LDFLAGS="-fprofile-arcs -ftest-coverage" ./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var  --disable-mpd --disable-itunes --disable-lastfm --disable-spotify --disable-verification  --disable-shared --enable-static && \
    make -C src/ SMARTPL2SQL.c SMARTPL.c DAAP2SQL.c DAAPLexer.c RSPLexer.c RSP2SQL.c && \
    make clean all $MAKE_OPT


# Setting up the environment using root account
USER root

RUN touch /home/ubuntu/experiments/forked-daapd.log && \
    chown ubuntu.root /home/ubuntu/experiments/forked-daapd.log

RUN touch /var/log/forked-daapd.log && \
    chown ubuntu.root /var/log/forked-daapd.log

RUN touch /var/run/forked-daapd.pid && \
    chown ubuntu.root /var/run/forked-daapd.pid

RUN update-rc.d avahi-daemon defaults

RUN mkdir /usr/share/forked-daapd/ && \
    cp -R $WORKDIR/forked-daapd/htdocs /usr/share/forked-daapd/htdocs

RUN ln -s $WORKDIR/MP3 /tmp/MP3

#The script needs to launch dbus and avahi-daemon using sudo
RUN echo "ALL ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Switch back to ubuntu account
USER ubuntu
RUN mkdir ${WORKDIR}/db

COPY --chown=ubuntu:ubuntu in-daap ${WORKDIR}/in-daap
COPY --chown=ubuntu:ubuntu cov_script.sh ${WORKDIR}/cov_script
COPY --chown=ubuntu:ubuntu run.sh ${WORKDIR}/run
COPY --chown=ubuntu:ubuntu MP3 ${WORKDIR}/MP3
COPY --chown=ubuntu:ubuntu forked-daapd.conf ${WORKDIR}/forked-daapd.conf
