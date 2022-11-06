from json import loads
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def read_config(path_to_config:str)->dict:
    with open(path_to_config) as config_file:
        return loads(config_file.read())

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



with open('conf.json') as file:
    configs = loads(file.read())
    path_to_sql_config = configs.get('sql_conf_file')
    sql_config = read_config(path_to_sql_config)
    engine = get_engine(sql_config)
    session = Session(engine)

