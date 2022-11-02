from sqlalchemy import create_engine, MetaData, Column, String, Integer, Table, ForeignKey, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.dialects import mysql
from json import loads
from models import get_engine


Base = declarative_base()

class Channels(Base):
    __tablename__ = 'channels'
    id = Column(mysql.BIGINT, primary_key=True, nullable=False)
    link = Column(String(50), nullable=False)

class Messages(Base):
    __tablename__ = 'messages'
    id = Column(mysql.INTEGER(20), primary_key=True, nullable=False)
    channel_id = Column("channel_id", mysql.BIGINT, ForeignKey('channels.id'), nullable=False, primary_key=True)
    pub_date = Column(DateTime)
    edit_date = Column(DateTime)
    message = Column(Text)


class Reactions(Base):
    __tablename__ = 'reactions'
    id = Column(mysql.INTEGER(20), primary_key=True, nullable=False)
    message_id = Column(mysql.INTEGER(20), ForeignKey('messages.id'))
    channel_id = Column(mysql.BIGINT, ForeignKey("messages.channel_id"))
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