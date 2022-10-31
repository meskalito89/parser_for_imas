from sqlalchemy import create_engine, MetaData, Column, String, Integer, Table, ForeignKey, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from json import loads


def get_engine(path_to_sql_conf_json='.gitignore/sql_conf.json') -> Engine:

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
        sql_conf = loads(sql_conf_file.read())
        url = "{database_type}://{username}:{password}@{server}:{port}/{database}".format(**sql_conf)
        engine = create_engine(url)
        return engine


Base = declarative_base()

class Channels(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True, nullable=False)
    link = Column(String(50), nullable=False)

class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, nullable=False)
    channel_id = Column("channel_id", Integer, ForeignKey('channels.id'), nullable=False, primary_key=True)
    pub_date = Column(DateTime)
    edit_date = Column(DateTime)
    message = Column(Text)


class Reactions(Base):
    __tablename__ = 'reactions'
    id = Column(Integer, primary_key=True, nullable=False)
    message_id = Column(Integer, ForeignKey('messages.id'))
    channel_id = Column(Integer, ForeignKey("messages.channel_id"))
    parse_date = Column(DateTime)
    reactions = Column(JSON)
    forward = Column(Integer)
    views = Column(Integer)


def create_telegram_tables():
    engine = get_engine()
    Channels.__table__.create(engine)
    Messages.__table__.create(engine)
    Reactions.__table__.create(engine)

if __name__ == "__main__":
    create_telegram_tables()