import datetime
import pymongo
import os
import discord
import time
import re
import sys
sys.path.append("../../")
import config 
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [["allaccess", allaccess, "all", "owner"]]

async def allaccess(client, message, command, messageArray, lang_u):
    if message.author.id == 252378040024301570:
        coll = db.sb
        data = coll.find({"p": 0})
        if lang_u == "en":
            if data[0]["access"] == 1:
                coll.update({"p": 0}, {"$set": {"access": 0}})
                await message.channel.send("Access to emotion commands is prohibited on all servers except idk.")
            else:
                coll.update({"p": 0}, {"$set": {"access": 1}})
                await message.channel.send("Access to emotion commands is allowed on all servers")
        elif lang_u == "ru":
            if data[0]["access"] == 1:
                coll.update({"p": 0}, {"$set": {"access": 0}})
                await message.channel.send("Доступ к командам-эмоциям запрещен на всех серверах, кроме idk.")
            else:
                coll.update({"p": 0}, {"$set": {"access": 1}})
                await message.channel.send("Доступ к командам-эмоциям разрешен на всех серверах")