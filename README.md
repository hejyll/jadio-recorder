# Jadio Recorder

## Setup

### Install

```bash
pip install git+https://github.com/hejyll/jadio-recorder
```

### Use Docker

Launch the MongoDB server and Jadio Recorder Docker containers.

```bash
export DOCKER_BUILDKIT=1
(cd ./docker && docker-compose up -d)
```

## Usage

### Execute recording

```bash
jadio-recorder \
    --queries-path ./svr/jadio-recorder/queries.json \
    --media-root ./media \
    --platform-config-path ./svr/jadio-recorder/config.json \
    --database-host "mongodb://localhost:27017/"
```

### Queries file

TODO

### Platform config file

TODO

## License

These codes are licensed under CC0.

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)
