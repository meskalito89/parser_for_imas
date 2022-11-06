from sqlalchemy import Column, String, Integer, Table,\
    ForeignKey, DateTime, Text, create_engine, JSON
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import mysql
from pdb import set_trace
from sql_configurator import engine
import argparse


Base = declarative_base()

class VkGroups(Base):
    __tablename__ = 'vk_groups'
    id = Column(mysql.BIGINT, primary_key=True)
    link = Column(String(50), nullable=False)

class VkPosts(Base):
    __tablename__ = "vk_posts"
    id = Column(Integer, primary_key=True)
    owner_id = Column(mysql.BIGINT, ForeignKey('vk_groups.id'), primary_key=True)
    date = Column(mysql.BIGINT)
    from_id = Column(mysql.BIGINT)
    text = Column(Text)

    def __str__(self):
        return f"tablename: {self.__tablename__}, owner: {self.owner_id}, date: {self.date}, text: {self.text[:15]}..."

class VkReactions(Base):
    __tablename__ = 'vk_reactions'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("vk_posts.id"))
    owner_id = Column(mysql.BIGINT, ForeignKey('vk_posts.owner_id'))
    comments = Column(Integer)
    likes = Column(Integer)
    reposts = Column(Integer)
    date = Column(DateTime(timezone=True), server_default=func.now())
    views = Column(Integer)

    def __str__(self):
        return f"tablename: {self.__tablename__}, id: {self.id}, resposts:{self.reposts}, date: {self.date} ..."

class TgChannels(Base):
    __tablename__ = 'tg_channels'
    link = Column(String(50), primary_key=True, nullable=False)

class TgMessages(Base):
    __tablename__ = 'tg_messages'
    id = Column(mysql.INTEGER(20), primary_key=True, nullable=False)
    channel_link = Column("channel_link", String(50), ForeignKey('tg_channels.link'), nullable=False, primary_key=True)
    pub_date = Column(DateTime)
    edit_date = Column(DateTime)
    message = Column(Text)

    def __str__(self):
        return f"table: {self.__tablename__}, id: {self.id}, channel_link: {self.channel_link}, publication_date: {self.pub_date}, message: {self.message}..."

class TgReactions(Base):
    __tablename__ = 'tg_reactions'
    id = Column(Integer, primary_key=True)
    message_id = Column(mysql.INTEGER(20), ForeignKey('tg_messages.id'))
    channel_link = Column(String(50), ForeignKey("tg_messages.channel_link"))
    parse_date = Column(DateTime(timezone=True), server_default=func.now())
    reactions = Column(JSON)
    forward = Column(Integer)
    views = Column(Integer)

    def __str__(self):
        return f"table: {self.__tablename__}, id: {self.id}, channel_link: {self.channel_link}, views: {self.views}, parse_date: {self.parse_date} ..."

if __name__ == "__main__":

    # set_trace()
    # if args.force:
    #     for table in [VkReactions, VkPosts, VkGroups, TgReactions, TgMessages, TgChannels]:
    #         try:
    #             table.__table__.drop(engine)
    #         except OperationalError as error:
    #             continue

    VkGroups.__table__.create(engine)
    VkPosts.__table__.create(engine)
    VkReactions.__table__.create(engine)

    TgChannels.__table__.create(engine)
    TgMessages.__table__.create(engine)
    TgReactions.__table__.create(engine)


