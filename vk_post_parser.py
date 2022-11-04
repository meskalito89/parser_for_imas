from models.vk_models import Groups_vk, Posts_vk, Reactions_vk
import sqlalchemy
from sqlalchemy import Column, String, Integer, Table, ForeignKey, DateTime, Text, create_engine
import vk_api
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

def get_todays_posts(channel_id):
    tools = vk_api.VkTools(vk_session)
    wall = tools.get_all_iter('wall.get', 10, {'owner_id': channel_id})
    posts = []
    for post in wall:
        if is_post_todays(post):
            posts.append(post)
            continue
        break
        
    return posts

def add_reaction_in_session(post, sql_session):
    new_reaction = Reactions_vk(
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
        posts = session.query(Posts_vk.owner_id).all()
        exist = session.query(
            Posts_vk.id, Posts_vk.owner_id).filter_by(owner_id=post.get('owner_id'), id=post.get("id")
            ).all()
        if exist:
            return True
        return False

def get_last_posts(channel_id, limit=args.limit):
    
    tools = vk_api.VkTools(vk_session)
    wall = tools.get_all_iter('wall.get', 10, {'owner_id': channel_id})
    posts = []
    for post in wall:
        if is_post_in_database(post) or len(posts)>=limit:
            break

        posts.append(post)
        continue
    return posts

def save_posts(posts:list[dict]) -> None:
    with Session(engine) as session:
        for post in posts:
            new_post = Posts_vk(
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
        


