FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    ffmpeg \
    git \
    gnupg \
    python3 \
    python3-dev \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && rm google-chrome-stable_current_amd64.deb

RUN python3 -m pip install git+https://github.com/hejyll/jadio-recorder

COPY ./scripts /jadio/scripts
RUN echo "0 5 * * * root /jadio/scripts/jadio-cron.sh" > /etc/cron.d/cron-jadio

CMD cron -f
