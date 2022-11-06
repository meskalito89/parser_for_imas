from create_models import TgChannels, TgMessages, TgReactions
# from sql_configurator import get_engine, read_config
# import telethon
# from operator import itemgetter
# from telethon.errors.rpcerrorlist import ChannelPrivateError
# from pdb import set_trace
# from random import shuffle


parser = argparse.ArgumentParser(description="""Parse telegram""")

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

args = parser.argparse()
tg_config = read_config(args.tg_config_file)
tg_client = telethon.sync.TelegramClient(*itemgetter('username', 'api_id', 'api_hash')(tg_config))
sql_config = read_config(args.sql_config_file)
engine = get_engine(sql_config)

class TgParser:
    def __init__(self, url: str, *args, **kwargs):
        self.url = url
        # self.id = self.get_self_id_by_database_request() or self.get_self_id_by_http_request()
        self.chank_size = kwargs.get("chank_size", 1)
        self.limit = kwargs.get("limit", 20)
        # self.post_iter = tg_client.iter_messages(self.url)
        
    def get_messages_from_database_filtered_by_url(self):
        with sql_session:
            all_messages_from_database_with_self_url = sql_session.query(TgMessages).filter_by(channel_link=self.url).all()
            return all_messages_from_database_with_self_url

    def get_all_messages_from_database(self):
        with sql_session:
            return sql_session.query(TgMessages).filter_by(owner_id=self.id).all()

    # def get_self_id_by_database_request(self):
    #     with sql_session:
    #         id = sql_session.query(TgChannels).filter_by(link=self.url).one().id
    #         return id

    # def get_self_id_by_http_request(self):
    #     group_name = self.url.split("/")[-1]
    #     response = tg_client.method("utils.resolveScreenName", {'screen_name': group_name})
    #     id = response.get("object_id", )*-1
    #     return id

    def message_dict_to_TgMessages(self, message_dict):
        
        new_message = TgMessages(
            id = message_dict.get('id'),
            channel_link = self.url,
            pub_date = message_dict.get('date'),
            edit_date = message_dict.get('edit_date'),
            message = message_dict.get('message')
        )

        return new_message
    
    def message_dict_to_TgReactions(self, message_dict):

        new_reaction = TgReactions(
            message_id = message_dict.get('id'),
            channel_link = self.url,
            reactions = message_dict.get("reactions"),
            forward = message_dict.get('forwards'),
            views = message_dict.get('views')
        )

        return new_reaction

    def is_message_in_database(self, message:dict):
        with sql_session:
            messges = self.get_messages_from_database_filtered_by_url()
            exist = sql_session.query(
                TgMessages.id, TgMessages.channel_link).filter_by(channel_link=message.get(''), id=message.get("id")
                ).all()
            if exist:
                return True
            return False

    def get_min_post_id_from_database(self):
        posts = self.get_messages_from_database_filtered_by_url()
        min_id = min([post.id for post in posts] or [1]) 
        return min_id

    def save_to_database(self, sqlalchemy_obj):
        with sql_session:
            sql_session.add(sqlalchemy_obj)
            sql_session.commit()
            print('saved ', self.url, sqlalchemy_obj.__tablename__)
        
    
    def scan_channels_first_time(self):
        with tg_client:
            message_iter = tg_client.iter_messages(self.url)
            for _ in range(self.limit):
                try: 
                    message = next(message_iter)
                except ChannelPrivateError as err:
                    continue
                except StopIteration as stop:
                    break
                message_dict = message.to_dict()
                new_message = self.message_dict_to_TgMessages(message_dict)
                new_reactions = self.message_dict_to_TgReactions(message_dict)
                self.save_to_database(new_message)
                self.save_to_database(new_reactions)

    def start(self):
        my_messages = self.get_messages_from_database_filtered_by_url()
        if not my_messages:
            self.scan_channels_first_time()
            return

        min_id = min(my_messages, key=lambda m: m.id) 
        max_id = max(my_messages, key=lambda m: m.id) 
        message_iter = tg_client.iter_messages(self.url, min_id=min_id)
        with tg_client:
            count = self.limit
            while True:
                try:
                    message = next(message_iter)
                except (ChannelPrivateError, TypeError):
                    break
                except StopIteration as stop:
                    break

                message_dict = message.to_dict()
                tg_message = self.message_dict_to_TgMessages(message_dict)
                tg_reactions = self.message_dict_to_TgReactions(message_dict)
                if max_id < tg_message.id:
                    self.save_to_database(tg_message)
                self.save_to_database(tg_reactions)
                if min_id >= tg_message.id:
                    break



if __name__ == "__main__":
    with sql_session:
        urls = [group.link for group in sql_session.query(TgChannels).all()]
        shuffle(urls)
        for url in urls:
            parser = TgParser(url)
            parser.start()