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
               ["deltest", deltest, "all", "owner"]
           ]

async def deltest(client, message, command, messageArray, lang_u):
    counter = 0

    async for message in message.channel.history(limit=None):

        if message.author == client.user:
            counter += 1

    await message.channel.send(f"{counter}")


