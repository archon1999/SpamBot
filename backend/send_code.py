import os
import time

from pyrogram import Client

session_name = input()
api_id = input()
api_hash = input()
phone_number = input()
workdir = os.path.join(os.path.dirname(__file__), 'sessions')
client = Client(session_name,
                api_id,
                api_hash,
                workdir=workdir,
                phone_number=phone_number)

client.connect()
sent_code = client.send_code(client.phone_number)
print(sent_code.phone_code_hash)

time.sleep(30)

with open(os.path.join(workdir, session_name + '-code')) as file:
    phone_code = file.read().strip()

client.sign_in(client.phone_number,
               sent_code.phone_code_hash,
               phone_code)
