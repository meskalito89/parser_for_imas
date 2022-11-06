import argparse
from sqlalchemy.orm import Session
from create_models import VkGroups, TgChannels
from random import shuffle
from vkparser import VkParser
from tgparser import TgParser

parser = argparse.ArgumentParser(description="""Этот парсер просматривает каналы из базы данных
 на наличие новых постов.""")


parser.add_argument(
    '-s',
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

parser.add_argument(
    '-t',
    "--tg_config_file",
    required=True,
    help="""Путь к файлу с ipi_id, api_hash, username в формате json
    пример.\n
    {
        "api_id": api id,
        "api_hash": "api hash",
        "username": "@username"
    }>
    """,
)


args = parser.parse_args()
engine = get_engine(args.sql_config_file)

tg_config = read_config(args.tg_config_file)
tg_client = TelegramClient(*itemgetter('username', 'api_id', 'api_hash')(tg_config))

vk_config = read_config(args.vk_config_filekj)
vk_client = vk_api.VkApi(**vk_config)

if __name__ == "__main__":
    with Session(engine) as session:
        vk_links = session.query(VkGroups).all()
        shuffle(vk_link)
        for link in vk_links:
            VkParser(link).start()
        tg_links = sesson.query(TgChannels).all()
        shuffle(tg_links)
        for link in tg_links:
            TgParser(link).start()

        