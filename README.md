# Jadio Recorder

jadio-recorder is a tool to wrap [jadio](https://github.com/hejyll/jadio) and easily record Japanese web radio programs.

By specifying conditions flexibly, radio programs can be easily recorded. For example, by specifying the following conditions, programs are automatically searched and all found programs are recorded.

* Names of radio services or broadcast stations
* Keywords in the title or description of the program
* Names of performers or guests
* Published date and time, and duration of the program

## Setup

### Case: Using Docker (Recommended)

Launch Docker containers of MongoDB, HTTP and Jadio servers.

```bash
git clone https://github.com/hejyll/jadio-recorder
(cd jadio-recorder/docker && docker-compose up -d)
```

### Case: Direct installation on the host

TODO

#### Setup MongoDB server

#### Setup HTTPD server

#### Install jadio-recorder in local

```bash
pip install git+https://github.com/hejyll/jadio-recorder
```

## Usage

### Docker

### CLI (`jadio` command)

#### `reserve` sub-command

Reserve radio program recordings.

```bash
jadio reserve \
    ./data/configs/reserve.json \
    --db-host mongodb://localhost:27017/
```

See [Config for `reserve` and `group` sub-command](#config-for-reserve-and-group-sub-command) for how to describe the  config file (`./data/configs/reserve.json`) (JSON).

**Options:**

* `--db-host` (default: `mongodb://localhost:27017/`)
  * Specify the MongoDB host to be used by `jadio` command.

#### `record` sub-command

Record a reserved radio programs with `reserve` sub-command.

```bash
jadio record \
    --service-config-path ./data/configs/service.json \
    --media-root ./data/media/ \
    --db-host mongodb://localhost:27017/
```

**Options:**

* `--force-fetch`
  * Force fetch programs from services.
  * In the `record` sub-command, fetch program data from all radio services and register them in the DB. Since the frequency of updating program data of services is only about one day, the data is usually not re-fetched if it has been within one day since the last fetch.
* `--service-config-path` (default: `./data/configs/service.json`)
  * Specify the file path that describes the settings for each radio service.
  * e.g. config file to specify premium account information of radiko.jp and onsen.ag
    ```json
    {
      "radiko.jp": {"mail": "hoge@hoge.com", "password": "passw0rd"},
      "onsen.ag": {"mail": "hoge@hoge.com", "password": "passw0rd"}
    }
    ```
* `--media-root` (default: `./data/media/`)
  * Specify the root directory where recorded radio programs are stored.
  * Program media file (`media.[m4a,mp4,...]`) and data file (`program.json`) are stored under `<media-root>/<service-id>/<program-id>/`.
* `--db-host` (default: `mongodb://localhost:27017/`)
  * Specify the MongoDB host to be used by `jadio` command.

#### `group` sub-command

Group recorded radio programs to compose Podcast RSS feeds.

Program groups reserved by `reserve` sub-command will have `ProgramGroup.{enable_record,enable_feed}` set to true, so there is no need to execute `group` sub-command again.

```bash
jadio group \
    ./data/configs/group.json \
    --db-host mongodb://localhost:27017/
```

See [Config for `reserve` and `group` sub-command](#config-for-reserve-and-group-sub-command) for how to describe the  config file (`./data/configs/group.json`) (JSON).

**Options:**

* `--db-host` (default: `mongodb://localhost:27017/`)
  * Specify the MongoDB host to be used by `jadio` command.

#### `feed` sub-command

Create or update Podcast RSS feeds of recorded radio programs.

```bash
jadio feed \
    --rss-root ./data/rss \
    --media-root ./data/media \
    --http-host http://localhost \
    --db-host mongodb://localhost:27017/
```

**Options:**

* `--rss-root` (default: `./data/rss/`)
  * Specify the root directory where created Podcast RSS feeds are stored.
* `--media-root` (default: `./data/media/`)
  * Specify the same path as `--media-root` in the `record` sub-command.
* `--http-host` (default: `http://localhost`)
  * Specify the HTTP host serving the recorded media files and RSS feed files.
* `--db-host` (default: `mongodb://localhost:27017/`)
  * Specify the MongoDB host to be used by `jadio` command.

#### Config for `reserve` and `group` sub-command

Just describe the data fields listed in [Data fields / `ProgramGroup`](#programgroup) in JSON as follows ([`data/configs/reserve.json`](data/configs/reserve.json)).

```json
[
  {
    "query": {"station_id": "TBS", "keywords": "JUNK"},
    "category": "お笑い",
    "link_url": "https://www.tbsradio.jp/junk/",
    "image_url": "https://tbsradio.g.kuroco-img.app/v=1624347703/files/topics/743_ext_18_0.jpg"
  }
]
```

## API

See docstring in the Python file under [`src/jadio_recorder/`](src/jadio_recorder/).

## Data fields

### [`ProgramGroup`](src/jadio_recorder/program_group.py)

| Field name | Type | Description |
| -- | -- | -- |
| `query` | `ProgramQuery` | Query for the program to be grouped. |
| `title` | str | Title of the program group. |
| `description` | str | Description of the program group. |
| `category` | str or `ProgramCategory` or list | Category of the program group. Multiple categories can be specified. |
| `tags` | str or list | Any tag attached to the program group. |
| `copyright` | str | Copyright of the program group. |
| `link_url` | str | URL of the program group link. |
| `image_url` | str | URL of the program group image. |
| `author` | str | Author of the program group. |
| `enable_record` | bool | Whether to record programs that correspond to the program group or not. |
| `enable_feed` | bool | Whether to feed the program group or not. |

### [`ProgramQuery`](src/jadio_recorder/program_query.py)

| Field name | Type | Description |
| -- | -- | -- |
| `service_id` | condition of (int or str) | Search condition for service ID(s). |
| `station_id` | condition of (int or str) | Search condition for station ID(s). |
| `program_id` | condition of (int or str) | Search condition for program ID(s). |
| `episode_id` | condition of (int or str) | Search condition for episode ID(s). |
| `pub_date` | condition of `datetime.datetime` | Search condition for publication date. The search condition changes depending on the value given. See [docstring](src/jadio_recorder/program_query.py) for details. |
| `duration` | condition of (int or float) | Search condition for duration. The search condition changes depending on the value given. See [docstring](src/jadio_recorder/program_query.py) for details. |
| `keywords` | condition of str | Search keywords. Search for text strings against program titles, descriptions and information, performers, and guests. |
| `is_video` | condition of bool | Search condition whether video or audio. |

### [`ProgramCategory`](src/jadio_recorder/program_category.py)

Refers to the program categories at https://podcast.1242.com/.

| Name | Value | [iTunes category](https://podcasters.apple.com/support/1691-apple-podcasts-categories) |
| -- | -- | -- |
| `COMEDY` | お笑い | Comedy |
| `LEISURE` | エンタメ | Leisure |
| `NEWS` | ニュース | News |
| `BUSINESS` | ビジネス | News / Business News |
| `ANIMATION` | アニメ | Leisure / Animation &amp; Manga |
| `MANGA` | 漫画 | Leisure / Animation &amp; Manga |
| `GAMES` | ゲーム | Leisure / Games |
| `SPORTS` | スポーツ | Sports |
| `HEALTH` | 健康 | Health &amp; Fitness |
| `EDUCATION` | 学習 | Education |
| `PHILOSOPHY` | 哲学 | Society &amp; Culture / Philosophy |
| `MUSIC` | 音楽 | Music |
| `KIDS` | キッズ | Kids &amp; Family |
| `PARENTING` | 子育て | Parenting |
| `NONFICTION` | ノンフィクション | Society &amp; Culture / Documentary |
| `ARTS` | アート | Arts |
| `FASHION` | ファッション | Arts / Fashion &amp; Beauty |
| `TECHNOLOGY` | テクノロジー | Technology |

## License

These codes are licensed under MIT License.
