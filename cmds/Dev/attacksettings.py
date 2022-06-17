import datetime
import pymongo
import os
import discord
import time
import random
import asyncio
import sys
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
users_db = db.prof_ec_users

def init():
    return [
               ["attack", attacks, "all", "owner"]
           ]

async def attacks(client, message, command, messageArray, lang_u):

    server = db.server

    attackSetting = server.find_one({ "server": "604083589570625555" })["attackSetting"]

    server.update_one({ "server": "604083589570625555" }, { "$set": { "attackSetting": 0 if attackSetting == 1 else 1 } })

    await message.channel.send("Отключено" if attackSetting == 1 else "Включено")


