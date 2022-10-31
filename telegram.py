from telethon import TelegramClient, connection
from pdb import set_trace

data = ('@Don_Quijote2', '17678942', "552285c6ee4bc6009ed8bbe157ff54e8")


with TelegramClient(*data) as client:
    set_trace()
