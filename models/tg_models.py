from sqlalchemy import create_engine, MetaData, Column, String, Integer, Table, ForeignKey, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import func
from json import loads
import json
import sys
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
        Скрипт создает таблицы в базе данных для Telegram. Групп постов и статистики постов
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

    args = parser.parse_args()

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

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

def create_telegram_tables():
    engine = get_engine(args.sql_config_file)
    Channels_tg.__table__.create(engine)
    Messages_tg.__table__.create(engine)
    Reactions_tg.__table__.create(engine)

if __name__ == "__main__":
    create_telegram_tables()