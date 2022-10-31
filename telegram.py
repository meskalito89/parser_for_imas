from telethon import TelegramClient, connection
from sqlalchemy import MetaData, create_engine
import sqlalchemy
from json import loads
from pdb import set_trace



def get_telegram_client(telegram_conf_file: str):
    with open(telegram_conf_file) as config_file:
        config = loads(config_file.read())
        args = (config.get('username'), config.get('api_id'), config.get('api_hash'))
        client = TelegramClient(*args)
        return client

from models.telegram import create_telegram_tables

set_trace()

# client = get_telegram_client(".gitignore/telegram_conf.json")
# with client:
#     set_trace()

# def get_n_messages_from_channel(channel:[int|str], n:int) -> list:
#     with open()
#     with

# get_engine('.gitignore/sql_conf.json')
# data = ('@Don_Quijote2', '17678942', "552285c6ee4bc6009ed8bbe157ff54e8")


# with TelegramClient(*data) as client:
#     set_trace()
