from sqlalchemy import Column, String, Integer, Table, ForeignKey, DateTime, Text, create_engine
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import mysql
from json import loads
import argparse

parser = argparse.ArgumentParser(description="""
    Скрипт создает таблицы в базе данных для груп постов и статистики постов
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
    """
)

Base = declarative_base()

class Group(Base):
    __tablename__ = 'group'
    id = Column(mysql.BIGINT, primary_key=True)
    link = Column(String(50), nullable=False)

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    owner_id = Column(mysql.BIGINT, ForeignKey('group.id'), primary_key=True)
    date = Column(mysql.BIGINT)
    from_id = Column(mysql.BIGINT)
    text = Column(Text)

class Reaction_vk(Base):
    __tablename__ = 'reaction_vk'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("post.id"))
    owner_id = Column(mysql.BIGINT, ForeignKey('post.owner_id'))
    comments = Column(Integer)
    likes = Column(Integer)
    reposts = Column(Integer)
    date = Column(DateTime(timezone=True), server_default=func.now())
    views = Column(Integer)


if __name__ == "__main__":

    args = parser.parse_args()
    engine = create_engine(args.sql_config_file)
    engine = get_engine()
    Group.__table__.create(engine)
    Post.__table__.create(engine)
    Reaction_vk.__table__.create(engine)
