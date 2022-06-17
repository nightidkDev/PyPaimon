import asyncio
import datetime
import json
import os
import random
import re
import time
import io
import psutil
import string
import glob
import numpy
from PIL import Image, ImageDraw, ImageFont

import discord
import discord.ext
from discord import utils
import pymongo
import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
users = db.prof_ec_users
servers = db.server
week_stats = db.week_stats
sdb = db.u_settings
clans_db = db.clans
mutes = db.mutes

from libs import Builders
from libs import Profile
from libs import DataBase
from libs import ReactionsOnMessage
from cmds import Mod
from plugins import voice_money
from plugins import checkreact
from plugins import checkselect
from plugins import funcb
from Modules import main

print("Loading...")

intents = discord.Intents().all() 
client = discord.Client(intents=intents)

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}д. {h:02d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{h:02d}:{m:02d}:{s:02d}"  

    
async def checkusertop(client, top, guild):
    place = 0
    user = guild.get_member(int(top[place]["id"]))
    while not user:
        place += 1
        user = guild.get_member(int(top[place]["id"]))

    return user

async def messages_in_chat():
    await client.wait_until_ready()
    while not client.is_closed():
        guild = client.get_guild(604083589570625555)
        channel = guild.get_channel(766351044380721202)
        role = guild.get_role(767012156557623356)
        phrase = random.choice(config.messsages_chat)
        members = list(filter(lambda a: a.bot == False, role.members))
        members = list(filter(lambda a: a.status != discord.Status.offline, members))

        member = random.choice(members)
        phrase = phrase.replace("{member}", member.mention)

        await channel.send(phrase)
        await asyncio.sleep(300)


async def status(): 
    await client.wait_until_ready()
    while True:
        guild = client.get_guild(604083589570625555)
        members = len(list(filter(lambda a: a.bot == False, guild.members)))
        await client.change_presence(activity=discord.Streaming(name=f"Участников: {members}", url="https://twitch.tv/maksimkarys"), status=discord.Status.do_not_disturb)
        await asyncio.sleep(60)

def image_to_byte_array(image:Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

async def check_time():
    await client.wait_until_ready()
    while True:
        mytime = time.localtime()
        if config.type_time == "day":
            if mytime.tm_hour > 5 and mytime.tm_hour < 13:
                config.type_time = "morning"
            elif mytime.tm_hour < 13 or mytime.tm_hour > 20:
                config.type_time = "night"
        elif config.type_time == "night":
            if mytime.tm_hour > 5 and mytime.tm_hour < 13:      
                config.type_time = "morning"
            elif mytime.tm_hour > 13 and mytime.tm_hour < 20:
                config.type_time = "day"
        elif config.type_time == "morning":
            if mytime.tm_hour > 13 and mytime.tm_hour < 20:
                config.type_time = "day"
            elif mytime.tm_hour < 13 or mytime.tm_hour > 20:
                config.type_time = "night"
        await asyncio.sleep(60)

async def check_cooldown():
    await client.wait_until_ready()
    
    while True:
        cooldowns = users.find({ "cooldown": { "$ne": [] } })
        for x in cooldowns:
            cd = x["cooldown"]
            cdnew = []
            for i in range(len(cd)):
                name, timec = cd[i]
                #print(name)
                #print(timec)
                if timec <= int(time.time()):
                    cdnew.append(cd[i])
            if len(cdnew) > 0:
                for b in cdnew:
                    ind = cd.index(b)
                    cd.pop(ind)
                users.update_one({ "disid": x["disid"], "guild": x["guild"] }, { "$set": { "cooldown": cd } })
        await asyncio.sleep(1)

async def fcheckreact():
    await client.wait_until_ready()
    while True:
        await checkselect.checkselect(client)
        await checkreact.checkreact(client)
        await checkreact.checkreactduels(client)
        await asyncio.sleep(1)

async def fcheckstatdate():
    await client.wait_until_ready()
    while True:
        
        server = servers.find_one({ "server": "604083589570625555" })
        day = server["day_time"]
        week = server["week_time"]
        week2 = server["week2_time"]
        timely = server["timely_time"]
        x = int(time.time())
        if x - day >= 86400:
            servers.update_one({ "server": "604083589570625555" }, { "$inc": { "day_time": 86400 } })
            history_1d = config.cmoneystats["history_1d"]
            users.update_many({}, { "$set": { f"moneystats.history_1d": history_1d, "moneystats.1d": 0 } })
        if x - week >= 604800:
            topvc = week_stats.find().sort("voice", -1)
            topch = week_stats.find().sort("chat", -1)

            guild = client.get_guild(604083589570625555)

            #uservc = guild.get_member(int(topvc["id"]))
            #userch = guild.get_member(int(topch["id"]))

            uservc = await checkusertop(client, topvc, guild)
            userch = await checkusertop(client, topch, guild)
        
            
            typer = guild.get_role(826925239187406849)
            speaker = guild.get_role(826919015452377109)

            if server["typer_week"] != "":
                userchold = guild.get_member(int(server["typer_week"]))
                try:
                    await userchold.remove_roles(typer)
                except:
                    pass
            if server["voicer_week"] != "":
                uservcold = guild.get_member(int(server["voicer_week"]))
                try:
                    await uservcold.remove_roles(speaker)
                except:
                    pass
            
            try:
                await uservc.add_roles(speaker)
            except:
                pass
            try:
                await userch.add_roles(typer)
            except:
                pass


            channel_give = guild.get_channel(767015636354203659)
            await channel_give.send(f'.give 2000 1 место в еженедельном топе. <@!{uservc.id}> <@!{userch.id}>')
            

            week_stats.delete_many({})
            servers.update_one({ "server": "604083589570625555" }, { "$inc": { "week_time": 604800 } })
            servers.update_one({ "server": "604083589570625555" }, { "$set": { "week_time": x, "typer_week": str(userch.id), "voicer_week": str(uservc.id) } })
            users.update_many({}, { "$set": { "moneystats.7d": 0 } })
            voice_members = list(filter(lambda a: a.voice != None, guild.members))
            xt = int(time.time())
            for user in voice_members:
                users.update_one({ "disid": f"{user.id}", "guild": f"{guild.id}" }, { "$set": { "last_time": f"{xt}" } })

        if x - week2 >= 1209600:
            servers.update_one({ "server": "604083589570625555" }, { "$inc": { "week2_time": 1209600 } })
            users.update_many({}, { "$set": { "moneystats.14d": 0 } })
        if x - timely >= 86400:
            servers.update_one({ "server": "604083589570625555" }, { "$inc": { "timely_time": 86400 } })
            users.update_many({ "timely_used": 0 }, { "$set": { "timely_count": 1 } })
            users.update_many({}, { "$set": { "timely_used": 0 } })
            users.update_many({ "btimely_used": 0 }, { "$set": { "btimely_count": 1 } })
            users.update_many({}, { "$set": { "btimely_used": 0 } })
        
        await asyncio.sleep(1)

@client.event
async def on_ready():
    print("--------------------------------")
    guild = client.get_guild(604083589570625555)
    while not guild:
        guild = client.get_guild(604083589570625555)
        print("Wait..")
        await asyncio.sleep(1)
    print("--------------------------------")
    mytime = time.localtime()
    if config.type_time == "day":
        if mytime.tm_hour > 5 and mytime.tm_hour < 13:
            config.type_time = "morning"
        elif mytime.tm_hour < 13 or mytime.tm_hour > 20:
            config.type_time = "night"
    elif config.type_time == "night":
        if mytime.tm_hour > 5 and mytime.tm_hour < 13:      
            config.type_time = "morning"
        elif mytime.tm_hour > 13 and mytime.tm_hour < 20:
            config.type_time = "day"
    elif config.type_time == "morning":
        if mytime.tm_hour > 13 and mytime.tm_hour < 20:
            config.type_time = "day"
        elif mytime.tm_hour < 13 or mytime.tm_hour > 20:
            config.type_time = "night"
    deny_words = None
    with open('./assets/Files/deny_words.txt') as f:
        deny_words = f.read().split("\n")
    config.deny_words = deny_words
    print(f"[{datetime.datetime.utcfromtimestamp(int(time.time()) + 10800).strftime('%H:%M:%S')}] Запустилась второстепенная (функции) Paimon.exe <3")

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.channel.id == 794161980662743050:
        if len(message.attachments) == 0:
            await message.delete()

    if message.author.bot and str(message.author.id) not in config.BOTS_REWARD:
        return

    if message.guild == None:
        return None
    else:
        userdata = users.find_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" })
        if servers.count_documents({"server": f"{message.guild.id}"}) == 0:
            if message.guild.region == discord.VoiceRegion.russia:
                servers.insert_one({"server": str(message.guild.id), "roleid_mute": "", "prefix": ".", "lang": "ru", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "Ты получил {level} уровень на сервере {server}!", "lvlChannelType": "dm", "lvlChannel": "" })
            else:
                servers.insert_one({"server": str(message.guild.id), "roleid_mute": "", "prefix": ".", "lang": "en", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "You got {level} level on the {server} server!", "lvlChannelType": "dm", "lvlChannel": "" })
        else:
            lang_u = servers.find_one({"server": f"{message.guild.id}"})["lang"]
        if users.count_documents({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }) == 0:
            x = int(time.time())
            users.insert_one({ "disid": str(message.author.id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{message.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "rob": 1, "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
        else:
            
            if sdb.count_documents({ "id": str(message.author.id), "guild": str(message.guild.id) }) == 0:
                sdb.insert_one({ "id": str(message.author.id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })
                
            user_s = sdb.find_one({ "id": str(message.author.id), "guild": str(message.guild.id) })
            if int(userdata["exp"]) >= int(userdata["nexp"]):
                exp_ins = int(userdata["exp"]) - int(userdata["nexp"])
                nexp_ins = int(userdata["nexp"]) + int(userdata["nlvl"])
                nlvl_ins = int(userdata["nlvl"]) + 10
                lvl_ins = int(userdata["lvl"]) + 1
                moneyu = userdata["money"]
                bonusm = 0
                if message.guild.id == 604083589570625555:
                    ranks = config.ranks
                    last_role = None
                    for rank in ranks:
                        if lvl_ins == rank[0]:
                            bonusm = rank[2]
                        else:
                            bonusm = 0
                        if lvl_ins >= rank[0]:
                            role_lvl = message.guild.get_role(int(rank[1]))
                            index_role = ranks.index([rank[0], rank[1], rank[2]])
                            #print(index_role)
                            if index_role != len(ranks) - 1:
                                last_role = message.guild.get_role(int(ranks[index_role + 1][1]))
                            if user_s["role_lvl"] == 1:
                                if role_lvl not in message.author.roles:
                                    await message.author.add_roles(role_lvl)
                                if last_role != None:
                                    if last_role in message.author.roles:
                                        await message.author.remove_roles(last_role)
                            break
                moneyu += bonusm
                users.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "exp": exp_ins, "nexp": str(nexp_ins), "lvl": lvl_ins, "nlvl": str(nlvl_ins), "money": moneyu } })
                member = message.guild.get_member(message.author.id)
                data = servers.find_one({ "server": f"{message.guild.id}" })
                lvlMessage = data["lvlMessage"]
                lvlMessage = lvlMessage.replace("{server}", message.guild.name)
                lvlMessage = lvlMessage.replace("{level}", str(lvl_ins))
                lvlMessage = lvlMessage.replace("{member}", f"<@!{member.id}>")
                e = discord.Embed(title="", description=f"{lvlMessage}", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                if data["lvlChannelType"] == "dm":
                    try:
                        if user_s["notify_lvl"] == 1:
                            await member.send(embed=e)
                    except:
                        sdb.update_one({ "id": str(member.id), "guild": str(message.guild.id) }, { "$set": { "notify_lvl": 0 } })
                elif data["lvlChannelType"] == "channel":
                    channel = message.guild.get_channel(int(data["lvlChannel"]))
                    await channel.send(embed=e)
            if message.channel.id in config.NotFloodChannels and message.channel.id != 911906858531450931:

                if week_stats.count_documents({ "id": f"{message.author.id}" }) == 0:
                    week_stats.insert_one({ "id": f"{message.author.id}", "chat": 0, "voice": 0 })
                uws = week_stats.find_one({ "id": f"{message.author.id}" })
                week_stats.update_one({ "id": f"{message.author.id}" }, { "$set": { "chat": uws["chat"] + 1 } })
                if int(userdata["msg_m"]) >= 2:
                    multiplier = 1
                    multiplier_money = 1
                    boost_role = message.guild.get_role(612661327101558796)
                    if boost_role in message.author.roles:
                        multiplier = 1.5
                        multiplier_money = 2 
                    
                    boosterclan = 1
                    if userdata["clan"] != "":
                        clan = clans_db.find_one({ "id": int(userdata["clan"]) })
                        boosterclan = clan["booster"]
                    exp = int(random.randint(10, 20) * multiplier * boosterclan)
                    exp_now = int(userdata["exp"])
                    exp_ins = exp + exp_now
                    ms = userdata["moneystats"]
                    ms["1d"] += 1
                    ms["7d"] += 1
                    ms["14d"] += 1
                    ms["all"] += 1
                    ms["history_1d"]["chat"]["count"] += 1
                    if ms["history_1d"]["chat"]["view"] == 0:
                        ms["history_1d"]["chat"]["view"] = 1
                    ms["history"]["chat"]["count"] += 1
                    if ms["history"]["chat"]["view"] == 0:
                        ms["history"]["chat"]["view"] = 1
                    if userdata["clan"] != "":
                        if message.author.id == 252378040024301570 or message.author.id == 518427777523908608:
                            expn = exp
                        else:
                            expn = int(exp / 2)
                        if clan["exp"] + expn < clan["nexp"] * 2:
                            clans_db.update_one({ "id": int(userdata["clan"]) }, { "$inc": { "exp": expn } })
                    
                    if message.channel.id == 832567656254668800:
                        money_add = int(multiplier_money * boosterclan / 2)
                    else:
                        money_add = int(multiplier_money * boosterclan)
                    users.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "msg": int(userdata["msg"]) + 1, "msg_m": "0", "money": int(userdata["money"]) + money_add, "exp": exp_ins, "moneystats": ms } })
                else:
                    users.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "msg": int(userdata["msg"]) + 1, "msg_m": str(int(userdata["msg_m"]) + 1) } })
            messages_s = 0
            foundChannel = False
            for elem in userdata["c_channels"]:
                for channel, m in list(elem.items()):
                    if channel == str(message.channel.id):
                        foundChannel = True
                        messages_s = m
                        break
            if foundChannel == False:
                users.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$push": { "c_channels": { str(message.channel.id): 0 } } })
            users.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { f"c_channels.$[element].{message.channel.id}": messages_s + 1 } }, array_filters=[ { f"element.{message.channel.id}": messages_s } ])
            users.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "s_chat": userdata["s_chat"] + 1 } })

    if message.guild.id == 604083589570625555:
        if message.channel.id == 787038639979757618:
            server_info = servers.find_one({ "server": "604083589570625555" })
            if server_info["count_message_answers"] >= 13:
                cat_lapki = client.get_emoji(767842545338023947)
                servers.update_one({ "server": "604083589570625555" }, { "$set": { "count_message_answers": 0 } })
                e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
                e.description = f"""**Внимание!

Просим всех путешественников тщательно формулировать вопросы для помощи в игре.
Старайтесь коротко формулировать свои вопросы, а также более разборчиво и кратко давать ответы.
Любые излишние комментарии не касающиеся ответов на вопрос будут подвергаться удалению.

Приятного вам отдыха, пупсики {cat_lapki}**"""
                e.set_footer(text=f"{message.guild.name}", icon_url=message.guild.icon_url)
                await message.channel.send(embed=e)
            else:
                servers.update_one({ "server": "604083589570625555" }, { "$set": { "count_message_answers": server_info["count_message_answers"] + 1 } })
                

        if message.channel.id == 787039917481525268:
            server_info = servers.find_one({ "server": "604083589570625555" })
            if server_info["count_message_search"] >= 15:
                cat_lapki = client.get_emoji(767842545338023947)
                servers.update_one({ "server": "604083589570625555" }, { "$set": { "count_message_search": 0 } })
                e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
                e.description = f"""**Внимание!

Просим всех путешественников тщательно формулировать просьбы помощи в игре.
Указывайте ваш `UID` при обращении, чтобы пользователям было проще вам помочь.
Любые приглашения в лс или же слоганы, по типу "ищу игроков", без вашего личного `UID` будут подвергаться удалению.

Удачных вам поисков, пупсики. {cat_lapki}**"""
                e.set_footer(text=f"{message.guild.name}", icon_url=message.guild.icon_url)
                await message.channel.send(embed=e)
            else:
                servers.update_one({ "server": "604083589570625555" }, { "$set": { "count_message_search": server_info["count_message_search"] + 1 } })        
        if message.channel.id == 794660897271578625:
            server_info = servers.find_one({ "server": "604083589570625555" })
            captcha = server_info["captcha_jail"]
            muted = message.guild.get_role(767025328405086218)
            if message.content == captcha["text"] and (captcha["used"] == 0 and captcha["expire"] == 0):
                if muted in message.author.roles:
                    captcha["used"] = 1
                    servers.update_one({ "server": "604083589570625555" }, { "$set": { "captcha_jail": captcha } })
                    user_info = mutes.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })

                    if not user_info:
                        return

                    if int(user_info["time_mute"]) - 3600 <= int(time.time()):
                        mutes.delete_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
                        await message.author.remove_roles(muted)
                        e = discord.Embed(title='', description="Поздравляем, вы ввели код и успешно освободились от мута.", color=0x2F3136)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=message.author.name, icon_url=message.author.avatar_url)
                        await message.reply(embed=e)
                    else:
                        mutes.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$set": { "time_mute": str(int(user_info["time_mute"]) - 3600) } })
                        e = discord.Embed(title='', description="Поздравляем, вы ввели код и получили -1 час от мута.", color=0x2F3136)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=message.author.name, icon_url=message.author.avatar_url)
                        await message.reply(embed=e)
                    try:
                        message_fetch = await message.channel.fetch_message(int(captcha["message_id"]))
                        await message_fetch.delete()
                    except:
                        pass
        elif message.channel.id == 766351044380721202:
            server_info = servers.find_one({ "server": "604083589570625555" })
            captcha = server_info["captcha"]
            staff_role = message.guild.get_role(761771540181942273)
            if message.content == captcha["text"] and (captcha["used"] == 0 and captcha["expire"] == 0):
                if staff_role not in message.author.roles:
                    captcha["used"] = 1
                    servers.update_one({ "server": "604083589570625555" }, { "$set": { "captcha": captcha } })
                    user_info = users.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
                    ms = user_info["moneystats"]
                    ms["1d"] += captcha["gift"]
                    ms["7d"] += captcha["gift"]
                    ms["14d"] += captcha["gift"]
                    ms["all"] += captcha["gift"]
                    if ms["history_1d"]["captcha"]["view"] == 0:
                        ms["history_1d"]["captcha"]["view"] = 1
                    ms["history_1d"]["captcha"]["count"] += captcha["gift"]
                    if ms["history"]["captcha"]["view"] == 0:
                        ms["history"]["captcha"]["view"] = 1
                    ms["history"]["captcha"]["count"] += captcha["gift"]
                    users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$set": { "money": user_info["money"] + captcha["gift"], "moneystats": ms } })
                    emoji_gems = client.get_emoji(config.MONEY_EMOJI)
                    e = discord.Embed(title="", description=f"Поздравляю, ты получил {captcha['gift']}{emoji_gems}.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.reply(embed=e)
                    try:
                        message_fetch = await message.channel.fetch_message(int(captcha["message_id"]))
                        await message_fetch.delete()
                    except:
                        pass
                else:
                    e = discord.Embed(title="", description=f"Ты находишься в стаффе, поэтому тебе запрещен сбор кодов.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.reply(embed=e, delete_after=10.0)
            

        elif message.channel.id == 823506887395770368:
            server_info = servers.find_one({ "server": "604083589570625555" })
            captcha = server_info["captcha2"]
            staff_role = message.guild.get_role(761771540181942273)
            if message.content == captcha["text"] and (captcha["used"] == 0 and captcha["expire"] == 0):
                if staff_role not in message.author.roles:
                    captcha["used"] = 1
                    servers.update_one({ "server": "604083589570625555" }, { "$set": { "captcha2": captcha } })
                    user_info = users.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
                    ms = user_info["moneystats"]
                    ms["1d"] += captcha["gift"]
                    ms["7d"] += captcha["gift"]
                    ms["14d"] += captcha["gift"]
                    ms["all"] += captcha["gift"]
                    if ms["history_1d"]["captcha"]["view"] == 0:
                        ms["history_1d"]["captcha"]["view"] = 1
                    ms["history_1d"]["captcha"]["count"] += captcha["gift"]
                    if ms["history"]["captcha"]["view"] == 0:
                        ms["history"]["captcha"]["view"] = 1
                    ms["history"]["captcha"]["count"] += captcha["gift"]
                    users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$set": { "money": user_info["money"] + captcha["gift"], "moneystats": ms } })
                    emoji_gems = client.get_emoji(config.MONEY_EMOJI)
                    e = discord.Embed(title="", description=f"Поздравляю, ты получил {captcha['gift']}{emoji_gems}.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.reply(embed=e)
                    try:
                        message_fetch = await message.channel.fetch_message(int(captcha["message_id"]))
                        await message_fetch.delete()
                    except:
                        pass
                else:
                    e = discord.Embed(title="", description=f"Ты находишься в стаффе, поэтому тебе запрещен сбор кодов.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.reply(embed=e, delete_after=10.0)
        
        
        elif message.channel.id == 832567656254668800:
            server_info = servers.find_one({ "server": "604083589570625555" })
            captcha = server_info["captcha3"]
            staff_role = message.guild.get_role(761771540181942273)
            if message.content == captcha["text"] and (captcha["used"] == 0 and captcha["expire"] == 0):
                if staff_role not in message.author.roles:
                    captcha["used"] = 1
                    servers.update_one({ "server": "604083589570625555" }, { "$set": { "captcha3": captcha } })
                    user_info = users.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
                    ms = user_info["moneystats"]
                    ms["1d"] += captcha["gift"]
                    ms["7d"] += captcha["gift"]
                    ms["14d"] += captcha["gift"]
                    ms["all"] += captcha["gift"]
                    if ms["history_1d"]["captcha"]["view"] == 0:
                        ms["history_1d"]["captcha"]["view"] = 1
                    ms["history_1d"]["captcha"]["count"] += captcha["gift"]
                    if ms["history"]["captcha"]["view"] == 0:
                        ms["history"]["captcha"]["view"] = 1
                    ms["history"]["captcha"]["count"] += captcha["gift"]
                    users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$set": { "money": user_info["money"] + captcha["gift"], "moneystats": ms } })
                    emoji_gems = client.get_emoji(config.MONEY_EMOJI)
                    e = discord.Embed(title="", description=f"Поздравляю, ты получил {captcha['gift']}{emoji_gems}.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.reply(embed=e)
                    try:
                        message_fetch = await message.channel.fetch_message(int(captcha["message_id"]))
                        await message_fetch.delete()
                    except:
                        pass
                else:
                    e = discord.Embed(title="", description=f"Ты находишься в стаффе, поэтому тебе запрещен сбор кодов.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.reply(embed=e, delete_after=10.0)
            

        if config.type_time == "night" or message.author.id == 252378040024301570 and message.channel.id not in [766390214267764786]:
            ssn = message.content.lower()
            if ("спокойной" in ssn and "ночи" in ssn) or ("споки" in ssn and "ноки" in ssn) or "спкнч" in ssn:
                await message.reply("Сладких снов :3")

        if config.type_time == "morning" or message.author.id == 252378040024301570 and message.channel.id not in [766390214267764786]:
            ssn = message.content.lower()
            if "доброе утро" in ssn or "доброго утра" in ssn or "доброе утречко" in ssn or "доброго утречка" in ssn:
                phrases = [
                    "Доброе утро! Утренние часы мимолетны и прекрасны. Посвяти же их тому, что любишь.",
                    "Доброе утро и хорошего дня :3",
                    "Доброе утро. Начни его с кружечки чая или кофе."
                ]
                await message.reply(random.choice(phrases))

        if message.author.guild_permissions.administrator is False and f"{message.author.id}" not in config.ADMINS and (message.channel.id == 823506887395770368 or message.channel.id == 766351044380721202 or message.channel.id == 832567656254668800 or message.channel.id == 766390214267764786):
            a = message.content.strip().lower()
            wf = main.WordsFilter()

            wf.set_words(config.deny_words)
            for b in list(string.punctuation):
                a = a.replace(f'{b}', '')
            answers = [
                "Хей-хей, полегче! Давай тебя немного успокоим предупреждением, чтобы я такого больше не видела!",
                "Людей определяют их поступки, а не твои впечатления.",
                "За преступлением всегда следует правосудие и ты не исключение.",
                "Совместное общение вообще-то предполагает хотя бы минимальный этикет!",
                "Смотреть сквозь пальцы на скрытые угрозы я не собираюсь!",
                "Без ответственности не надейся быть свободным!",
                "В компании важно быть вежливым со всеми."
            ]
            d = {'а' : ['а', 'a', '@'],
                'б' : ['б', '6', 'b'],
                'в' : ['в', 'b', 'v'],
                'г' : ['г', 'g'],
                'д' : ['д', 'd'],
                'е' : ['е', 'e'],
                'ё' : ['ё', 'e'],
                'ж' : ['ж', 'zh', '*'],
                'з' : ['з', '3', 'z'],
                'и' : ['и', 'u', 'i'],
                'й' : ['й', 'u', 'i'],
                'к' : ['к', 'k', 'i{', '|{'],
                'л' : ['л', 'l', 'ji'],
                'м' : ['м', 'm'],
                'н' : ['н', 'h', 'n'],
                'о' : ['о', 'o', '0'],
                'п' : ['п', 'n', 'p'],
                'р' : ['р', 'r', 'p'],
                'с' : ['с', 'c', 's'],
                'т' : ['т', 'm', 't'],
                'у' : ['у', 'y', 'u'],
                'ф' : ['ф', 'f'],
                'х' : ['х', 'x', 'h' , '}{'],
                'ц' : ['ц', 'c', 'u,'],
                'ч' : ['ч', 'ch'],
                'ш' : ['ш', 'sh'],
                'щ' : ['щ', 'sch'],
                'ь' : ['ь', 'b'],
                'ы' : ['ы', 'bi'],
                'ъ' : ['ъ'],
                'э' : ['э', 'e'],
                'ю' : ['ю', 'io'],
                'я' : ['я', 'ya']
            }

            ed_phrase = a

            for key, value in d.items():
                for letter in value:
                    for phr in ed_phrase:
                        if letter == phr:
                            ed_phrase = ed_phrase.replace(phr, key)


            if wf.filter(a) is True or wf.filter(ed_phrase) is True:
                try:
                    msg = message.content.replace('\n', '')
                    await message.guild.get_channel(822510348808486952).send(f".warn <@!{message.author.id}> Автомодерация чата: запрещённые слова. (\'{msg}\')")
                except:
                    await message.guild.get_channel(822510348808486952).send(f".warn <@!{message.author.id}> Автомодерация чата: запрещённые слова.")
                await message.reply(f"{random.choice(answers)}")
                return await funcb.deltime(message, 3)
                
client.loop.create_task(messages_in_chat())
client.loop.create_task(fcheckstatdate())
client.loop.create_task(check_time())
client.loop.create_task(check_cooldown())
client.loop.create_task(status())
client.loop.create_task(fcheckreact())
token = config.TOKEN
client.run(str(token))