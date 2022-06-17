import datetime
import pymongo
import os
import discord
import time
import re
import subprocess
import sys
import json
import asyncio
sys.path.append("../../")
import config 
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [
            ["restart", devs().restart, "all", "owner"],
            ["restartp", devs().restartp, "all", "owner"],
            ["react", devs().react, "all", "owner"],
            ["creact", devs().creact, "all", "owner"],
            ["fv", devs().fixview, "all", "owner"]
           ]

class devs:
    def __init__(self):
        pass

    async def fixview(self, client, message, command, messageArray, lang_u):
        users = db.prof_ec_users
        if len(messageArray) == 1:
            flagu = users.find_one({ "disid": f"{messageArray[0]}", "guild": f"{message.guild.id}" })["view"]
            e = discord.Embed(title='', description=f"У пользователя <@!{messageArray[0]}> флаг \"view\": {flagu}", color=discord.Color(0x2F3136))
            e.set_author(name='Просмотр флага \"view\" в базе данных')
            await message.channel.send(embed=e)
        else:
            users.update_one({ "disid": f"{messageArray[0]}", "guild": f"{message.guild.id}" }, { "$set": { "view": f"{messageArray[1]}" } })
            e = discord.Embed(title='', description=f"У пользователя <@!{messageArray[0]}> установлен флаг \"view\": {messageArray[1]}", color=discord.Color(0x2F3136))
            e.set_author(name='Изменение флага \"view\" в базе данных')
            await message.channel.send(embed=e)

    async def restart(self, client, message, command, messageArray, lang_u):
        config.restart = 1
        d = None
        with open("restart_info.json", "r") as ri:
            d = json.load(ri)
        d["restart"] = int(time.time())
        with open("restart_info.json", "w") as ri:
            json.dump(d, ri)
        e = discord.Embed(title="", description="Ожидание завершения всех реакций...", color=discord.Colour(0xff0000))
        e.set_footer(text="Принудительная перезагрузка через 30 секунд.")
        restart_message = await message.channel.send(embed=e)
        time_restart = int(time.time()) + 30
        react = db.reactions.count_documents({})
        react_l = None
        while react != 0:
            if time_restart <= int(time.time()):
                break
            react = db.reactions.count_documents({})
            if react == 0:
                break
            react_l = db.reactions.find_one({})
            try:
                if await client.get_channel(int(react_l["channel_id"])).fetch_message(int(react_l["message_id"])) == None:
                    db.reactions.delete_one({ "message_id": react_l["message_id"] })
            except:
                db.reactions.delete_one({ "message_id": react_l["message_id"] })
            await asyncio.sleep(1)
        e2 = discord.Embed(title="", description="Перезагрузка...", color=discord.Colour(0xff0000))
        await restart_message.edit(embed=e2)
        with open("restart_info.json", "r") as ri:
            d = json.load(ri)
        d["restart_channel"] = message.channel.id
        d["restart_message"] = restart_message.id
        d["restarted_by"] = message.author.id
        with open("restart_info.json", "w") as ri:
            json.dump(d, ri)
        os.system("pm2 restart paimon_func")
        os.system("pm2 restart paimon_func2")
        os.system("pm2 restart paimon_dfunc")
        os.system("pm2 restart paimon_main")

    async def restartp(self, client, message, command, messageArray, lang_u):
        e = discord.Embed(title="PRIVATES RESTART", description="Бот с приватками был перезапущен.", color=discord.Colour(0xff0000))
        await message.channel.send(embed=e)
        os.system("pm2 restart klee")

            
    async def stop(self, client, message, command, messageArray, lang_u):
        e = discord.Embed(title="", description="Stopped.", color=discord.Colour(0xff0000))
        await message.channel.send(embed=e)
        os.system("pm2 stop paimon_react")
        os.system("pm2 stop paimon_func")
        os.system("pm2 stop paimon_func2")
        os.system("pm2 stop paimon_dfunc")
        os.system("pm2 stop paimon_clans")
        os.system("pm2 stop paimon_main")

    async def react(self, client, message, command, messageArray, lang_u):
        m = await message.channel.fetch_message(int(messageArray[0]))
        await m.add_reaction(client.get_emoji(int(messageArray[1])))

    async def creact(self, client, message, command, messageArray, lang_u):
        m = await message.channel.fetch_message(int(messageArray[0]))
        await m.clear_reactions()