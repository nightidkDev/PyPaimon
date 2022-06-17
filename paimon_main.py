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
import ast
import copy
import sqlite3
from _thread import start_new_thread

import discord
import discord.ext
from discord import utils
#import discord_components
#from discord_components import *
from PIL import Image, ImageDraw, ImageFont
import pymongo
import importlib
import cmds

import config
from cmds import Dev
from cmds import Staff
from cmds import Reactions
from cmds import Mod
from cmds import Economy
from cmds import Info
from cmds import User
from libs import Builders
from libs import Profile
from libs import DataBase
from libs import ReactionsOnMessage
from libs import SelectLib
from plugins import voice_money
from plugins import checkreact
from plugins import funcb
import cmds
import libs
import handler
import rhandler

uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
uri2 = config.uri2
mongoclient2 = pymongo.MongoClient(uri2)
db2 = mongoclient2.aimi

# h8bai51akqg6 = []

print("Loading...")
config.commands, config.category = handler.load()

def check_rlist(x):
    try:
        return True if x[4] == "rlist" else False
    except:
        return False

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

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

intents = discord.Intents().all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    await client.wait_until_ready()
    try:
        d = None
        with open("restart_info.json", "r") as ri:
            d = json.load(ri)
        c = client.get_channel(d["restart_channel"])
        message_restart = await c.fetch_message(d["restart_message"])

        e3 = discord.Embed(title="", description="Перезагрузка завершена, все команды снова работают.", color=discord.Colour(0xff0000))
        time_r = int(time.time()) - d['restart']
        e3.set_footer(text=f"Перезагрузка заняла {time_r} {funcb.declension([ 'секунда', 'секунды', 'секунд' ], time_r)}.")
        await message_restart.edit(embed=e3)
    except BaseException as e:
        pass
    try:
        with open("/root/bots/restart_info.json") as f:
            restart_data = json.load(f)
        restart_data['paimon']['status'] = 1
        restart_data['paimon']['time'] = int(time.time())
        with open("/root/bots/restart_info.json", "w") as f:
            json.dump(restart_data, f)
        channel = await bot.get_user(751145877242118246)
        await channel.send("p\ready")
    except BaseException:
        pass
    #DiscordComponents(client)
    print(f"[{datetime.datetime.utcfromtimestamp(int(time.time()) + 10800).strftime('%H:%M:%S')}] Запустилась главная Paimon.exe <3")

@client.event
async def on_message(message):
    global h8bai51akqg6


    if message.author == client.user and message.channel.id != 822510348808486952 and message.channel.id != 767015636354203659:
        return

    if message.author.bot and str(message.author.id) not in config.BOTS_REWARD and message.channel.id != 822510348808486952 and message.channel.id != 767015636354203659:
        return

    if message.guild is None:
        return

    if message.guild.id == 604083589570625555:
        lb = message.guild.get_role(767626360965038080)

        if lb in message.author.roles:
            return

    lang_u = "ru"

    server_coll = db.server
    if server_coll.count_documents({"server": f"{message.guild.id}"}) == 0:
            if message.guild.region == discord.VoiceRegion.russia:
                server_coll.insert_one({"server": str(message.guild.id), "roleid_mute": "0", "prefix": ".", "lang": "ru", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "Ты получил {level} уровень на сервере {server}!", "lvlChannelType": "dm", "lvlChannel": "" })
            else:
                server_coll.insert_one({"server": str(message.guild.id), "roleid_mute": "0", "prefix": ".", "lang": "en", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "You got {level} level on the {server} server!", "lvlChannelType": "dm", "lvlChannel": "" })
    prefix = server_coll.find_one({"server": f"{message.guild.id}" })["prefix"]

    if message.content == f"<@!{client.user.id}>" or message.content == f"<@{client.user.id}>":
        e = discord.Embed(title="Paimon.exe", description=f"Бот в рабочем состоянии.", color=discord.Color(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
        await message.channel.send(embed=e)


    if message.content.startswith(prefix):

        if message.author.id != 252378040024301570:
            e = discord.Embed(title="", description="В данный момент Паймон на технических работах.\nПриносим свои извинения за предоставленные неудобства.", color=discord.Color(0x2F3136))
            # return await message.channel.send(embed=e)

        lenPrefix = len(prefix)
        command = message.content[lenPrefix:]
        messageArray = command.strip().split()
        if messageArray == []:
            return None
        commandf = str(str(messageArray[0]).lower())
        commandf2 = str(messageArray[0])
        messageArray.remove(commandf2)

        if message.channel.id == 794660897271578625 and commandf2 != "tmute":
            return

        try:
            commands = config.commands
            commandsx = [item for sublist in commands for item in sublist]
            ind = [item[0].split("|") for sublist in commands for item in sublist]
            cmd = None
            for x in range(len(ind)):
                if commandf in ind[x]:
                    cmd = commandsx[x]
            #print(cmd)
            mute_role = message.guild.get_role(767025328405086218)
            lb_role = message.guild.get_role(767626360965038080)
            if mute_role in message.author.roles or lb_role in message.author.roles:
                commands1 = config.commands
                commandsx1 = [item for sublist in commands1 for item in sublist]
                commandsrlist = list(filter(lambda x: check_rlist(x), commandsx1))
                commandsrlistnames = list(map(lambda y: y[0], commandsrlist))
                if not message.content.startswith(".tmute") and message.content.lower().split(" ")[0][len(prefix):] not in commandsrlistnames and cmd:
                    if message.channel.id == 794660897271578625:
                        return
                    else:
                        e = discord.Embed(title="", description=f"Все команды, кроме `.tmute` и команд-реакций, запрещены в мьюте или локал бане.", color=0x2F3136)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                        await message.channel.send(embed=e)
                        time.sleep(3)
                        try:
                            await message.delete()
                        except:
                            pass
                        return
            if str(message.author.id) not in config.ADMINS:
                if message.channel.id in config.deny_channels:
                    return None
                if config.bot_status == "off":
                    #e = discord.Embed(title="", description="В данный момент бот перезагружается, пожалуйста, подождите.", color=discord.Color(0xff0000))
                    return
                if config.restart == 1:
                    e = discord.Embed(title="", description="В данный момент бот перезагружается, пожалуйста, подождите.", color=discord.Color(0xff0000))
                    return await message.channel.send(embed=e, delete_after=2.0)
                if cmd[2] == "flood":
                    if message.channel.id in config.NotFloodChannels:
                        return None
                if cmd[2] == "staff":
                    if message.channel.id != 738937369167921235:
                        return
                if cmd[3] == "work":
                    if message.author.id != 252378040024301570 and message.author.id != 214667168715898880:
                        e = discord.Embed(title="", description="В данный момент эта команда отключена.\n\nThis command is currently disabled.", color=discord.Color(0x2F3136))
                        return await message.channel.send(embed=e)
                if cmd[3] == "admins":
                    if message.author.guild_permissions.administrator == False and str(message.author.id) not in config.ADMINS:
                        return None
                if cmd[3] == "sadmins":
                    sa = message.guild.get_role(767084198816776262)
                    if sa not in message.author.roles and message.author.guild_permissions.administrator is False and str(message.author.id) not in config.ADMINS:
                        return None
                elif cmd[3] == "boost":
                    boost_role = message.guild.get_role(612661327101558796)
                    if boost_role not in message.author.roles:
                        e = discord.Embed(title="", description="Для доступа к данной команде вам нужно дать хотя бы 1 буст серверу.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        return await message.channel.send(embed=e)
                elif cmd[3] == "mods":
                    role = message.guild.get_role(761771540181942273)
                    if message.author.guild_permissions.administrator == False and role not in message.author.roles:
                        return None
                elif cmd[3] == "owner":
                    if str(message.author.id) not in config.ADMINS:
                        return None
                elif cmd[3] == "night":
                    if message.author.id != 252378040024301570:
                        return None
                elif cmd[3] == "bao":
                    if str(message.author.id) not in config.ADMINS and str(message.author.id) not in config.BOTS_REWARD:
                        return None
                elif cmd[3] == "G":
                    return None
                elif cmd[3] == "OZAS":
                    return None
                elif cmd[3] == ".":
                    admin_role = message.guild.get_role(760922443777835028)
                    if admin_role not in message.author.roles or message.author.guild_permissions.administrator == False:
                        return None
                #id_tokens = [
                #                "788857372201844746", "788855466339467264", "789156220057550910", "789156242563006464", "789155852891324486", "789157240178343987", "789158347227136040", "789154565458755585", "789158623314051092",
                #                "789159142697992253", "789156376306909216", "789156573091463228", "789155485164240906", "789161334578741290", "789161094656557087"
                #            ]
                #for token_id in id_tokens:
                #    u = client.get_user(int(token_id))
                #    if u is None:
                #        continue
                #    if (len(message.mentions) > 0 and message.mentions[0] == u) or (len(messageArray) > 0 and (messageArray[0] == str(u.id) or messageArray[0] == u.name or messageArray[0] == str(u))):
                #        try:
                #            return await message.delete()
                #        except:
                #            return None
            try:
                if len(message.mentions) > 0:
                    users = db.prof_ec_users
                    if users.count_documents({ "disid": str(message.mentions[0].id), "guild": f"{message.guild.id}" }) == 0:
                        x = int(time.time())
                        users.insert_one({ "disid": str(message.mentions[0].id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{message.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
            except:
                pass
            await cmd[1](client, message, command, messageArray, lang_u)
            try:
                if cmd[3] != "night" and cmd[4] != "rlist":
                    await funcb.deltime(message, 3)
            except BaseException as e:
                try:
                    if cmd is not None:
                        await funcb.deltime(message, 3)
                except:
                    pass
        except BaseException as e:
            print(f"{message.author.name} - {message.content} - {e}")


        messageArray.clear()

token = config.TOKEN
client.run(str(token))
