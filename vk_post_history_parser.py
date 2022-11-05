import vk_api
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models.create_models import VkPosts, VkReactions
from pdb import set_trace
from vk_api.execute import VkFunction
from vk_api.exceptions import VkToolsException
from vk_post_parser import get_vk_config, add_reaction_in_session
import argparse
import sys
import json


parser = argparse.ArgumentParser(description="""Этот парсер собирает статистику постов.
 Количество лайков, просмотров, и репостов.""")
parser.add_argument("--sql_query",
    help="""Запрос для выбора постов. По умолчанию select * from posts_vk;
    """,
    default="select * from posts_vk;"
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


args = parser.parse_args()


engine = get_engine(args.sql_config_file)
config = get_vk_config(args.vk_config_file)

def get_query_to_database(query):
    with Session(engine) as session:
        response = session.execute(query)
        return response.all()

def get_owner_id_post_id_for_sarch_method(query):
    all_posts = get_query_to_database(query)
    post_ids = [f"{str(post.owner_id)}_{str(post.id)}" for post in all_posts]
    return post_ids

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def get_post_by_owner_id_post_id(owner_id_post_id: list):
    """В вк каждый пост имеет уникальное значение 
    которое выглядит как номер группы нижнее подчеркивание номер поста
    Например 
    -1232123_3212321 """
    
    vkbot = vk_api.vk_api.VkApi(**config)
    for post_chank in chunker(owner_id_post_id, 100):
        chank = vkbot.method('wall.getById', values={'posts':",".join(post_chank)})
        yield chank

def save_reactions(posts):
    with Session(engine) as session:
        for post in posts:
            add_reaction_in_session(post, session)
        session.commit()
        
        

if __name__ == "__main__":

    owner_id_post_id = get_owner_id_post_id_for_sarch_method(args.sql_query)
    chanks = get_post_by_owner_id_post_id(owner_id_post_id)
    for chank in chanks:
        save_reactions(chank)
