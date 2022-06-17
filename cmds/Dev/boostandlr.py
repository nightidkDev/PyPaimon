import config
import datetime
import pymongo
import os
import discord
import time
import random
import sys
import asyncio
sys.path.append("../../")
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
users_db = db.prof_ec_users
rooms = db.love_rooms


def init():
    return [
        ["blr", blr().give, "all", "owner"]
    ]


class blr:

    async def give(self, client, message, command, messageArray, lang_u):
        loading = client.get_emoji(794502101853798400)
        success = client.get_emoji(794502119600291861)
        e = discord.Embed(title="", description="",
                          color=discord.Color(0x2F3136))
        e.description = """

Привет.

"""
        msg = await message.channel.send(embed=e)
        await asyncio.sleep(3)
        e.description = """

Запуск процесса...

"""
        await msg.edit(embed=e)
        await asyncio.sleep(5)
        e.description = f"""

Статус: Обработка... {loading}

"""
        await msg.edit(embed=e)
        for x in users_db.find({ "love_room": { "$ne": "" } }):
            if rooms.count_documents({ "owner2": x["disid"] }) != 0:
                continue 
            a = x["love_room_created"]
            b = x["love_room_created"]
            while b <= int(time.time()):
                b += 2592000
            rooms.insert_one({ "id": x["love_room"], "owner1": x["disid"], "owner2": x["partner"], "ctime": a, "ptime": b, "notify": "false", "payment": "false" })
        e.description = f"""

Статус: Команда выполнена. {success}

"""
        await msg.edit(embed=e)
