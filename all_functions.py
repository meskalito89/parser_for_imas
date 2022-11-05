from models.create_models import VkGroups, VkPosts, VkReactions
import sqlalchemy
from sqlalchemy import Column, String, Integer, Table, ForeignKey, DateTime, Text, create_engine
import vk_api
from vk_api.exceptions import VkToolsException
from sqlalchemy.orm import Session
from pdb import set_trace
from pprint import pprint
from datetime import datetime
from random import shuffle
import json
import argparse
import sys

parser = argparse.ArgumentParser(description="""Этот парсер просматривает каналы из базы данных
 на наличие новых постов.""")
parser.add_argument("--sql_query",
    help="""Запрос для выбора групп. По умолчанию select * from groups_vk;
    """,
    default="select * from groups_vk;",
    )
parser.add_argument("--vk_config_file",
    help="""Путь к файлу с токеном, логином и паролем от Вконтакте в формате json
    пример.\n
        {
            "token": "token",
            "login": "login",
            "password": "password"
        }
    """,
    required=True
    )
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
parser.add_argument(
    '--limit',
    help="""Если в базе нет ни одного поста сканируемой группы, 
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

if __name__ == "__main__":
    engine = get_engine(args.sql_config_file)

def get_vk_config(path_to_file):
    with open(path_to_file) as config_file:
        config = json.loads(config_file.read())
        return config

if __name__ == "__main__":
    config = get_vk_config(args.vk_config_file)
    vk_session = vk_api.VkApi(**config)
 
def convert_link_to_id(link):
    group_name = link.split("/")[-1]
    response = vk_session.method("utils.resolveScreenName", {'screen_name': group_name})
    result = response.get("object_id", )*-1
    return result

def is_post_todays(post):
    today = datetime.today()
    post_date = datetime.fromtimestamp(post.get('date'))
    if today.year == post_date.year and today.month == post_date.month and today.day == post_date.day:
        return True
    return False


def add_reaction_in_session(post, sql_session):
    new_reaction = VkReactions(
        post_id = post.get('id'),
        owner_id = post.get('owner_id'),
        likes = post.get('likes', dict()).get('count', 0),
        reposts = post.get('reposts', dict()).get('count', 0),
        views = post.get('views', dict()).get('count', 0),
        comments = post.get('comments', dict()).get('count', 0),
    )
    sql_session.add(new_reaction)

def get_all_posts_from_database():
    with Session(engine) as session:
        return session.query(Post).all()

def get_groups():
    with engine.connect() as conn:
        groups = conn.execute(args.sql_query)
        return list(groups)

def save_post(post):

    new_post = Post(
        id = post.get('id'),
        owner_id = post.get('owner_id'),
        date = post.get('date'),
        from_id = post.get('from_id'),
        text = post.get('text'),
    )

    with Session(engine) as session:
        try:
            session.add(new_post)
            session.commit()
        except sqlalchemy.exc.IntegrityError as err:
            session.rollback()
        
def is_post_in_database(post):
    with Session(engine) as session:
        posts = session.query(VkPosts.owner_id).all()
        exist = session.query(
            VkPosts.id, VkPosts.owner_id).filter_by(owner_id=post.get('owner_id'), id=post.get("id")
            ).all()
        if exist:
            return True
        return False

def get_last_posts(channel_id, limit=args.limit):
    tools = vk_api.VkTools(vk_session)
    posts = []
    chank_size = 10
    try:
        wall = tools.get_all_iter('wall.get', chank_size, {'owner_id': channel_id})
        for post in wall:
            if is_post_in_database(post) or len(posts)>=limit:
                break
            posts.append(post)
        
        return posts
    except VkToolsException as err:
        return posts
        


def save_posts(posts:list[dict]) -> None:
    with Session(engine) as session:
        for post in posts:
            new_post = VkPosts(
                id = post.get('id'),
                owner_id = post.get('owner_id'),
                date = post.get('date'),
                from_id = post.get('from_id'),
                text = post.get('text'),
            )
            session.add(new_post)
            add_reaction_in_session(post, session)

        session.commit()


if __name__ == '__main__':
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    groups = get_groups()
    shuffle(groups)
    for group in groups:
        posts = get_last_posts(group.id)
        save_posts(posts)
        


from sqlalchemy.orm import Session
from models.create_models import TgMessages
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
        channels = session.query(TgMessages).filter_by(channel_link=channel_link, id=id).all()
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
    sqlalchemy_message = TgMessages(
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