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

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}d {h:d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:d}:{s:02d}"

def init():
    return [
                ["warn", warns().warn, "all", "mods"],
                ["unwarn", warns().unwarn, "all", "mods"],
                ["clear_warns", warns().cw, "all", "mods"],
                ["warns", warns().warns, "all", "mods"]
           ]

class warns:

    def __init__(self):
        pass
    
    async def warn(self, client, message, command, messageArray, lang_u):
        emoji_1 = client.get_emoji(780831508600062003)
        emoji_2 = client.get_emoji(794180012299124737)
        coll = db.prof_ec_users
        e = discord.Embed(title=f"{emoji_1} {emoji_2} ♡ Выдача предупреждения", description="", color=discord.Colour(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        if len(messageArray) == 0 or messageArray[0] == "":
            e.description = f"Участник не найден."
            return await message.channel.send(embed=e)
        else:
            if len(message.mentions) != 0:
                if coll.count_documents({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}) == 0:
                    e.description = f"Участник не найден."
                    return await message.channel.send(embed=e)
                else:
                    if message.author.id == message.mentions[0].id:
                        e.description = f"Ты не можешь выдать предупреждение себе."
                        return await message.channel.send(embed=e)
                    if message.guild.owner_id != message.author.id and message.mentions[0].top_role >= message.author.top_role:
                        e.description = f"Данный пользователь находится на одной роли с тобой или выше."
                        return await message.channel.send(embed=e)
                    coll11 = db.mutes
                    data11 = coll11.find({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" })
                    if coll11.count_documents({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" }) == 1:
                        time_now = int(time.time())
                        left_t = int(data11[0]['time_mute']) - time_now
                        return await message.channel.send(f"Этот пользователь уже имеет мут. Осталось: {seconds_to_hh_mm_ss(left_t)}")
                    reason = ""
                    user = coll.find_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id) })
                    if len(messageArray) < 2:
                        reason = "Не указана"
                    else:
                        for i in range(1, len(messageArray)):
                            reason += f"{messageArray[i]} "
                        reason.strip()
                        if reason == "":
                            reason = "Не указана"
                    reason = reason.strip()
                    index = len(user["warns"])
                    index_system = user["warns_counter_system"]
                    warn_info = { 
                        "index": index + 1, 
                        "mod": str(message.author.id), 
                        "reason": reason, 
                        "time": int(time.time() + 10800) 
                    }
                    coll.update_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}, { "$push": { "warns": { "$each": [ warn_info ] }, "history_warns": { "$each": [ warn_info ] } } })
                    coll.update_one({ "disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" }, { "$inc": { "warns_counter_system": 1 } })
                    e.description = f"Участник <@!{message.mentions[0].id}> получил предупреждение #{index + 1}, причина: **{reason}**."
                    if index + 1 >= 3:
                        warn_roles = [876711190091423816, 876714788732952637, 876771661628731432]
                        if index_system + 1 == 3:
                            warn1 = message.guild.get_role(warn_roles[0])
                            await message.author.add_roles(warn1)
                        elif index_system + 1 == 6:
                            warn2 = message.guild.get_role(warn_roles[1])
                            await message.author.add_roles(warn2)
                        elif index_system + 1 == 9:
                            warn3 = message.guild.get_role(warn_roles[2])
                            await message.author.add_roles(warn3)
                        servers = db.server
                        role_id = servers.find_one({"server": str(message.guild.id)})["roleid_mute"]
                        rb = message.guild.get_role(int(role_id))
                        rb_db = db.mutes
                        x = int(time.time())
                        if index_system == 3:
                            xn = x + 43200
                            mute_text = "12 часов"
                        elif index_system == 6:
                            xn = x + 86400
                            mute_text = "24 часа"
                        elif index_system >= 9:
                            xn = x + 172800
                            mute_text = "2 дня"
                        rb_db.insert_one({"disid": str(message.mentions[0].id), "time_mute": str(xn), "guild": str(message.guild.id), "mod": str(message.author.id), "roleid": str(rb.id), "reason": "Авто-мут 3/3 предупреждений."})
                        users = db.prof_ec_users
                        users.update_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}, { "$set": { "warns": [] } })
                        #vrole = message.guild.get_role(767025328405086218)
                        #await message.mentions[0].remove_roles(vrole)
                        await message.mentions[0].add_roles(rb, reason="Warns 3/3")
                        e.description = f"Участник <@!{message.mentions[0].id}> получил предупреждение #{index + 1} из 3 возможных, за это ему была выдана роль <@&{rb.id}>. Она будет снята через `🕒` {mute_text}. \nПричина: **{reason}**."
                        if message.mentions[0].voice is not None:
                            voice_m = message.mentions[0].voice.channel
                            await message.mentions[0].edit(voice_channel=voice_m, reason="muted.")
                    await message.channel.send(embed=e)
                    try:
                        await message.mentions[0].send(embed=e)
                    except:
                        await message.guild.get_channel(766390214267764786).send(content=f"<@!{message.mentions[0].id}>", embed=e)
                    #await message.guild.get_channel(803664955306934372).send(embed=e)
            else:
                e.description = f"Участник не найден."
                return await message.channel.send(embed=e)
                        

    async def unwarn(self, client, message, command, messageArray, lang_u):
        emoji_1 = client.get_emoji(780831508600062003)
        emoji_2 = client.get_emoji(794180012299124737)
        e = discord.Embed(title=f"{emoji_1} {emoji_2} ♡ Снятие предупреждения", description="", color=discord.Colour(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        coll = db.prof_ec_users
        if len(messageArray) == 0 or messageArray[0] == "":
            e.description = f"Участник не найден."
            return await message.channel.send(embed=e)
        else:
            if len(message.mentions) != 0:
                if coll.count_documents({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}) == 0:
                    e.description = f"Участник не найден."
                    return await message.channel.send(embed=e)
                else:
                    if message.author.id == message.mentions[0].id:
                        e.description = f"Ты не можешь снять предупреждение себе."
                        return await message.channel.send(embed=e)
                    if message.guild.owner_id != message.author.id and message.mentions[0].top_role >= message.author.top_role:
                        e.description = f"Данный пользователь находится на одной роли с тобой или выше."
                        return await message.channel.send(embed=e)
                    user = coll.find_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id) })
                    if len(user["warns"]) == 0:
                        e.description = f"У участника не обнаружено предупреждений."
                        return await message.channel.send(embed=e)
                    coll.update_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}, { "$pop": { "warns": 1 } })
                    e.description = f"Предупреждение с <@!{message.mentions[0].id}> было снято, теперь у него {len(user['warns']) - 1}/3."
                    await message.channel.send(embed=e)
                    try:
                        await message.mentions[0].send(embed=e)
                    except:
                        await message.guild.get_channel(766390214267764786).send(content=f"<@!{message.mentions[0].id}>", embed=e)
            else:
                e.description = f"Участник не найден."
                return await message.channel.send(embed=e)

    async def cw(self, client, message, command, messageArray, lang_u):
        if str(message.author.id) not in config.ADMINS:
            return None
        coll = db.prof_ec_users
        if len(messageArray) == 0 or messageArray[0] == "":
            return await message.channel.send("unknown member")
        else:
            if len(message.mentions) != 0:
                if coll.count_documents({"disid": str(message.mentions[0].id), "guild": str(message.guild.id) }) == 0:
                    return await message.channel.send("unknown member")
                else:
                    coll.update_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}, { "$set": { "warns": [] } })
    
    async def warns(self, client, message, command, messageArray, lang_u):
        emoji_1 = client.get_emoji(780831508600062003)
        emoji_2 = client.get_emoji(794180012299124737)
        e = discord.Embed(title=f"", description="", color=discord.Colour(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        coll = db.prof_ec_users
        if len(messageArray) == 0 or messageArray[0] == "":
            user = coll.find_one({"disid": str(message.author.id), "guild": str(message.guild.id) })
            warns = ''
            for elem in user["warns"]:
                index = elem["index"]
                mod = elem["mod"]
                reason = elem["reason"]
                time_w = elem["time"]
                warns += f"#{index}. Выдано предупреждение от <@!{mod}> в {datetime.datetime.utcfromtimestamp(time_w).strftime('%d.%m.%Y %H:%M:%S')} с причиной: {reason}\n"
            if warns == "":
                warns = "Предупреждений не найдено."
            e.description = warns
            e.title = f"{emoji_1} {emoji_2} ♡ Предупреждения `{message.author}`"
            await message.channel.send(embed=e)
        else:
            if len(message.mentions) != 0:
                if db.prof_ec_users.count_documents({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}) == 0:
                    e.description = f"Участник не найден."
                    return await message.channel.send(embed=e)
                user = coll.find_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id) })
                warns = ''
                for elem in user["warns"]:
                    index = elem["index"]
                    mod = elem["mod"]
                    reason = elem["reason"]
                    time_w = elem["time"]
                    warns += f"#{index}. Выдано предупреждение от <@!{mod}> в {datetime.datetime.utcfromtimestamp(time_w).strftime('%d.%m.%Y %H:%M:%S')} с причиной: {reason}\n"
                if warns == "":
                    warns = "Предупреждений не найдено."
                e.description = warns
                e.title = f"{emoji_1} {emoji_2} ♡ Предупреждения `{message.mentions[0]}`"
                await message.channel.send(embed=e)