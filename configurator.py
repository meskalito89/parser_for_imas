from json import loads
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import vk_api
from telethon.sync import TelegramClient
import argparse
from pdb import set_trace
from operator import itemgetter

parser = argparse.ArgumentParser(description="""Для парсинга необходимо указать настройки 
базы данных, а так же телеграмм и вк""")

# parser.add_argument("--sql_query",
#     help="""Запрос для выбора групп. По умолчанию select * from groups_vk;
#     """,
#     default="select * from groups_vk;",
#     )

parser.add_argument(
    "--sql_config_file",
    help="""Путь к файлу с настройками sql соединения json
    {
        "database_type": "mariadb",
        "server": "192.168.1.4",
        "port": 3306,
        "database": "social_network",
        "username": "username",
        "password": "password"
    }
    """,
    required=True
)

def read_config(path_to_config:str)->dict:
    with open(path_to_config) as config_file:
        return loads(config_file.read())

def get_engine(sql_config):
    """Creates database from scratch.
    sql_conf file should looks like
    {
        "database_type": "mariadb",
        "server": "192.168.1.4",
        "port": 3306,
        "database": "social_network",
        "username": "username",
        "password": "password"
    }
    """

    url = "{database_type}://{username}:{password}@{server}:{port}/{database}".format(**sql_config)
    engine = create_engine(url)
    return engine


args = parser.parse_args()
sql_config = read_config(args.sql_config_file)
engine = get_engine(sql_config)
sql_session = Session(engine)

