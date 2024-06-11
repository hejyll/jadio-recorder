# Jadio Recorder

jadio-recorder is a tool to wrap [jadio](https://github.com/hejyll/jadio) and easily record Japanese web radio programs.

By specifying conditions flexibly, radio programs can be easily recorded. For example, by specifying the following conditions, programs are automatically searched and all found programs are recorded.

* Names of radio services or broadcast stations
* Keywords in the title or description of the program
* Names of performers or guests
* Published date and time, and duration of the program

## Setup

### Install jadio-recorder in local

```bash
pip install git+https://github.com/hejyll/jadio-recorder
```

### Run Docker containers

Launch Docker containers of MongoDB, HTTP and Jadio servers.

```bash
git clone https://github.com/hejyll/jadio-recorder
(cd jadio-recorder/docker && docker-compose up -d)
```

## Usage

### Docker

### CLI (`jadio` command)

#### `reserve` sub-command

Reserve radio program recordings.

```bash
jadio reserve \
    ./reserve_config.json \
    --db-host mongodb://localhost:27017/
```

**Options:**

* `--db-host` (default: `mongodb://localhost:27017/`)
  * Specify the MongoDB host to be used by `jadio` command.

#### `record` sub-command

Record a reserved radio programs with `reserve` sub-command.

```bash
jadio record \
    --service-config-path ./configs/service_config.json \
    --media-root ./media \
    --db-host mongodb://localhost:27017/
```

**Options:**

* `--force-fetch`
  * Force fetch programs from services.
  * In the `record` sub-command, fetch program data from all radio services and register them in the DB. Since the frequency of updating program data of services is only about one day, the data is usually not re-fetched if it has been within one day since the last fetch.
* `--service-config-path` (default: TODO)
  * Specify the file path that describes the settings for each radio service.
  * e.g. config file to specify premium account information of radiko.jp and onsen.ag
    ```json
    {
      "radiko.jp": {"mail": "hoge@hoge.com", "password": "passw0rd"},
      "onsen.ag": {"mail": "hoge@hoge.com", "password": "passw0rd"}
    }
    ```
* `--media-root` (default: `./media/`)
  * Specify the root directory where recorded radio programs are stored.
  * Program media file (`media.[m4a,mp4,...]`) and data file (`program.json`) are stored under `<media-root>/<service-id>/<program-id>/`.
* `--db-host` (default: `mongodb://localhost:27017/`)
  * Specify the MongoDB host to be used by `jadio` command.

#### `group` sub-command

Group recorded radio programs to compose Podcast RSS feeds.

```bash
jadio group \
    ./group_config.json \
    --db-host mongodb://localhost:27017/
```

**Options:**

* `--db-host` (default: `mongodb://localhost:27017/`)
  * Specify the MongoDB host to be used by `jadio` command.

#### `feed` sub-command

Create or update Podcast RSS feeds of recorded radio programs.

```bash
jadio feed \
    --rss-root ./rss \
    --media-root ./media \
    --http-host http://localhost \
    --db-host mongodb://localhost:27017/
```

**Options:**

* `--rss-root` (default: `./rss/`)
  * Specify the root directory where created Podcast RSS feeds are stored.
* `--media-root` (default: `./media/`)
  * Specify the same path as `--media-root` in the `record` sub-command.
* `--http-host` (default: `http://localhost`)
  * Specify the HTTP host serving the recorded media files and RSS feed files.
* `--db-host` (default: `mongodb://localhost:27017/`)
  * Specify the MongoDB host to be used by `jadio` command.

## API

See docstring in the Python file under [`src/jadio_recorder/`](src/jadio_recorder/).

## Configs

### For `reserve` sub-command

### For `group` sub-command

## License

These codes are licensed under MIT License.
