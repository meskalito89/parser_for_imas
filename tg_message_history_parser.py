from classes.parser import get_engine

# from sqlalchemy.orm import Session
# from sqlalchemy import create_engine
# from models.create_models import TgMessages, Reactions_tg
# from tg_channel_parser import get_telegram_client
# from pdb import set_trace
# from random import shuffle
# import argparse
# import sys
# import json


# parser = argparse.ArgumentParser(description="""Этот парсер собирает статистику сообщений в канале.
#  Количество лайков, просмотров, и репостов.""")

# # parser.add_argument("--sql_query",
# #     help="""Запрос для выбора постов. По умолчанию select * from messages_tg;
# #     (В базе данных mysql слово group зарезервированно. Не забывайте включить его в апостроф `group`)
# #     """,
# #     default="select * from messages_tg;"
# #     )
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
    }>
    """,
)

tg_client = TelegramClient(*itemgetter('username', 'api_id', 'api_hash')(tg_config))
tg_config = read_config(args.tg_config_file)

# parser.add_argument(
#     '-t',
#     "--tg_config_file",
#     required=True,
#     help="""Путь к файлу с ipi_id, api_hash, username в формате json
#     пример.\n
#     {
#         "api_id": api id,
#         "api_hash": "api hash",
#         "username": "@username"
#     }
#     """,
#     )

# parser.add_argument(
#     '-c',
#     "--sql_config_file",
#     help="""Путь к файлу с настройками sql соединения json
#     {
#         "database_type": "mariadb",
#         "server": "192.168.1.4",
#         "port": 3306,
#         "database": "social_network",
#         "username": "username",
#         "password": "password"
#     }
#     """,
#     required=True
# )

# def get_engine(path_to_sql_conf_json):

#     """Creates database from scratch.
#     sql_conf file should looks like 
#     {
#         "database_type": "mariadb",
#         "server": "192.168.1.4",
#         "port": 3306,
#         "database": "social_network",
#         "username": "username",
#         "password": "password"
#     }
#     """
#     with open(path_to_sql_conf_json) as sql_conf_file:
#         sql_conf = json.loads(sql_conf_file.read())
#         url = "{database_type}://{username}:{password}@{server}:{port}/{database}".format(**sql_conf)
#         engine = create_engine(url)
#         return engine


# args = parser.parse_args()
# engine = get_engine(args.sql_config_file)
# client = get_telegram_client(args.tg_config_file)


# def send_sql_query(sql_query):
#     with Session(engine) as session:
#         result = session.execute(sql_query)
#         return result


# def extract_messages_by_channel_link(channel_link):
#     with Session(engine) as session:
#         messages = session.query(TgMessages).filter_by(channel_link=channel_link).all()
#         return messages


# def get_messages_from_cannel(channel_link, messages_id):
#     max_id = max(messages_id)
#     min_id = min(messages_id)
#     with client:
#         iter_messages = client.iter_messages(channel_link, max_id=max_id, min_id=min_id)
#         messages = list(iter_messages)
#         filtered_messages = filter(lambda message: message.id in messages_id, messages)
#         return list(filtered_messages)



# def iterate_over_messages_of_links():

#     links = send_sql_query('select link from channels_tg;')
#     # shuffle(links)
#     for link, in links:
#         messages = extract_messages_by_channel_link(link)
#         messages_id = [message.id for message in messages]
#         updated_messages = get_messages_from_cannel(link, messages_id)
#         reactions = [create_sqlalchemy_Reactions_from_message(message, link) for message in updated_messages]
#         # shuffle(reactions)
#         yield reactions

# def create_sqlalchemy_Reactions_from_message(message, link):
#     message_dict = message.to_dict()
#     atrs = dict(
#         message_id   = message_dict.get('id'),
#         channel_link = link,
#         forward      = message_dict.get("forwards"),
#         views        = message_dict.get('views')
#     )
#     reactions = message_dict.get("reactions")
#     if reactions:
#         atrs['reactions'] = reactions.get("results")

#     new_reaction = Reactions_tg(**atrs)
#     return new_reaction

# def save_chank_of_messages_to_db(chank):
#     with Session(engine) as session:
#         for reaction in chank:
#             session.add(reaction)
#         session.commit()


# if __name__ == "__main__":
#     for chanks_of_Reactions in iterate_over_messages_of_links():
#         save_chank_of_messages_to_db(chanks_of_Reactions)
