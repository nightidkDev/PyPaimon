import datetime
import pymongo
import os
import discord
import time
import random
import sys
sys.path.append("../../")
import config 
from libs import Profile
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [["rtimely|rt", settimely, "all", "owner"]]

async def settimely(client, message, command, messageArray, lang_u):
    if str(message.author.id) not in config.ADMINS:
        return

    check = await Profile.Profile().check_member(message.guild, messageArray)

    user = check if len(message.mentions) == 0 else message.mentions[0]

    if user is None:
        return await message.channel.send('err member')

    users = db.prof_ec_users

    try:
        used = int(messageArray[1])
    except:
        return await message.channel.send("err timely count")
    if used <= 0: 
        return await message.channel.send("err timely count")

    users.update_one({ "disid": f"{user.id}", "guild": "604083589570625555" }, { "$set": { "timely_used": 0, "timely_count": used } })

    await message.channel.send(f"<@!{user.id}> был установлен счетчик ежедневных наград на {used} и сброшено выполнение сегодняшней команды.")
    


    

