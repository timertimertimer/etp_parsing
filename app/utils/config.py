import csv
import os
from datetime import datetime, timedelta
from pathlib import PurePath, Path
from random import choice
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from .datetime_helper import DateTimeHelper

project_main_dir = PurePath(__file__).parent.parent

absolute_download_path = Path(
    os.getenv("ABSOLUTE_DOWNLOAD_PATH", Path(project_main_dir).joinpath("files"))
)
relative_download_path = Path(os.getenv("RELATIVE_DOWNLOAD_PATH", "/files"))

config_file_name = "config.ini"
proxy_file_name = "proxies.txt"
socks_file_name = "socks_5.txt"
user_agent_file_name = "user-agent.txt"
indexes_file_name = "index.json"
lot_classifiers_file_name = "lot_classifiers.csv"
data_path = project_main_dir / "data"
config_path = project_main_dir / config_file_name
indexes_path = data_path / indexes_file_name
proxy_path = data_path / proxy_file_name
socks5_proxy_path = data_path / socks_file_name
user_agent_path = data_path / user_agent_file_name
lot_classifiers_path = data_path / lot_classifiers_file_name
if Path(user_agent_path).exists():
    with open(f"{user_agent_path}", "r") as f:
        lines = f.readlines()
    user_agents = [i.replace("\\n", "").strip() for i in lines]
else:
    user_agents = []

default_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'

if Path(socks5_proxy_path).exists():
    with open(f"{socks5_proxy_path}", "r") as f:
        lines = f.readlines()
    socks5_proxies = [i.replace("\\n", "").strip() for i in lines]
else:
    socks5_proxies = []

lot_classifiers_name_to_code = dict()
lot_classifiers_code_to_name = dict()
with open(f"{lot_classifiers_path}", "r", encoding="utf-8-sig") as f:
    reader: csv.DictReader = csv.DictReader(f, delimiter=";")
    for row in reader:
        lot_classifiers_code_to_name[row["Код"]] = row["Наименование"]
        lot_classifiers_name_to_code[row["Наименование"]] = row["Код"]

env_path = Path(__file__).parent.parent.parent / ".env"


class ENV(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_path, env_file_encoding="utf-8", extra="allow"
    )

    yandex_api_key: Optional[str] = None
    dadata_api_token: Optional[str] = None
    dadata_api_secret: Optional[str] = None
    parser_secret: Optional[str] = None
    site_url: Optional[str] = None

    db_user: str = "etp_parsing"
    db_password: str = "strong_password"
    db_host: str = "localhost"
    db_port: int = 3306
    db_database: str = "etp_parsing"

    mysql_external_port: int = 3316

    retry_count: Optional[int] = 5


env = ENV()
env.connection_string = f"mysql+pymysql://{env.db_user}:{env.db_password}@{env.db_host}:{env.db_port}/{env.db_database}"

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Request": "1",
    "User-Agent": choice(user_agents),
}

image_formats = [
    ".jpeg",
    ".png",
    ".jpg",
    ".bmp",
    ".webp",
]
image_and_doc_formats = image_formats + [
    ".docx",
    ".doc",
    ".pdf",
    ".rtf",
]
archive_formats = [
    ".rar",
    ".zip",
    ".7z",
]
allowable_formats = image_and_doc_formats + archive_formats
trash_resources = [
    "image",
    "stylesheet",
    "audio",
    "font",
    # "xhr",
    "fetch",
    "eventsource",
    "websocket",
    "media",
    "ping",
]

default_days = days = 30
default_datetime_format = "%d.%m.%Y"
default_start_date = start_date = DateTimeHelper.format_datetime(
    datetime.now(DateTimeHelper.moscow_tz) - timedelta(days=days),
    default_datetime_format,
)
today = default_end_date = end_date = DateTimeHelper.format_datetime(
    datetime.now(), default_datetime_format
)

start_dates = {
    "akosta": start_date,
    "altimeta": start_date,
    "b2b_center": DateTimeHelper.format_datetime(
        datetime.now() - timedelta(days=7), default_datetime_format
    ),
    "bankrot_cdtrf": DateTimeHelper.format_datetime(
        datetime.now() - timedelta(days=3), default_datetime_format
    ),
    "electro_torgi": DateTimeHelper.format_datetime(
        datetime.now() - timedelta(days=default_days),
        f"{default_datetime_format} 00:01",
    ),
    "heveya": DateTimeHelper.format_datetime(
        datetime.now(DateTimeHelper.moscow_tz) - timedelta(days=7),
        default_datetime_format,
    ),
    "itender": DateTimeHelper.format_datetime(
        datetime.now() - timedelta(days=default_days), "%Y-%m-%d 0:0:-1"
    ),
    "lot_online_old": DateTimeHelper.format_datetime(
        datetime.now() - timedelta(days=default_days), "%d/%m/%Y"
    ),
    "lot_online_tender": DateTimeHelper.format_datetime(
        datetime.now() - timedelta(days=1), "%Y-%m-%d"
    ),
    "mets": DateTimeHelper.format_datetime(
        datetime.now() - timedelta(days=7), default_datetime_format
    ),
    "sberbank": DateTimeHelper.format_datetime(
        datetime.now(DateTimeHelper.moscow_tz) - timedelta(days=7), "%Y-%m-%d"
    ),
    "roseltorg": DateTimeHelper.format_datetime(
        datetime.now() - timedelta(days=1), default_datetime_format
    ),
    "zakupkigov": today,
}

download_files_from_get_url = True  # True - файлы качаются по GET запросу
unpack_archives = True
write_log_to_file = False
post_main_service = False
parse_fedresurs = False
