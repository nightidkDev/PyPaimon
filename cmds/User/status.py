import datetime
import pymongo
import os
import discord
import time
import random
import sys
import string
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
users = db.prof_ec_users

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}d {h:d}h {m:d}m {s:d}s"
    elif seconds >= 3600:
        return f"{h:d}h {m:d}m {s:d}s"
    elif seconds >= 60:
        return f"{m:d}m {s:d}s"
    else:
        return f"{s:d}s"

def init():
    return [
        ["status", status, "flood", "all"]
    ]

async def status(client, message, command, messageArray, lang_u):
    e = discord.Embed(color=discord.Colour(0x2F3136))
    e.set_author(name=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    e.timestamp = datetime.datetime.utcnow()
    user = users.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
    if len(messageArray) == 0:
        status = user["status"]
        e.description = f"{status if status != '' else 'Нет подписи'}"
        await message.channel.send(embed=e)
    else:
        if messageArray[0] == "set":
            if len(messageArray) >= 1:
                set_status = " ".join(messageArray[1:])
                set_status = set_status.replace("⠀", "")
                if set_status == "":
                    e.description = f"Укажите статус."
                    return await message.channel.send(embed=e)
                if len(set_status) > 32:
                    e.description = f"Укажите статус менее 32 символов."
                    return await message.channel.send(embed=e)
                rus = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
                for x in list(set_status):
                    if x not in string.printable and x not in rus:
                        e.description = f"В статусе присутствует недопустимый символ \"{x}\"."
                        return await message.channel.send(embed=e)
                users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$set": { "status": set_status } })
                e.description = f"Статус установлен."
                await message.channel.send(embed=e)
        elif messageArray[0] == "del" or messageArray[0] == "delete":
            users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$set": { "status": "" } })
            e.description = f"Статус удалён."
            await message.channel.send(embed=e)
        else:
            status = user["status"]
            e.description = f"{status if status != '' else 'Нет подписи'}"
            await message.channel.send(embed=e)

