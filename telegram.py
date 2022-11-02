from telethon import TelegramClient, connection, utils, events
from telethon.tl.functions.channels import JoinChannelRequest
from models.telegram_models import get_engine
from sqlalchemy.orm import Session
from models.telegram_models import Channels, Reactions, Messages
import sqlalchemy
from json import loads
from pdb import set_trace
import asyncio
from pprint import pprint
import datetime


telegram_conf_file = ".gitignore/telegram_conf.json"
engine = get_engine()

def get_telegram_links():
    with Session(engine) as session:
        return [channel.link for channel in session.query(Channels).all()]

def get_telegram_client(telegram_conf_file:str=telegram_conf_file):
    with open(telegram_conf_file) as config_file:
        config = loads(config_file.read())
        args = (config.get('username'), config.get('api_id'), config.get('api_hash'))
        client = TelegramClient(*args)
        return client


client = get_telegram_client()


async def get_last_n_messages_from_channel(channel, n, *args, **kwargs):
    async with client:
        messages = []
        async for message in client.iter_messages(channel, n):
            messages.append(message)
        return list(messages)


async def get_messages_at_date(chat, date):
    result = []
    tomorrow = date + datetime.timedelta(days=1)
    async for msg in client.iter_messages(chat, offset_date=date):
        if msg.date < date:
            return result
        result.append(msg)

async def get_messages_for_the_last_24_hour_from_now(chat):
    day_before = datetime.datetime.now() + datetime.timedelta(days=1)
    messages = []

    async for message in client.iter_messages(chat, offset_date=day_before):
        messages.append(message)
        set_trace()

    return messages


# async def get_entities():
#     entities = []
#     async with client:

#         async with open('channels.txt') as channels:
#             channel_links = channels.read().splitlines()

#         async for link in channel_links:
#             await client(JoinChannelRequest(link))
#             entities.append(client.get_entity(link))

#     return entities

# def get_links():
#     with open("channels.txt") as file:
#         return file.read().splitlines()
        
@client.on(events.NewMessage(chats=("https://t.me/vyezd_v_kazahstan")))
async def f(event):
    print(event)
    print("\a")

    
if __name__ == '__main__':
    with client:
        client.run_until_disconnected()

