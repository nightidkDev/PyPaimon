import datetime
import pymongo
import os
import discord
import time
import random
import sys
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [["updw", updw, "all", "owner"]]

async def updw(client, message, command, messageArray, lang_u):
    if str(message.author.id) not in config.ADMINS:
        return

    e = discord.Embed(title="", description=f"Запуск программы...", color=discord.Color(0x2F3136))
    e.timestamp = datetime.datetime.utcnow()
    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    mess = await message.channel.send(embed = e)

    e.description = "Очистка данных..."
    e.timestamp = datetime.datetime.utcnow()
    await mess.edit(embed=e)

    waifus = db.waifu.find({})
    for waifu in waifus:
        role = message.guild.get_role(int(waifu["id"]))
        for user in role.members:
            await user.remove_roles(role)

    e.description = "Очистка завершена."
    e.timestamp = datetime.datetime.utcnow()
    await mess.edit(embed=e)

    

    """
    users = db.prof_ec_users

    e.description = "Запрос данных..."
    e.timestamp = datetime.datetime.utcnow()
    await mess.edit(embed=e)

    usersinv = users.find({ "inv": { "$ne": [] } })

    e.description = f"Получено пользователей: {usersinv.count()}"
    e.timestamp = datetime.datetime.utcnow()
    await mess.edit(embed=e)

    a = 0
    b = 0

    e.description = f"Обновление пользователей... ({a}/{usersinv.count()})"
    e.timestamp = datetime.datetime.utcnow()
    await mess.edit(embed=e)

    for user in usersinv:
        if b == 10:
            e.description = f"Обновление пользователей... ({a}/{usersinv.count()})"
            e.timestamp = datetime.datetime.utcnow()
            await mess.edit(embed=e)
            b = 0
        items = user["inv"]
        new_items = []
        for item in items:
            if item["type"] == "waifu":
                new_items.append({ "type": item["type"], "id": item["id"], "equip": 0 })
            else:
                new_items.append(item)
        users.update_one({ "disid": user["disid"], "guild": user["guild"] }, { "$set": { "inv": new_items } })
        a += 1
        b += 1

    e.description = f"Обновление завершено."
    e.timestamp = datetime.datetime.utcnow()
    await mess.edit(embed=e)
    """
    
    


    

