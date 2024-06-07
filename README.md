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

### Docker

Launch the MongoDB server and Jadio Recorder Docker containers.

```bash
git clone https://github.com/hejyll/jadio-recorder
(cd jadio-recorder/docker && docker-compose up -d)
```

## Usage

### CLI

#### `jadio-recorder` command

`jadio-recorder` command does the following:

1. Fetch program
   * Fetch all program information from various radio distribution platforms.
2. Reserve program
   * Extract programs that match the conditions from among all program information.
3. Record program
   * Record programs that match the conditions.

```bash
jadio-recorder \
    --queries-path ./svr/jadio-recorder/queries.json \
    --platform-config-path ./svr/jadio-recorder/config.json \
    --media-root ./media \
    --database-host "mongodb://localhost:27017/"
```

Options for this command:

* `--queries-path`
  * Specify the file path that describes the conditions for recording the program.
  * See [`jadio.ProgramQuery`](https://github.com/hejyll/jadio/blob/main/src/jadio/search.py) for details on how to describe queries.
  * e.g. query file to record TBS station programs that contain the string "JUNK" in the program name.
    ```json
    [{"station_id": "TBS", "program_name": {"$regex": "JUNK"}}]
    ```
* `--platform-config-path`
  * Specify the file path that describes the settings (e.g. login user/pass) for each radio distribution platform.
  * e.g. config file to specify account information for premium members of radiko.jp and onsen.ag
    ```json
    {
      "radiko.jp": {"mail": "hoge@hoge.com", "password": "passw0rd"},
      "onsen.ag": {"mail": "hoge@hoge.com", "password": "passw0rd"}
    }
    ```
* `--media-root`
  * Specify the root directory where recorded radio programs are stored.
  * Program media files are stored under the specified directory with the naming convention `<platform-id>/<station-id>/<program-id>.[m4a,mp4,...]`.
* `--database-host`
  * Specify the MongoDB host.
  * Information on fetch/reserve/recorded programs is managed by MongoDB.
* `--force-fetch`
  * Force fetch programs from platforms. Usually, once a fetch program is done, it will not fetch again within 24 hours.

### Python API

TODO

## License

These codes are licensed under CC0.

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)
