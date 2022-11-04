Набор скриптов для парсинга телеграмм каналов и групп вк.

Для работы нужны конфигурационные файлы:  
`sql_config.json`  
В котором находятся астройки подключения к базе данных.  
```json  
    {
        "database_type": "mariadb",
        "server": "192.168.1.4",
        "port": 3306,
        "database": "database",
        "username": "username",
        "password": "password"
    }
```
`tg_config.json`  
С данными авторизации вашего приложения telegram.   
```json

{
    "api_id":  "api_id",
    "api_hash": "api_hash", 
    "username": "@username"
}
```
`vk_conf.json`  
С данными авторизации Вк  
```json
{
    "token": "token",
    "login": "login",
    "password": "password"
}     
```

В директории models расположены скрипты для создания таблиц в базе данных  
`tg_models.py`  для создания таблиц связанных с парером telegram.  
`vk_models.py` для Vk.  
Для создания таблиц нужно запустить скрипт с соответствующими настройками.  
Пример  
```shell
./venv/bin/python .models/tg_models.py --sql_config_file path_to_sql_config_file
```  
```shell
./venv/bin/python .models/vk_models.py --sql_config_file path_to_sql_config_file
```  

После создания таблиц, таблицы `channels_tg` и `groups_vk` заполняются вручную.  
В channels_tg нужно поместить ссылки на телеграм каналы которые будем парсить.  
В groups_vk нужно поместить ссылку на группу и id группы.  

После того как таблицы заполнены, запускаем скрипты `tg_channels_parser.py` и `vk_post_parser.py`.  
Пример  
```shell
./venv/bin/python .models/tg_channel_parser.py --sql_config_file path_to_sql_config_file --tg_config_file path_to_tg_config_file
``` 

```shell
./venv/bin/python .models/vk_post_parser.py --sql_config_file path_to_sql_config_file --vk_config_file path_to_tg_config_file
```  
Если канал парсится впервые то количество постов которые неоходимо собрать можно указать в параметре  
`--limit`  
По умолчанию 10  
Если с канала или группы посты уже собирались, то скрипт будет собирать данные пока не наткнется на пост который уже есть в базе.  

Так-же у скрипта `tg_channel_parser.py` есть параметр `--sql_query`, который позволяет указать в виде sql запроса с какими каналами работает скрипт. По умолчанию `select * from channels_tg;`   

Для того чтобы отслеживать историю реакций (лайки, просмотры, репосты и т.д.) постов которые уже есть в базе, нужно запустить скрипты `tg_message_history_parser.py` и `vk_post_history_parser.py`  
Пример  
```shell
./venv/bin/python .models/tg_essage_history_parser.py --sql_config_file path_to_sql_config_file --tg_config_file path_to_tg_config_file
```  