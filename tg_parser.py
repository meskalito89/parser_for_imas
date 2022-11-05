from sqlalchemy.orm import Session
from models.create_models import Messages_tg
from sqlalchemy import create_engine
from random import shuffle
from json import loads
import json
from pdb import set_trace
from telethon import sync
from pprint import pprint
import argparse


parser = argparse.ArgumentParser(description="""Этот парсер просматривает каналы из базы данных
 на наличие новых постов.""")
parser.add_argument(
    '-q',
    "--sql_query",
    help="""Запрос для выбора групп. По умолчанию select * from channels_tg;""",
    default="select * from channels_tg;",
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
    }
    """,
    )

parser.add_argument(
    '-c',
    "--sql_config_file",
    required=True,
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
)
parser.add_argument(
    '--limit',
    help="""Если в базе нет ни одного поста сканируемого канала,
    то limit задает сколько крайних постов нужно сохранить в базу.
    По умолчанию 10""",
    type=int,
    default=10
)

args = parser.parse_args()


def get_engine(path_to_sql_conf_json):

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

    with open(path_to_sql_conf_json) as sql_conf_file:
        sql_conf = json.loads(sql_conf_file.read())
        url = "{database_type}://{username}:{password}@{server}:{port}/{database}".format(**sql_conf)
        engine = create_engine(url)
        return engine


engine = get_engine(args.sql_config_file)

def execute_sql_request(sql_request):
    with Session(engine) as session:
        return session.execute(sql_request).all()

def get_telegram_client(telegram_conf_file:str):
    with open(telegram_conf_file) as config_file:
        config = loads(config_file.read())
        args = (config.get('username'), config.get('api_id'), config.get('api_hash'))
        client = sync.TelegramClient(*args)
        return client


client = get_telegram_client(args.tg_config_file)
def is_message_in_database(message, channel_link):
    message_dict = message.to_dict()
    id = message_dict.get("id")
    with Session(engine) as session:
        channels = session.query(Messages_tg).filter_by(channel_link=channel_link, id=id).all()
        if channels:
            return True
        return False


def get_last_messages_from_channel(channel_link, limit=args.limit):
    with client:
        messages = []
        try:
            iter_messages = client.iter_messages(channel_link, limit=limit)
            for message in iter_messages:
                if is_message_in_database(message, channel_link):
                    break
                messages.append(message)
            return messages
        except ValueError('Проверьте, существует ли канал {channel_link}') as err:
            print(err)
            return messages



def create_sqlalchemy_object_from_message(message, channel_link):
    message_dict = message.to_dict()
    sqlalchemy_message = Messages_tg(
        id=message_dict.get('id'),
        channel_link=channel_link,
        pub_date=message_dict.get('date'),
        edit_date=message_dict.get('edit_date'),
        message=message_dict.get('message')
    )
    return sqlalchemy_message

def save_messages(chank, channel_link):
    with Session(engine) as session:
        for message in chank:
            sqlalchemy_message = create_sqlalchemy_object_from_message(message, channel_link)
            session.add(sqlalchemy_message)
        session.commit()


if __name__ == "__main__":
    channels = execute_sql_request(args.sql_query)
    shuffle(channels)
    for channel in channels:
        last_messages_from_channel = get_last_messages_from_channel(channel.link)
        save_messages(last_messages_from_channel, channel.link)
