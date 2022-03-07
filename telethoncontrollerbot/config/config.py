import datetime
from pathlib import Path

from environs import Env

env = Env()
env.read_env()

TG_TOKEN = env.str("TG_TOKEN")
SHOP_ID = env.int("SHOP_ID")
YANDEX_API_KEY = env.str("YANDEX_API_KEY")
TEST = env.bool("TEST")

DB_USERNAME = env.str("DB_USERNAME")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")
DB_DB_NAME = env.str("DB_DB_NAME")

ADMINS = list(map(lambda x: int(x.strip()), env.list("ADMINS")))
TZ = datetime.timezone(datetime.timedelta(hours=3))
BASE_DIR = Path(__file__).parent.parent.parent

TEMP_DATA = {}
