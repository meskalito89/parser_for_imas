from json import loads
from pdb import set_trace
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

SQL_CONFIG_PATH = "/etc/imas_parser.conf/my_server_database_conf.json"



def read_config(path_to_config:str)->dict:
    with open(path_to_config) as config_file:
        return loads(config_file.read())

sql_config = read_config(SQL_CONFIG_PATH)
vk_config = dict()
tg_config = dict()

def get_engine(sql_config):
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

    url = "{database_type}://{username}:{password}@{server}:{port}/{database}".format(**sql_config)
    engine = create_engine(url)
    return engine

engine = get_engine(sql_config)
session = Session(engine)


# with session:
#     response = session.execute('select * from ')






class Parser:
    def __init__(self, url: str, *args, **kwargs):
        self.ufl = url
        self.sql_request = kwargs.get('sql_request', None)
        
    
    def get_messages_from_database(self):
        if self.sql_request:
            pass
