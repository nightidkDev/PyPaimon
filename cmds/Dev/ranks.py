import datetime
import pymongo
import os
import discord
import time
import random
import sys
import asyncio
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
users_db = db.prof_ec_users

def init():
    return [
               ["update_roles", ranks().give, "all", "owner"]
           ]

class ranks:

    async def give(self, client, message, command, messageArray, lang_u):
        loading = client.get_emoji(794502101853798400)
        success = client.get_emoji(794502119600291861)
        e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
        e.description = """

Привет.

"""
        msg = await message.channel.send(embed=e)
        await asyncio.sleep(3)
        e.description = """

Восстановление процесса, который не завершился...

"""
        await msg.edit(embed=e)
        await asyncio.sleep(3)
        #e.description = """

#Запуск процесса...

#"""
        #await msg.edit(embed=e)
        #await asyncio.sleep(5)
        #e.description = f"""

#Статус: Снятие всех ролей за уровень со всех пользователей.
#
#Стадии: 
#1. Снятие ролей: {loading}
#2. Выдача новых: {loading}

#"""
        #await msg.edit(embed=e)
        """
        await asyncio.sleep(2)
        ranks = config.ranks
        for x in message.guild.members:
            for rank in ranks:
                role = message.guild.get_role(int(rank[1]))
                if role in x.roles:
                    await x.remove_roles(role)
        """
        #e.description = f"""

#Статус: Снятие завершено, загружаю следующую стадию...

#Стадии: 
#1. Снятие ролей: {success}
#2. Выдача новых: {loading}

#"""
        #await msg.edit(embed=e)
        await asyncio.sleep(5)

        e.description = f"""

Статус: Выдача новых ролей за уровень.

Стадии: 
1. Снятие ролей: {success}
2. Выдача новых: {loading}

"""
        await msg.edit(embed=e)
        #await asyncio.sleep(2)
        users = db.prof_ec_users
        sdb = db.u_settings
        users_db = users.find({ "guild": f"{message.guild.id}", "view": "true" }).sort("lvl", -1)
        for x in users_db:
            try:
                if int(x["lvl"]) < 5:
                    continue
                member = message.guild.get_member(int(x["disid"]))
                #print(member)
                user_s = sdb.find_one({ "id": f"{member.id}", "guild": f"{member.guild.id}" })
                lvl_ins = int(x["lvl"])
                ranks = config.ranks
                for rank in ranks:
                    if lvl_ins >= rank[0]:
                        role_lvl = message.guild.get_role(int(rank[1]))
                        if user_s["role_lvl"] == 1:
                            if role_lvl not in member.roles:
                                await member.add_roles(role_lvl)
                        break
            except:
                continue

        e.description = f"""

Статус: Процесс завершен.

Стадии: 
1. Снятие ролей: {success}
2. Выдача новых: {success}

"""
        await msg.edit(embed=e)
        #await asyncio.sleep(2)
