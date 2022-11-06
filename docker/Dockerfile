FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    ffmpeg \
    git \
    python3 \
    python3-dev \
    python3-pip \
&& rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

RUN python3 -m pip install git+https://github.com/hejyll/jpradio-recorder
   
COPY ./jpradio-recorder.sh /etc/cron.daily/
RUN ln -sf /proc/1/fd/1 /var/log/cron.log

CMD crond -f
