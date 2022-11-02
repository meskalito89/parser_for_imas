from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine
from json import loads

def get_engine(path_to_sql_conf_json) -> Engine:

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