import datetime
import pymongo
import os
import discord
import time
import re
import sys
sys.path.append("../../")
import config 
import libs
from libs import DataBase
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

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
# 760873610528161812, 766390222979465237, 766390759095533610, 761771540181942273
def init():
    return [
                ["fire", staff().fire, "all", "G"],
                ["mwarn", staff().mwarn, "all", "mods"],
                ["munwarn", staff().munwarn, "all", "mods"],
                ["mwarns", staff().mwarns, "all", "mods"],
                ["ms|mstats", staff().ms, "all", "mods"]
           ]

class staff:

    def __init__(self):
        pass
    
    async def fire(self, client, message, command, messageArray, lang_u):
        log_channel = message.guild.get_channel(config.STAFF_CHAT)
        for role in message.author.roles:
            if (role.id == 760873610528161812 or role.id == 766390222979465237) or (role.id == 766390759095533610 or role.id == 761771540181942273):
                message.author.remove_roles(role)
        e = discord.Embed(title="Снятие: псж", description="Вы ушли с поста модерации!")
        await message.channel.send(embed=e)
        e = discord.Embed(title="Log: снятие", description=f"<@!{message.author.id}> ({message.author} | {message.author.id}) ушел по причине: псж")
        await log_channel.send(embed=e)

    async def mwarn(self, client, message, command, messageArray, lang_u):
        staff_role = message.guild.get_role(761771540181942273)
        staff_roles = [767084198816776262, 760218179447685142, 760873610528161812, 761771540181942273]
        staff = db.staff
        if len(messageArray) == 0 or messageArray[0] == "":
            e = discord.Embed(title="", description="Пользователь не найден.", color=discord.Colour(0x2F3136))
            return await message.channel.send(embed=e)
        if len(message.mentions) == 0:
            e = discord.Embed(title="", description="Пользователь не найден.", color=discord.Colour(0x2F3136))
            return await message.channel.send(embed=e)
        if staff.count_documents({"id": str(message.mentions[0].id)}) == 0 and staff_role in message.mentions[0].roles:
            DataBase.actions().insert(staff, "one", {"id": str(message.mentions[0].id), "time_staff": int(time.time()), "warns": 0, "mutes": 0, "bans": 0, "mwarns": [] })
        if staff.count_documents({"id": str(message.mentions[0].id)}) == 0:
            e = discord.Embed(title="", description="Этот пользователь не состоит в стаффе.", color=discord.Colour(0x2F3136))
            return await message.channel.send(embed=e)
        #if message.author.id == message.mentions[0].id:
        #    return await message.channel.send("Ты не можешь выдать варн себе.")
        #if message.guild.owner_id != message.author.id and message.mentions[0].top_role >= message.author.top_role:
        #    return await message.channel.send("Данный пользователь находится на одной роли с тобой или выше.")
        reason = ""
        user = DataBase.actions().find(staff, [{"id": str(message.mentions[0].id) }])[0]
        if len(messageArray) < 2:
            reason = "Не указана"
        else:
            for i in range(1, len(messageArray)):
                reason += f"{messageArray[i]} "
            reason = reason.strip(' ')
            if reason == "":
                reason = "Не указана"
        index = len(user["mwarns"])
        staff.update_one({"id": str(message.mentions[0].id)}, { "$push": { "mwarns": { "$each": [ { "index": index + 1, "admin": str(message.author.id), "reason": reason, "time": int(time.time() + 10800) } ] } } })
        desc = f"Модератор <@{str(message.mentions[0].id)}> получил варн. Сейчас у него {index + 1} из 3.\n──────────────────────────\nАдминистратор - <@{str(message.author.id)}>\nПричина: {reason}\n──────────────────────────"
        e = discord.Embed(title="", description="**" + desc + "**", color=discord.Colour(0x2F3136))
        await message.channel.send(embed=e)
        if index == 2:
            for role in message.mentions[0].roles:
                if role.id in staff_roles:
                    await message.mentions[0].remove_roles(role)
            #staff.delete_one({"id": str(message.mentions[0])})
            e2 = discord.Embed(title="Мод. преды: снятие с стаффа", description="Модератор получил 3 предупреждения и у него были сняты все стафф роли.", color=discord.Colour(0xff0000))
            return await message.channel.send(embed=e2)
    
    async def munwarn(self, client, message, command, messageArray, lang_u):
        staff_role = message.guild.get_role(761771540181942273)
        staff = db.staff
        if len(messageArray) == 0 or messageArray[0] == "":
            e = discord.Embed(title="", description="Пользователь не найден.", color=discord.Colour(0x2F3136))
            return await message.channel.send(embed=e)
        if len(message.mentions) == 0:
            e = discord.Embed(title="", description="Пользователь не найден.", color=discord.Colour(0x2F3136))
            return await message.channel.send(embed=e)
        if staff.count_documents({"id": str(message.mentions[0].id)}) == 0 and staff_role in message.mentions[0].roles:
            DataBase.actions().insert(staff, "one", {"id": str(message.mentions[0].id), "time_staff": int(time.time()), "warns": 0, "mutes": 0, "bans": 0, "mwarns": [] })
            e = discord.Embed(title="", description="Этот модератор не имеет предупреждений.", color=discord.Colour(0x2F3136))
            return await message.channel.send(embed=e)
        if staff.count_documents({"id": str(message.mentions[0].id)}) == 0:
            e = discord.Embed(title="", description="Этот пользователь не состоит в стаффе.", color=discord.Colour(0x2F3136))
            return await message.channel.send(embed=e)
        user = DataBase.actions().find(staff, [{"id": str(message.mentions[0].id) }])[0]
        index = len(user["mwarns"])
        if index == 0:
            e = discord.Embed(title="", description="Этот модератор не имеет предупреждений.", color=discord.Colour(0x2F3136))
            return await message.channel.send(embed=e)
        for elem in user["mwarns"]:
            if elem["index"] == index:
                reason = elem["reason"]
                time_warn = elem["time"]
                break
        staff.update_one({"id": str(message.mentions[0].id)}, { "$pop": { "mwarns": 1  } })
        desc = f"С модератора <@{str(message.mentions[0].id)}> снят варн. Сейчас у него {index - 1} из 3.\n──────────────────────────\nАдминистратор - <@{str(message.author.id)}>\n──────────────────────────\nПричина выдачи варна была: {reason}\nДата выдачи варна: {datetime.datetime.utcfromtimestamp(time_warn).strftime('%d.%m.%Y %H:%M:%S')}\n──────────────────────────"
        e = discord.Embed(title="", description="**" + desc + "**", color=discord.Colour(0x2F3136))
        await message.channel.send(embed=e)
        

    async def ms(self, client, message, command, messageArray, lang_u):
        staff = db.staff
        staff_role = message.guild.get_role(761771540181942273)
        if (len(messageArray) == 0 or messageArray[0] == "") or len(message.mentions) == 0:
            user = DataBase.actions().find(staff, [{"id": str(message.author.id)}])[0]
            if staff_role not in message.author.roles:
                return None
            if user == None and staff_role in message.author.roles:
                DataBase.actions().insert(staff, "one", {"id": str(message.author.id), "time_staff": int(time.time()), "warns": 0, "mutes": 0, "bans": 0, "mwarns": [] })
                user = DataBase.actions().find(staff, [{"id": str(message.author.id)}])[0]
            e = discord.Embed(title=f"Cтатистика модератора `{message.author}`", description="", color=discord.Colour(0x2F3136))
            e.set_thumbnail(url=f"{message.author.avatar_url}")
            e.add_field(name="Количество предупреждение модератора:", value=f"{len(user['mwarns'])}/3", inline=False)
            e.add_field(name="Сколько времени стоит в стаффе:", value=f"{seconds_to_hh_mm_ss(int(time.time()) - user['time_staff'])}", inline=False)
            e.add_field(name="Количество выданных наказаний:", value=f"{user['mutes']} mute(s)", inline=False)
            await message.channel.send(embed=e)
        else:
            user = DataBase.actions().find(staff, [{"id": str(message.mentions[0].id)}])[0]
            if staff_role not in message.mentions[0].roles:
                return None
            if user == None and staff_role in message.mentions[0].roles:
                DataBase.actions().insert(staff, "one", {"id": str(message.mentions[0].id), "time_staff": int(time.time()), "warns": 0, "mutes": 0, "bans": 0, "mwarns": [] })
                user = DataBase.actions().find(staff, [{"id": str(message.mentions[0].id)}])[0]
            e = discord.Embed(title=f"Cтатистика модератора `{message.mentions[0]}`", description="", color=discord.Colour(0x2F3136))
            e.set_thumbnail(url=f"{message.mentions[0].avatar_url}")
            e.add_field(name="Количество предупреждение модератора:", value=f"{len(user['mwarns'])}", inline=False)
            e.add_field(name="Сколько времени стоит в стаффе:", value=f"{seconds_to_hh_mm_ss(int(time.time()) - user['time_staff'])}", inline=False)
            e.add_field(name="Количество выданных наказаний:", value=f"{user['mutes']} mute(s)", inline=False)
            await message.channel.send(embed=e)

    async def mwarns(self, client, message, command, messageArray, lang_u):
        staff = db.staff
        staff_role = message.guild.get_role(761771540181942273)
        if (len(messageArray) == 0 or messageArray[0] == "") or len(message.mentions) == 0:
            user = DataBase.actions().find(staff, [{"id": str(message.author.id)}])[0]
            if staff_role not in message.author.roles:
                return None
            if user == None and staff_role in message.author.roles:
                DataBase.actions().insert(staff, "one", {"id": str(message.author.id), "time_staff": int(time.time()), "warns": 0, "mutes": 0, "bans": 0, "mwarns": [] })
                user = DataBase.actions().find(staff, [{"id": str(message.author.id)}])[0]
            warns_list = []
            for elem in user["mwarns"]:
                warns_list.append([elem["index"], elem["reason"], elem["admin"], elem["time"]])
            warns_list_str = ""
            for index, reason, admin, time_w in warns_list:
                warns_list_str += f"──────────────────────────\nIndex: {index}\nAdmin: <@!{admin}>\nReason: {reason}\nTime: {datetime.datetime.utcfromtimestamp(time_w).strftime('%d.%m.%Y %H:%M:%S')}\n"
            if warns_list == []:
                warns_list_str = "Нет предупреждений."
            e = discord.Embed(title=f"Предупреждния модератора `{message.author}`", description=f"**{warns_list_str}**", color=discord.Colour(0x2F3136))
            e.set_thumbnail(url=f"{message.author.avatar_url}")
            return await message.channel.send(embed=e)
        else:
            user = DataBase.actions().find(staff, [{"id": str(message.mentions[0].id)}])[0]
            if staff_role not in message.mentions[0].roles:
                return None
            if user == None and staff_role in message.mentions[0].roles:
                DataBase.actions().insert(staff, "one", {"id": str(message.mentions[0].id), "time_staff": int(time.time()), "warns": 0, "mutes": 0, "bans": 0, "mwarns": [] })
                user = DataBase.actions().find(staff, [{"id": str(message.mentions[0].id)}])[0]
            warns_list = []
            for elem in user["mwarns"]:
                warns_list.append([elem["index"], elem["reason"], elem["admin"], elem["time"]])
            warns_list_str = ""
            for index, reason, admin, time_w in warns_list:
                warns_list_str += f"──────────────────────────\nIndex: {index}\nAdmin: <@!{admin}>\nReason: {reason}\nTime: {datetime.datetime.utcfromtimestamp(time_w).strftime('%d.%m.%Y %H:%M:%S')}\n"
            if warns_list == []:
                warns_list_str = "Нет предупреждений."
            e = discord.Embed(title=f"Предупреждния модератора `{message.mentions[0]}`", description=f"**{warns_list_str}**", color=discord.Colour(0x2F3136))
            e.set_thumbnail(url=f"{message.mentions[0].avatar_url}")
            return await message.channel.send(embed=e)