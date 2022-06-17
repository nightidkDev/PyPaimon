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
               ["giveaway", giveaway, "all", "owner"]
           ]

async def giveaway(client, message, command, messageArray, lang_u):
    loading = client.get_emoji(794502101853798400)
    success = client.get_emoji(794502119600291861)
    error = client.get_emoji(794506211738648586)
    gwm = await message.guild.get_channel(789998005456863242).fetch_message(794111331685892116)
    reactions = gwm.reactions[0]
    users_w = await reactions.users().flatten()
    err_m = []
    e = discord.Embed(title="Розыгрыш", description=f"{loading} Поиск участника...", color=discord.Color(0x2F3136))
    msg = await message.channel.send(embed=e)
    while True:
        e1 = discord.Embed(title="Розыгрыш", description=f"{loading} Поиск участника...", color=discord.Color(0x2F3136))
        await msg.edit(embed=e1)
        await asyncio.sleep(5)
        win = random.choice(users_w)
        while win in err_m:
            win = random.choice(users_w)
        e2 = discord.Embed(title="Розыгрыш", description=f"{success} Поиск участника. (<@{win.id}>)\n{loading} Проверка статистики...", color=discord.Color(0x2F3136))
        await msg.edit(embed=e2)
        user = users_db.find_one({ "disid": f"{win.id}", "guild": f"{message.guild.id}" })
        await asyncio.sleep(5)
        if user["s_chat"] < 20 or int(time.time()) - int(win.joined_at.timestamp()) < 172800 or int(time.time()) - int(win.created_at.timestamp()) < 1209600:
            err2 = discord.Embed(title="Розыгрыш", description=f"{success} Поиск участника. (<@{win.id}>)\n{error} Проверка статистики.", color=discord.Color(0x2F3136))
            await msg.edit(embed=err2)
            err_m.append(win)
            await asyncio.sleep(5)
            continue
        e3 = discord.Embed(title="Розыгрыш", description=f"{success} Поиск участника. (<@{win.id}>)\n{success} Проверка статистики.\n{loading} Проверка участника в войсе...", color=discord.Color(0x2F3136))
        await msg.edit(embed=e3)
        await asyncio.sleep(5)
        if win.voice == None:
            err3 = discord.Embed(title="Розыгрыш", description=f"{success} Поиск участника. (<@{win.id}>)\n{success} Проверка статистики.\n{error} Проверка участника в войсе.", color=discord.Color(0x2F3136))
            await msg.edit(embed=err3)
            err_m.append(win)
            await asyncio.sleep(5)
            continue
        e4 = discord.Embed(title="Розыгрыш", description=f"{success} Поиск участника. (<@{win.id}>)\n{success} Проверка статистики.\n{success} Проверка участника в войсе.", color=discord.Color(0x2F3136))
        await msg.edit(embed=e4)
        res = discord.Embed(title="Итоги розыгрыша", description=f"Поздравляю, победил <@{win.id}>.", color=discord.Color(0x2F3136))
        await message.channel.send(embed=res)
        break


