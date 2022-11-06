## Набор скриптов для парсинга телеграмм каналов и групп вк.

Для работы нужны конфигурационные файлы:  
`conf.json`  
Файл вида  

```json
{
    "tg_conf_file": "Путь до файла конфигурации telegram",
    "vk_conf_file": "Путь до файла конфигурации vk",
    "sql_conf_file": "Путь до файла конфигурации sql соединения"
}
```
Располагается в текущей директории.


### Файл sql соединения
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

### Файл аутентификации telegram  
`tg_config.json`  
С данными авторизации вашего приложения telegram.   
```json

{
    "api_id":  "api_id",
    "api_hash": "api_hash", 
    "username": "@username"
}
```

### Файл аутентификации Vk  
`vk_conf.json`  
С данными авторизации Вк  
```json
{
    "token": "token",
    "login": "login",
    "password": "password"
}     
```

Файл `create_models.py`  создаст таблицы в базе данных.  

После создания таблиц, таблицы `tg_channels` и `vk_groups` заполняются вручную.  
Есть тестовый sql набор `database_fill.sql` там уже есть некоторое количество каналов и групп.  

В `channels_tg` нужно поместить ссылки на телеграм каналы которые будем парсить.  
В `groups_vk` нужно поместить ссылку на группу и id группы.  

После того как таблицы заполнены, запускаем скрипты `tgparser.py` и `vkparser.py`.  
Пример  
```shell
.venv/bin/python tgparser.py
``` 

```shell
.venv/bin/python vkparser.py
```  

Если канал парсится впервые то количество постов которые неоходимо собрать можно указать в параметре  
