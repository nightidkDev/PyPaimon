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

import discord
import discord.ext
import discord_components
from discord_components import *
from discord import utils
import pymongo
import config
uri = config.uri

from libs import Builders
from libs import Profile
from libs import DataBase
from libs import ReactionsOnMessage
from libs import SelectLib
from plugins import voice_money
from plugins import checkreact
from plugins import funcb
from cmds import Mod

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
users = db.prof_ec_users
mutes = db.mutes
lb = db.lb
no13 = db.no13
servers = db.server
week_stats = db.week_stats

print("Loading...")

intents = discord.Intents().all() 
client = discord.Client(intents=intents)

dict_letters = {'а' : ['а', 'a', '@'],
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

@client.event
async def on_ready():
    
    x = int(time.time())
    guild = client.get_guild(604083589570625555)

    for user in users.find({ "voice_state": "1" }):
        member = guild.get_member(int(user['disid']))
        if not member:
            users.update_one({ "disid": user["disid"] }, { "$set": { "voice_state": "0" } }) 
            continue
        if member.voice is None:
            users.update_one({ "disid": user["disid"] }, { "$set": { "voice_state": "0" } }) 

    members_guild = list(filter(lambda a: a.bot is False and a.voice is not None, guild.members))

    for member in members_guild:
        if member.voice:
            try:
                if member.bot:
                    continue
                if users.count_documents({ "disid": str(member.id), "guild": str(guild.id) }) == 0:
                    # nexp: 100, nlvl: 55
                    users.insert_one({ "disid": str(member.id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
                user = users.find_one({ "disid": str(member.id), "guild": str(guild.id) })
                if user["voice_state"] == 0:
                    users.update_one({ "disid": user["disid"], "guild": f"{guild.id}" }, { "$set": { "voice_state": "1", "last_time": str(x) } })
            except:
                pass
    
    members = len(list(filter(lambda a: a.bot == False, guild.members)))
    await client.change_presence(activity=discord.Streaming(name=f"Участников: {members}", url="https://twitch.tv/maksimkarys"), status=discord.Status.do_not_disturb)
    mytime = time.localtime()
    if mytime.tm_hour < 6 or mytime.tm_hour > 20:
        config.type_time = "night"
    else:
        config.type_time = "day"
    #DiscordComponents(client)
    print(f"[{datetime.datetime.utcfromtimestamp(int(time.time()) + 10800).strftime('%H:%M:%S')}] Запустилась второстепенная (дискорд функции) Paimon.exe <3")

#@client.event
#async def on_button_click(interaction):
#    if not interaction:
#        return
#    await interaction.respond(content = f"You clicked on `{interaction.component.label}`")

@client.event
async def on_select_option(interaction):
    if not interaction:
        return
    await SelectLib.on_select(client, discord, interaction.user, interaction.message, config, interaction)

@client.event
async def on_member_join(member):
    if member.guild.id == 604083589570625555:
        attackSetting = servers.find_one({ "server": "604083589570625555" })["attackSetting"]
        if attackSetting == 1:
            config.lastblocktime = config.blocktime
            config.blocktime = time.time()
            if config.blocktime - config.lastblocktime <= 2:
                config.blockuser.append(member.id)
            else:
                config.blockuser = []
            if len(config.blockuser) >= 5:
                psina = member.guild.get_member(856847328043859978)
                night = member.guild.get_member(252378040024301570)
                wishellon = member.guild.get_member(332816661897805826)
                e = discord.Embed(color=0xff0000)
                e.title = "ВНИМАНИЕ!"
                e.description = "ОБНАРУЖЕНА ВОЗМОЖНАЯ АТАКА.\nЕСЛИ ЭТО СООБЩЕНИЕ ДУБЛИРУЕТСЯ БОЛЬШЕ ОДНО РАЗА, ТО ЭТО ТОЧНО АТАКА."
                await psina.send(embed=e)
                await night.send(embed=e)
                await wishellon.send(embed=e)
                for u in config.blockuser:
                    try:
                        await member.guild.ban(member.guild.get_member(u), reason="module: AttackDef")
                    except:
                        pass
                
                config.blockuser = []

@client.event
async def on_member_remove(member):
    if users.count_documents({"disid": str(member.id), "guild": str(member.guild.id)}) != 0:
        user = users.find_one({"disid": str(member.id), "guild": str(member.guild.id)})
        if user["partner"] != "":
            guild = client.get_guild(int(user["guild"]))
            member2 = guild.get_member(int(user["partner"]))
            role = guild.get_role(772569219555917834)
            try:
                await member.remove_roles(role)
            except:
                pass
            users.update_one({"disid": f"{member2.id}", "guild": str(member2.guild.id)}, { "$set": { 'partner': "", 'love_room': "", 'marry_time': 0, 'love_room_created': 0 } })
            try:
                await member.guild.get_channel(int(user["love_room"])).delete()
            except BaseException as e:
                print(e)
        users.update_one({"disid": str(member.id), "guild": str(member.guild.id)}, { "$set": { "view": "false", 'partner': "", 'love_room': "", 'marry_time': 0, 'love_room_created': 0 } })

@client.event
async def on_voice_state_update(member, before, after):
    if member == client.user:
        return

    if not before.channel and after.channel:
        if after.channel.category.id == 865613264296869908:
            if member.bot:
                await member.edit(voice_channel=None)
    
    if before.channel and after.channel:
        if after.channel.category.id == 865613264296869908:
            if member.bot:
                await member.edit(voice_channel=None)

    if member.bot:
        return

    if week_stats.count_documents({ "id": f"{member.id}" }) == 0:
        week_stats.insert_one({ "id": f"{member.id}", "chat": 0, "voice": 0 })

    uws = week_stats.find_one({ "id": f"{member.id}" })


    x = int(time.time())
    if users.count_documents({ "disid": str(member.id), "guild": f"{member.guild.id}" }) == 0:
        users.insert_one({ "disid": str(member.id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{member.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
    userdata = users.find_one({ "disid": str(member.id), "guild": f"{member.guild.id}" })
    if userdata["view"] == "false":
        return
    if before.channel == None and after.channel != None:
        if (before.mute == False and after.mute == False) and (before.self_mute == False and after.self_mute == False):
            foundChannel = False
            for elem in userdata["v_channels"]:
                for channel, time_c in list(elem.items()):
                    if channel == str(after.channel.id):
                        foundChannel = True 
                        break
            if foundChannel == False:
                users.update_one({"disid": str(member.id), "guild": str(member.guild.id)}, { "$push": { "v_channels": { str(after.channel.id): 0 } } })
        users.update_one({ "disid": str(member.id), "guild": f"{member.guild.id}" }, { "$set": { "voice_state": "1", "last_time": str(x)  } })
        #print(str(member) + " вошел в гк") 
    if (before.channel != None and after.channel != None) and before.channel != after.channel:
        lastt = int(userdata["last_time"])
        voicen = x - lastt
        if (before.mute == False and after.mute == False) and (before.self_mute == False and after.self_mute == False):
            foundChannel1 = False
            foundChannel = False
            time_n = 0
            for elem in userdata["v_channels"]:
                for channel, time_c in list(elem.items()):
                    if channel == str(before.channel.id):
                        foundChannel1 = True
                        time_n = time_c
                        break
                for channel, time_c in list(elem.items()):
                    if channel == str(after.channel.id):
                        foundChannel = True
                        break
            if foundChannel1 == False:
                if after.channel.id != 787001614061928468:
                    users.update_one({"disid": str(member.id), "guild": str(member.guild.id)}, { "$push": { "v_channels": { str(before.channel.id): 0  } } })
            if foundChannel == False:
                if after.channel.id != 787001614061928468:
                    users.update_one({"disid": str(member.id), "guild": str(member.guild.id)}, { "$push": { "v_channels": { str(after.channel.id): 0  } } })
            users.update_one({ "disid": str(member.id), "guild": f"{member.guild.id}" }, { "$set": { f"v_channels.$[element].{before.channel.id}": time_n + voicen, "s_voice": userdata["s_voice"] + voicen, "voice_time": int(userdata["voice_time"]) + voicen, "last_time": str(x) } }, array_filters=[ { f"element.{before.channel.id}": time_n } ])
            week_stats.update_one({ "id": f"{member.id}" }, { "$set": { "voice": uws["voice"] + voicen } })
        #print(str(member) + " перешел в другой гк")
    if before.channel != None and after.channel == None:
        lastt = int(userdata["last_time"])
        voicen = x - lastt
        if (before.mute == False and after.mute == False) and (before.self_mute == False and after.self_mute == False):
            foundChannel = False
            time_n = 0
            for elem in userdata["v_channels"]:
                for channel, time_c in list(elem.items()):
                    if channel == str(before.channel.id):
                        foundChannel = True
                        time_n = time_c
                        break
            if foundChannel == False:
                users.update_one({"disid": str(member.id), "guild": str(member.guild.id)}, { "$push": { "v_channels": { str(before.channel.id): 0 } } })
            users.update_one({ "disid": str(member.id), "guild": f"{member.guild.id}" }, { "$set": { f"v_channels.$[element].{before.channel.id}": time_n + voicen, "s_voice": userdata["s_voice"] + voicen, "voice_time": int(userdata["voice_time"]) + voicen, "last_time": str(x), "voice_state": "0" } }, array_filters=[ { f"element.{before.channel.id}": time_n } ])
            week_stats.update_one({ "id": f"{member.id}" }, { "$set": { "voice": uws["voice"] + voicen } })
    if before.channel != None and after.channel != None and (before.mute == False and after.mute == True and before.self_mute != True and after.self_mute != True) or (before.self_mute == False and after.self_mute == True and before.mute != True and after.mute != True):
        x = int(time.time())
       
        lastt = int(userdata["last_time"])
        voice = int(userdata["voice_time"])
        
        voicen = x - lastt
        voice += voicen
        foundChannel = False
        time_n = 0
        if before.channel == None:
            return None
        for elem in userdata["v_channels"]:
            for channel, time_c in list(elem.items()):
                if channel == str(before.channel.id):
                    foundChannel = True
                    time_n = time_c
                    break
        if foundChannel == False:
            users.update_one({"disid": str(member.id), "guild": str(member.guild.id)}, { "$push": { "v_channels": { str(before.channel.id): 0 } } })
        users.update_one({ "disid": str(member.id), "guild": f"{member.guild.id}" }, { "$set": { f"v_channels.$[element].{before.channel.id}": time_n + voicen, "s_voice": userdata["s_voice"] + voicen, "voice_time": voice, "last_time": str(x) } }, array_filters=[ { f"element.{before.channel.id}": time_n } ])
        week_stats.update_one({ "id": f"{member.id}" }, { "$set": { "voice": uws["voice"] + voicen } })
        #print(str(member) + " выключил микро")
    if before.channel != None and after.channel != None and (before.mute == True and after.mute == False and before.self_mute == False and after.self_mute == False) or (before.self_mute == True and after.self_mute == False and before.mute != True and after.mute != True):
        x = int(time.time())
        users.update_one({ "disid": str(member.id), "guild": f"{member.guild.id}" }, { "$set": { "last_time": str(x) } })
        #print(str(member) + " включил микро")

@client.event
async def on_guild_channel_create(channel):
    if servers.count_documents({"server": str(channel.guild.id)}) == 0:
        overwrite = discord.Permissions()
        overwrite.send_messages = False
        overwrite.speak = False
        role = await channel.guild.create_role(name="Muted", permissions=overwrite)
        try:
            await channel.set_permissions(role, send_messages = False,
                                            speak = False)
        except:
            pass
        for channel in channel.guild.channels:
            overwrite = discord.Permissions()
            overwrite.send_messages = False
            overwrite.speak = False
            try:
                await channel.set_permissions(role, send_messages = False,
                                                speak = False)
            except:
                pass
        servers.insert_one({"server": str(channel.guild.id), "roleid_mute": str(role.id), "prefix": ".", "lang": "en", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "You got {level} level on the {server} server!", "lvlChannelType": "dm", "lvlChannel": "" })
    else:
        data = servers.find_one({"server": str(channel.guild.id)})
        role = discord.utils.get(channel.guild.roles, id=int(data["roleid_mute"]))
        try:
            await channel.set_permissions(role, send_messages = False,
                                                    speak = False)
        except:
            pass

@client.event
async def on_raw_message_edit(payload):
    try:
        message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    except:
        return

    if message.author == client.user:
        return

    if message.author.bot and str(message.author.id) not in config.BOTS_REWARD:
        return

    if message.guild != None and message.guild.id == 604083589570625555:
        def check_link(regex, value):
            for b in list(string.punctuation):
                while value.endswith(b):
                    value = value[:-1]
            find_urls_in_string = re.compile(regex, re.IGNORECASE)
            url_check = find_urls_in_string.search(value)
            if url_check is not None:
                return True
            else:
                return False
        alink = message.content.lower()
        regex = r'((?:(https?|s?ftp):\/\/)?(?:www\.)?((?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)([A-Z]{2,6})|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(?::(\d{1,5}))?(?:(\/\S+)*))'
        urls = re.findall(r'(https?://[^\s]+)', message.content)
        urls2 = re.findall(r'([^\s]+)', message.content)
        urls1_check = list(filter(lambda x: check_link(regex, x) is True, urls))
        urls2_check = list(filter(lambda x: check_link(regex, x) is True, urls2))
        ed_phrase = alink

        for key, value in dict_letters.items():
            for letter in value:
                for phr in ed_phrase:
                    if letter == phr:
                        ed_phrase = ed_phrase.replace(phr, key)
        if ('кто успел, тот и съел' in ed_phrase or ('<@&604083589570625555>' in alink or '@everyone' in alink) or 
        (("steam" in alink or "стим" in alink or "discord" in alink or "дискорд" in alink) and 
        ("giveaway" in alink or "раздач" in alink or "скины" in alink or "нитро" in alink or "nitro" in alink))) and (len(urls1_check) > 0 or len(urls2_check) > 0):
            staffrole = message.guild.get_role(761771540181942273)
            if message.author.guild_permissions.administrator is False and staffrole not in message.author.roles:
                e = discord.Embed(title="", description="Попытался отправить скам ссылку и был забанен.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar_url}")
                await message.channel.send(embed=e)
                es = discord.Embed(title="", color=discord.Color(0x2F3136))
                es.description = """Приветствую, вас взломали и вы были забанены за скам на Genshin Impact [RU COM]

Что вам нужно сделать на данный момент? <a:1PaimonSpinner:772748541213933618>  

1) Поменяйте пароль от вашего Discord аккаунта.
2) Смените почту от вашего Discord аккаунта.
3) После проделанных действий напишите в лс `Японская Псина#0777` для вашей дальнейшей разблокировки.

P.s - Также советуем вам удалить все плагины установленные на Discord и другие подозрительные файлы."""
                es.timestamp = datetime.datetime.utcnow()
                #es.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar_url}")
                try:
                    await message.author.send(embed=es)
                except:
                    pass
                try:
                    await message.delete()
                except:
                    pass
                await message.author.ban(reason="scam link", delete_message_days=1)
                print(f"{message.author} - {message.content}")


    if message.guild != None and message.guild.id == 604083589570625555:
        regex = r'((?:(https?|s?ftp):\/\/)?(?:www\.)?((?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)([A-Z]{2,6})|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(?::(\d{1,5}))?(?:(\/\S+)*))'
        urls = re.findall(r'(https?://[^\s]+)', message.content)
        urls2 = re.findall(r'([^\s]+)', message.content)
        check_url = False
        if urls != [] or urls2 != []:
            for url in urls:
                for b in list(string.punctuation):
                    while url.endswith(b):
                        url = url[:-1]
                find_urls_in_string = re.compile(regex, re.IGNORECASE)
                url_check = find_urls_in_string.search(url)
                if url_check == None:
                    continue
                if url_check.groups()[5] != None:
                    if str(url_check.groups()[2]) == "discord.gg" or str(url_check.groups()[2]) == "discord.com":
                        try:
                            info = await client.fetch_invite(url)
                        except:
                            continue
                        if info.guild.id != 604083589570625555 and info.guild.id != 522681957373575168:
                            if not message.author.guild_permissions.administrator:
                                try:
                                    await message.delete()
                                except:
                                    pass
                                e = discord.Embed(title="", description="Попытался отправить инвайт ссылку на другой сервер и был забанен.", color=discord.Color(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar_url}")
                                await message.channel.send(embed=e)
                                await message.author.ban(reason="invite link in chat")
                                check_url = True
                                break
                            else:
                                break
                    else:
                        continue
                else:
                    continue
            if check_url == False:
                for url in urls2:
                    for b in list(string.punctuation):
                        while url.endswith(b):
                            url = url[:-1]
                    find_urls_in_string = re.compile(regex, re.IGNORECASE)
                    url_check = find_urls_in_string.search(url)
                    if url_check == None:
                        continue
                    if url_check.groups()[5] != None:
                        if str(url_check.groups()[2]) == "discord.gg" or str(url_check.groups()[2]) == "discord.com":
                            try:
                                info = await client.fetch_invite(url)
                            except:
                                continue
                            if info.guild.id != 604083589570625555 and info.guild.id != 522681957373575168:
                                if not message.author.guild_permissions.administrator:
                                    try:
                                        await message.delete()
                                    except:
                                        pass
                                    e = discord.Embed(title="", description="Попытался отправить инвайт ссылку на другой сервер и был забанен.", color=discord.Color(0x2F3136))
                                    e.timestamp = datetime.datetime.utcnow()
                                    e.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar_url}")
                                    await message.channel.send(embed=e)
                                    await message.author.ban(reason="invite link in chat")
                                    break
                                else:
                                    break
                        else:
                            continue
                    else:
                        continue

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.author.bot and str(message.author.id) not in config.BOTS_REWARD:
        return

    if message.guild != None and message.guild.id == 604083589570625555:
        def check_link(regex, value):
            for b in list(string.punctuation):
                while value.endswith(b):
                    value = value[:-1]
            find_urls_in_string = re.compile(regex, re.IGNORECASE)
            url_check = find_urls_in_string.search(value)
            if url_check is not None:
                return True
            else:
                return False
        alink = message.content.lower()
        regex = r'((?:(https?|s?ftp):\/\/)?(?:www\.)?((?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)([A-Z]{2,6})|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(?::(\d{1,5}))?(?:(\/\S+)*))'
        urls = re.findall(r'(https?://[^\s]+)', message.content)
        urls2 = re.findall(r'([^\s]+)', message.content)
        urls1_check = list(filter(lambda x: check_link(regex, x) is True, urls))
        urls2_check = list(filter(lambda x: check_link(regex, x) is True, urls2))

        ed_phrase = alink

        for key, value in dict_letters.items():
            for letter in value:
                for phr in ed_phrase:
                    if letter == phr:
                        ed_phrase = ed_phrase.replace(phr, key)
        if ('кто успел, тот и съел' in ed_phrase or ('<@&604083589570625555>' in alink or '@everyone' in alink) or 
        (("steam" in alink or "стим" in alink or "discord" in alink or "дискорд" in alink) and 
        ("giveaway" in alink or "раздач" in alink or "скины" in alink or "нитро" in alink or "nitro" in alink))) and (len(urls1_check) > 0 or len(urls2_check) > 0):
            staffrole = message.guild.get_role(761771540181942273)
            if message.author.guild_permissions.administrator is False and staffrole not in message.author.roles:
                e = discord.Embed(title="", description="Попытался отправить скам ссылку и был забанен.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar_url}")
                await message.channel.send(embed=e)
                es = discord.Embed(title="", color=discord.Color(0x2F3136))
                es.description = """Приветствую, вас взломали и вы были забанены за скам на Genshin Impact [RU COM]

Что вам нужно сделать на данный момент? <a:1PaimonSpinner:772748541213933618>  

1) Поменяйте пароль от вашего Discord аккаунта.
2) Смените почту от вашего Discord аккаунта.
3) После проделанных действий напишите в лс `Японская Псина#0777` для вашей дальнейшей разблокировки.

P.s - Также советуем вам удалить все плагины установленные на Discord и другие подозрительные файлы."""
                es.timestamp = datetime.datetime.utcnow()
                #es.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar_url}")
                try:
                    await message.author.send(embed=es)
                except:
                    pass
                try:
                    await message.delete()
                except:
                    pass
                await message.author.ban(reason="scam link", delete_message_days=1)
                print(f"{message.author} - {message.content}")

    if message.guild != None and message.guild.id == 604083589570625555:
        regex = r'((?:(https?|s?ftp):\/\/)?(?:www\.)?((?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)([A-Z]{2,6})|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(?::(\d{1,5}))?(?:(\/\S+)*))'
        urls = re.findall(r'(https?://[^\s]+)', message.content)
        urls2 = re.findall(r'([^\s]+)', message.content)
        check_url = False
        if urls != [] or urls2 != []:
            for url in urls:
                for b in list(string.punctuation):
                    while url.endswith(b):
                        url = url[:-1]
                find_urls_in_string = re.compile(regex, re.IGNORECASE)
                url_check = find_urls_in_string.search(url)
                if url_check == None:
                    continue
                if url_check.groups()[5] != None:
                    if str(url_check.groups()[2]) == "discord.gg" or str(url_check.groups()[2]) == "discord.com":
                        try:
                            info = await client.fetch_invite(url)
                        except:
                            continue
                        if info.guild.id != 604083589570625555 and info.guild.id != 522681957373575168:
                            if not message.author.guild_permissions.administrator:
                                try:
                                    await message.delete()
                                except:
                                    pass
                                e = discord.Embed(title="", description="Попытался отправить инвайт ссылку на другой сервер и был забанен.", color=discord.Color(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar_url}")
                                await message.channel.send(embed=e)
                                await message.author.ban(reason="invite link in chat")
                                check_url = True
                                break
                            else:
                                break
                    else:
                        continue
                else:
                    continue
            if check_url == False:
                for url in urls2:
                    for b in list(string.punctuation):
                        while url.endswith(b):
                            url = url[:-1]
                    find_urls_in_string = re.compile(regex, re.IGNORECASE)
                    url_check = find_urls_in_string.search(url)
                    if url_check == None:
                        continue
                    if url_check.groups()[5] != None:
                        if str(url_check.groups()[2]) == "discord.gg" or str(url_check.groups()[2]) == "discord.com":
                            try:
                                info = await client.fetch_invite(url)
                            except:
                                continue
                            if info.guild.id != 604083589570625555 and info.guild.id != 522681957373575168:
                                if not message.author.guild_permissions.administrator:
                                    try:
                                        await message.delete()
                                    except:
                                        pass
                                    e = discord.Embed(title="", description="Попытался отправить инвайт ссылку на другой сервер и был забанен.", color=discord.Color(0x2F3136))
                                    e.timestamp = datetime.datetime.utcnow()
                                    e.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar_url}")
                                    await message.channel.send(embed=e)
                                    await message.author.ban(reason="invite link in chat")
                                    break
                                else:
                                    break
                        else:
                            continue
                    else:
                        continue
    
token = config.TOKEN
client.run(str(token))