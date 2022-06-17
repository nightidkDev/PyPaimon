import datetime
import pymongo
import os
import discord
import time
import re
import sys
sys.path.append("../../")
import config 
from libs import DataBase
from libs import Profile
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

def declension(forms, val):
    cases = [ 2, 0, 1, 1, 1, 2 ]
    if val % 100 > 4 and val % 100 < 20:
        return forms[2]
    else:
        if val % 10 < 5:
            return forms[cases[val % 10]]
        else:
            return forms[cases[5]]

def get_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    if days != 0:
        return f"{days} {declension([ 'день', 'дня', 'дней' ], days)}, {hours} {declension([ 'час', 'часа', 'часов' ], hours)}, {minutes} {declension([ 'минута', 'минуты', 'минут' ], minutes)}"
    else:
        if hours != 0:
            return f"{hours} {declension([ 'час', 'часа', 'часов' ], hours)}, {minutes} {declension([ 'минута', 'минуты', 'минут' ], minutes)}"
        else:
            return f"{minutes} {declension([ 'минута', 'минуты', 'минут' ], minutes)}"


def init():
    return [
                ["mute", moderation().mute, "all", "mods"], 
                ["unmute", moderation().unmute, "all", "mods"],
                ["clear", moderation().clear, "all", "admins"],
                ["slowmode|sm", moderation().slowmode, "all", "admins"],
                ["ban", moderation().ban, "all", "sadmins"],
                ["unban", moderation().unban, "all", "mods"],
           ]

class moderation:
    def __init__(self):
        pass
    
    async def ban(self, client, message, command, messageArray, lang_u):
        check = await Profile.Profile().check_member(message.guild, messageArray)
        user = message.mentions[0] if len(message.mentions) != 0 else check if check else None
        if not user:
            e = discord.Embed(title="", description="Участник не найден.", color=discord.Colour(0x2f3136))
            e.set_footer(text=f"{message.author.name}", icon_url=message.author.avatar_url)
            e.set_author(name="Бан участника")
            e.timestamp = datetime.datetime.utcnow()
            await message.channel.send(embed=e)
        else:
            if user == message.author:
                e = discord.Embed(title="", description="Не бань себя!", color=discord.Colour(0x2f3136))
                e.set_footer(text=f"{message.author.name}", icon_url=message.author.avatar_url)
                e.set_author(name="Бан участника")
                e.timestamp = datetime.datetime.utcnow()
                await message.channel.send(embed=e)
            elif message.guild.owner_id == user.id:
                e = discord.Embed(title="", description="Невозможно забанить владельца сервера.", color=discord.Colour(0x2f3136))
                e.set_footer(text=f"{message.author.name}", icon_url=message.author.avatar_url)
                e.set_author(name="Бан участника")
                e.timestamp = datetime.datetime.utcnow()
                await message.channel.send(embed=e)
            elif message.guild.owner_id != message.author.id and user.top_role >= message.author.top_role:
                e = discord.Embed(title="", description="Невозможно забанить человека вышестоящего по роли.", color=discord.Colour(0x2f3136))
                e.set_footer(text=f"{message.author.name}", icon_url=message.author.avatar_url)
                e.set_author(name="Бан участника")
                e.timestamp = datetime.datetime.utcnow()
                await message.channel.send(embed=e)
            else:
                reason = " ".join(messageArray[1:]) 
                if not reason:
                    reason = "Не указана"
                e = discord.Embed(title="", description="", color=discord.Colour(0x2f3136))
                e.description = f"Участник <@!{message.mentions[0].id}> получил бан от <@!{message.author.id}> \nПричина: **{reason}**."
                e.set_author(name="Бан участника")
                e.set_footer(text=f"{message.author.name}", icon_url=message.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                await message.channel.send(embed=e)
                await message.guild.ban(user=user, reason=reason)

    async def unban(self, client, message, command, messageArray, lang_u):
        if str(message.author.id) not in config.ADMINS:
            return None

    async def mute(self, client, message, command, messageArray, lang_u):
        if message.guild.id == 604083589570625555:
            channel_log = message.guild.get_channel(config.log_channel)
        if lang_u == "en":
            if len(messageArray) == 0:
                #print("1")
                return await message.channel.send("Specify the person to mute.")
            try:
                if len(message.mentions) == 0 and message.guild.get_member(int(messageArray[0])) == None:
                    #print("2")
                    #print(messageArray[0])
                    #print(message.mentions)
                    #print(message.guild.get_member(messageArray[0]))
                    return await message.channel.send("Specify the person to mute.")
            except:
                return await message.channel.send("Specify the person to mute.")
            coll = db.mutes
            data11 = coll.find({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}"})
            if coll.count_documents({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" }) == 1:
                time_now = int(time.time())
                left_t = int(data11[0]["time_mute"]) - time_now
                return await message.channel.send(f"This user already has mute. Time left: {seconds_to_hh_mm_ss(left_t)}")
            if message.author.id == message.mentions[0].id:
                return await message.channel.send("You can't mute yourself.")
            if message.guild.owner_id == message.mentions[0].id:
                return await message.channel.send("You can't mute the server owner!")
            if message.guild.owner_id != message.author.id and ((message.mentions[0].top_role >= message.author.top_role) and message.mentions[0].top_role.id != 885610515743772752):
                return await message.channel.send("This user is on the same role as you or higher.")
            if len(messageArray) < 2 or messageArray[1] == "":
                return await message.channel.send("Specify the time in which it is necessary to mute the person.")
        elif lang_u == "ru":
            if len(messageArray) == 0:
                #print("1")
                return await message.channel.send("Укажи человека, которого надо замьютить.")
            try:
                if len(message.mentions) == 0 and message.guild.get_member(int(messageArray[0])) == None:
                    #print("2")
                    #print(messageArray[0])
                    #print(message.mentions)
                    #print(message.guild.get_member(messageArray[0]))
                    return await message.channel.send("Укажи человека, которого надо замьютить.")
            except:
                return await message.channel.send("Укажи человека, которого надо замьютить.")
            coll = db.mutes
            data11 = coll.find({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" })
            if coll.count_documents({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" }) == 1:
                time_now = int(time.time())
                left_t = int(data11[0]['time_mute']) - time_now
                return await message.channel.send(f"Этот пользователь уже имеет мут. Осталось: {seconds_to_hh_mm_ss(left_t)}")
            if message.author.id == message.mentions[0].id:
                return await message.channel.send("Ты не можешь замьютить себя.")
            if message.guild.owner_id == message.mentions[0].id:
                return await message.channel.send("Ты не можешь замьютить овнера сервера!")
            if message.guild.owner_id != message.author.id and ((message.mentions[0].top_role >= message.author.top_role) and message.mentions[0].top_role.id != 885610515743772752):
                return await message.channel.send("Данный пользователь находится на одной роли с тобой или выше.")
            if len(messageArray) < 2 or messageArray[1] == "":
                return await message.channel.send("Укажите на сколько надо выдать мьют.")
        x = int(time.time())
        time1j = re.findall(r'(\d+)', messageArray[1])
        if len(time1j) == 0:
            if lang_u == "en":
                return await message.channel.send("Specify the time in which it is necessary to mute the person.")
            elif lang_u == "ru":
                return await message.channel.send("Укажите на сколько надо выдать мьют.")
        time_mute = time1j[0]
        mmm = messageArray[1]
        interval_mute = mmm[len(str(time1j[0])):]
        time_str = ""
        if interval_mute == "m":
            time_str = declension([ 'минуту', 'минуты', 'минут' ], int(time_mute))
            time_mute = int(time_mute) * 60
        elif interval_mute == "h":
            time_str = declension([ 'час', 'часа', 'часов' ], int(time_mute))
            time_mute = int(time_mute) * 3600
        elif interval_mute == "d":
            time_str = declension([ 'день', 'дня', 'дней' ], int(time_mute))
            time_mute = int(time_mute) * 86400
        else:
            if lang_u == "en":
                return await message.channel.send("Specify the time in which it is necessary to mute the person.")
            elif lang_u == "ru":
                return await message.channel.send("Укажите на сколько надо выдать мьют.")
        xn = x + int(time_mute)
        msg = ""
        if len(messageArray) < 3:
            if lang_u == "en":
                msg = "Unspecified"
            else:
                msg = "Не указана"
        else:
            for old in range(2, len(messageArray)):
                msg += " " + messageArray[old]
        msg = msg.strip()
        """
        ok1 = True
        ok2 = False
        for role in client.get_guild(message.guild.id).roles:
            coll = db.server
            data = coll.find({"server": str(message.guild.id)})
            if coll.count_documents({"server": str(message.guild.id)}) == 0:
                overwrite = discord.Permissions()
                overwrite.send_messages = False
                overwrite.speak = False
                role = await message.guild.create_role(name="Muted", permissions=overwrite)
                for channel in message.guild.channels:
                    overwrite = discord.Permissions()
                    overwrite.send_messages = False
                    overwrite.speak = False
                    await channel.set_permissions(role, send_messages = False,
                                                        speak = False)
                if message.guild.region == discord.VoiceRegion.russia:
                    coll.insert_one({"server": str(message.guild.id), "roleid_mute": str(role.id), "prefix": ".", "lang": "ru", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "Ты получил {level} уровень на сервере {server}!", "lvlChannelType": "dm", "lvlChannel": "" })
                else:
                    coll.insert_one({"server": str(message.guild.id), "roleid_mute": str(role.id), "prefix": ".", "lang": "en", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "You got {level} level on the {server} server!", "lvlChannelType": "dm", "lvlChannel": "" })
                coll = db.mutes
                coll.insert_one({"disid": str(message.mentions[0].id), "time_mute": str(xn), "guild": str(message.guild.id), "mod": str(message.author.id), "roleid": str(role.id), "reason": msg})
                await message.mentions[0].add_roles(role)
                break
            else:

                ok2 = True
                if str(role.id) == data[0]["roleid_mute"]:
                    coll = db.mutes
                    coll.insert_one({"disid": str(message.mentions[0].id), "time_mute": str(xn), "guild": str(message.guild.id), "roleid": str(role.id), "reason": msg})
                    await message.mentions[0].add_roles(role)
                    ok1 = False
                    break
        if ok1 and ok2:
            overwrite = discord.Permissions()
            overwrite.send_messages = False
            overwrite.speak = False
            role = await message.guild.create_role(name="Muted", permissions=overwrite)
            coll = db.server
            coll.update({"server": str(message.guild.id)}, { "$set": {"roleid_mute": str(role.id)}})
            coll = db.mutes
            coll.insert_one({"disid": str(message.mentions[0].id), "time_mute": str(xn), "guild": str(message.guild.id), "mod": str(message.author.id), "roleid": str(role.id), "reason": msg})
            await message.mentions[0].add_roles(role)
        """
        servers = db.server
        role_id = servers.find_one({"server": str(message.guild.id)})["roleid_mute"]
        role = message.guild.get_role(int(role_id))
        await message.mentions[0].add_roles(role)
        coll = db.mutes
        coll.insert_one({"disid": str(message.mentions[0].id), "time_mute": str(xn), "guild": str(message.guild.id), "mod": str(message.author.id), "roleid": str(role.id), "reason": msg})
        if lang_u == "en":
            desc = f"Member <@{str(message.mentions[0].id)}> muted for {str(time1j[0])} {time_str}\n──────────────────────────\nModerator - <@{str(message.author.id)}>\nReason: {msg}\n──────────────────────────"
        elif lang_u == "ru":
            desc = f"Участник <@{str(message.mentions[0].id)}> получил мут на {str(time1j[0])} {time_str}\n──────────────────────────\nМодератор - <@{str(message.author.id)}>\nПричина: {msg}\n──────────────────────────"
        staff = db.staff
        if staff.count_documents({"id": str(message.author.id)}) == 0:
            DataBase.actions().insert(staff, "one", {"id": str(message.author.id), "time_staff": int(time.time()), "warns": 0, "mutes": 0, "bans": 0, "mwarns": [] })
        user_s = staff.find_one({"id": str(message.author.id)})
        mutes = user_s['mutes']
        staff.update_one({"id": str(message.author.id)}, { "$set": { "mutes": mutes + 1 } })
        embed = discord.Embed(title="", description="**" + desc + "**", color=discord.Colour(0x2F3136))
        await message.channel.send(embed=embed)
        if message.mentions[0].voice != None:
            voice_m = message.mentions[0].voice.channel
            await message.mentions[0].edit(voice_channel=voice_m, reason="muted.")
        if message.guild.id == 604083589570625555:
            await channel_log.send(embed=embed)

    async def unmute(self, client, message, command, messageArray, lang_u):
        if message.guild.id == 604083589570625555:
            channel_log = message.guild.get_channel(config.log_channel)
        if lang_u == "en":
            if len(messageArray) == 0:
                return await message.channel.send("Specify the person to unmute.")
            if len(message.mentions) == 0 and message.guild.get_member(int(messageArray[0])) == None:
                return await message.channel.send("Specify the person to unmute.")
            coll = db.mutes
            if coll.count_documents({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" }) == 0:
                return await message.channel.send(f"This user already unmuted.")
        elif lang_u == "ru":
            if len(messageArray) == 0:
                return await message.channel.send("Укажи человека, которого надо размьютить.")
            if len(message.mentions) == 0 and message.guild.get_member(int(messageArray[0])) == None:
                return await message.channel.send("Укажи человека, которого надо размьютить.")
            coll = db.mutes
            if coll.count_documents({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" }) == 0:
                return await message.channel.send(f"Этот пользователь уже не имеет мут.")
        """
        ok1 = True
        ok2 = False
        for role in client.get_guild(message.guild.id).roles:
            coll = db.server
            data = coll.find({"server": str(message.guild.id)})
            if coll.count_documents({"server": str(message.guild.id)}) == 0:
                overwrite = discord.Permissions()
                overwrite.send_messages = False
                overwrite.speak = False
                role = await message.guild.create_role(name="Muted", permissions=overwrite)
                for channel in message.guild.channels:
                    overwrite = discord.Permissions()
                    overwrite.send_messages = False
                    overwrite.speak = False
                    await channel.set_permissions(role, send_messages = False,
                                                        speak = False)
                if message.guild.region == discord.VoiceRegion.russia:
                    coll.insert_one({"server": str(message.guild.id), "roleid_mute": str(role.id), "prefix": ".", "lang": "ru", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "Ты получил {level} уровень на сервере {server}!", "lvlChannelType": "dm", "lvlChannel": "" }) 
                else:
                    coll.insert_one({"server": str(message.guild.id), "roleid_mute": str(role.id), "prefix": ".", "lang": "en", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "You got {level} level on the {server} server!", "lvlChannelType": "dm", "lvlChannel": "" })
                coll = db.mutes
                coll.delete_one({"disid": str(message.mentions[0].id), "guild": f"{message.guild.id}" })
                await message.mentions[0].remove_roles(role)
                break
            else:

                ok2 = True
                if role.id == int(data[0]["roleid_mute"]):
                    coll = db.mutes
                    coll.delete_one({"disid": str(message.mentions[0].id), "guild": f"{message.guild.id}" })
                    await message.mentions[0].remove_roles(role)
                    ok1 = False
                    break
        if ok1 and ok2:
            overwrite = discord.Permissions()
            overwrite.send_messages = False
            overwrite.speak = False
            role = await message.guild.create_role(name="Muted", permissions=overwrite)
            coll = db.server
            coll.update({"server": str(message.guild.id)}, { "$set": {"roleid_mute": str(role.id)}})
            coll = db.mutes
            coll.delete_one({"disid": str(message.mentions[0].id), "guild": f"{message.guild.id}" })
            await message.mentions[0].remove_roles(role)
        """
        servers = db.server
        role_id = servers.find_one({"server": str(message.guild.id)})["roleid_mute"]
        role = message.guild.get_role(int(role_id))
        await message.mentions[0].remove_roles(role)
        coll = db.mutes
        coll.delete_one({"disid": str(message.mentions[0].id), "guild": f"{message.guild.id}" })
        if lang_u == "en":
            desc = f"Member <@{str(message.mentions[0].id)}> unmuted.\n──────────────────────────\nModerator - <@{str(message.author.id)}>\n──────────────────────────"
        elif lang_u == "ru":
            desc = f"Участник <@{str(message.mentions[0].id)}> получил размут.\n──────────────────────────\nМодератор - <@{str(message.author.id)}>\n──────────────────────────"
        embed = discord.Embed(title="", description="**" + desc + "**", color=discord.Colour(0x2F3136))
        await message.channel.send(embed=embed)
        if message.mentions[0].voice != None:
            voice_m = message.mentions[0].voice.channel
            await message.mentions[0].edit(voice_channel=voice_m, reason="unmuted.")
        if message.guild.id == 604083589570625555:
            await channel_log.send(embed=embed)
    
    async def slowmode(self, client, message, command, messageArray, lang_u):
        if message.author.guild_permissions.administrator:
            if lang_u == "en":
                if len(messageArray) == 0:
                    return await message.channel.send("Specify the slow mode time from 0 to 21600 seconds.")
                time1j = re.findall(r'(\d+)', messageArray[0])
                if len(time1j) == 0:
                    return await message.channel.send("Specify the slow mode time from 0 to 21600 seconds.")
                if int(time1j[0]) > 21600 or int(time1j[0]) < 0:
                    return await message.channel.send("Specify the slow mode time from 0 to 21600 seconds.")
                await message.channel.send(f"Slow mode is set to {time1j[0]} second(s).")
                await message.channel.edit(slowmode_delay=int(time1j[0])) 
            elif lang_u == "ru":
                if len(messageArray) == 0:
                    return await message.channel.send("Укажите на сколько надо поставить слоумод от 0 до 21600 секунд.")
                time1j = re.findall(r'(\d+)', messageArray[0])
                if len(time1j) == 0:
                    return await message.channel.send("Укажите на сколько надо поставить слоумод от 0 до 21600 секунд.")
                if int(time1j[0]) > 21600 or int(time1j[0]) < 0:
                    return await message.channel.send("Укажите на сколько надо поставить слоумод от 0 до 21600 секунд.")
                await message.channel.send(f"Установлен слоумод на {time1j[0]} секунд(у|ы).")
                await message.channel.edit(slowmode_delay=int(time1j[0]))

    async def clear(self, client, message, command, messageArray, lang_u):
        
        if str(message.author.id) in config.ADMINS:
            if len(messageArray) == 0 or messageArray[0] == "":
                e = discord.Embed(title="Ошибка", description=f"Укажите сколько сообщений надо очистить.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            deleted = await message.channel.purge(limit=int(messageArray[0]) + 1)
            e = discord.Embed(title="Очистка чата", description=f'Очищено сообщений: {len(deleted) - 1}.', color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e, delete_after=10)