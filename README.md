# Jadio Recorder: Recorder for Japanese radio programs

jadio-recorder is a tool to wrap [jadio](https://github.com/hejyll/jadio) and easily record radio programs.

By specifying conditions flexibly, radio programs can be easily recorded. For example, by specifying the following conditions, programs are automatically searched and all found programs are recorded.

* Name of broadcast station
* Keywords in the name or description of the program
* Names of performers or guests
* Specified datetime, and length of the program

## Setup

### Install

```bash
pip install git+https://github.com/hejyll/jadio-recorder
```

### Use Docker

Launch the MongoDB server and Jadio Recorder Docker containers.

```bash
export DOCKER_BUILDKIT=1
git clone https://github.com/hejyll/jadio-recorder
(cd jadio-recorder/docker && docker-compose up -d)
export DOCKER_BUILDKIT=1
```

## Usage

### CLI

#### Record programs

```bash
jadio-recorder \
    --queries-path ./svr/jadio-recorder/queries.json \
    --media-root ./media \
    --platform-config-path ./svr/jadio-recorder/config.json \
    --database-host "mongodb://localhost:27017/"
```

#### Queries file

TODO

#### Platform config file

TODO

### Python API

TODO

## License

These codes are licensed under CC0.

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)
