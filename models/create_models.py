from sqlalchemy import Column, String, Integer, Table,\
    ForeignKey, DateTime, Text, create_engine, JSON
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import mysql
from pdb import set_trace
import json
import sys
import argparse

parser = argparse.ArgumentParser(description="""
    Скрипт создает таблицы для парсинга ВК. Группы, посты, и история постов.
   groups_vk,  posts_vk, reactions_vk
""")

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
    '--force',
    help="""Удаляет таблицы если они существуют""",
    action='store_true',
)

if __name__ == "__main__":
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


Base = declarative_base()

class Groups_vk(Base):
    __tablename__ = 'groups_vk'
    id = Column(mysql.BIGINT, primary_key=True)
    link = Column(String(50), nullable=False)

class Posts_vk(Base):
    __tablename__ = "posts_vk"
    id = Column(Integer, primary_key=True)
    owner_id = Column(mysql.BIGINT, ForeignKey('groups_vk.id'), primary_key=True)
    date = Column(mysql.BIGINT)
    from_id = Column(mysql.BIGINT)
    text = Column(Text)

class Reactions_vk(Base):
    __tablename__ = 'reactions_vk'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts_vk.id"))
    owner_id = Column(mysql.BIGINT, ForeignKey('posts_vk.owner_id'))
    comments = Column(Integer)
    likes = Column(Integer)
    reposts = Column(Integer)
    date = Column(DateTime(timezone=True), server_default=func.now())
    views = Column(Integer)

class Channels_tg(Base):
    __tablename__ = 'channels_tg'
    link = Column(String(50), primary_key=True, nullable=False)

class Messages_tg(Base):
    __tablename__ = 'messages_tg'
    id = Column(mysql.INTEGER(20), primary_key=True, nullable=False)
    channel_link = Column("channel_link", String(50), ForeignKey('channels_tg.link'), nullable=False, primary_key=True)
    pub_date = Column(DateTime)
    edit_date = Column(DateTime)
    message = Column(Text)

class Reactions_tg(Base):
    __tablename__ = 'reactions_tg'
    id = Column(Integer, primary_key=True)
    message_id = Column(mysql.INTEGER(20), ForeignKey('messages_tg.id'))
    channel_link = Column(String(50), ForeignKey("messages_tg.channel_link"))
    parse_date = Column(DateTime(timezone=True), server_default=func.now())
    reactions = Column(JSON)
    forward = Column(Integer)
    views = Column(Integer)

if __name__ == "__main__":
    engine = get_engine(args.sql_config_file)

    if args.force:
        for table in [Reactions_vk, Posts_vk, Groups_vk, Reactions_tg, Messages_tg, Channels_tg]:
            try:
                table.__table__.drop(engine)
            except OperationalError as error:
                continue

    Groups_vk.__table__.create(engine)
    Posts_vk.__table__.create(engine)
    Reactions_vk.__table__.create(engine)

    Channels_tg.__table__.create(engine)
    Messages_tg.__table__.create(engine)
    Reactions_tg.__table__.create(engine)

