from sqlalchemy import Column, String, Integer, Table, ForeignKey, DateTime, Text, create_engine
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import mysql
from json import loads
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

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

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

if __name__ == "__main__":
    args = parser.parse_args()
    engine = create_engine(args.sql_config_file)
    engine = get_engine()
    Groups_vk.__table__.create(engine)
    Posts_vk.__table__.create(engine)
    Reaction_vk.__table__.create(engine)

