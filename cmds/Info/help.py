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
    return [
            ["help|h", info().help, "flood", "all"],
            ["rlist", info().rlist, "flood", "all", "help", "команды-реакции"]
            ]

async def probels_count(cmd, probels_c):
    kk = 0
    probels = "   "
    while probels_c - (len(cmd) + 1) >= kk:
        probels += " "
        kk += 1
    return probels

def check_help(x):
    try:
        return True if x[4] == "help" else False
    except:
        return False

def check_rlist(x):
    try:
        return True if x[4] == "rlist" else False
    except:
        return False

class info():
    def __init__(self):
        pass

    async def help(self, client, message, command, messageArray, lang_u):
        #if str(message.author.id) not in config.ADMINS:
            #    return None
        #    return message.channel.send("Access denied. This part of the command is incomplete.")
        commands = config.commands
        commandsx = [item for sublist in commands for item in sublist]
        commandshelp = list(filter(lambda x: check_help(x), commandsx))
        e = discord.Embed(title="Помощь", description="```", color=discord.Color(0x2F3136))
        for cmd in commandshelp:
            try:
                inpcmd = f"{cmd[0].split('|')[0]}"
                coms = cmd[0].split("|")
                if len(coms) >= 2:
                    inpcmd += " ("
                    b = 0
                    for i in range(1, len(coms)):
                        if b == 0:
                            inpcmd += f"{coms[i]}"
                            b += 1
                        else:
                            inpcmd += f", {coms[i]}"
                    inpcmd += ")"
                    
                e.description += f".{inpcmd} - {cmd[5]}\n"
            except:
                pass
        e.description += "```"
        try:
            await message.author.send(embed=e)
        except:
            await message.channel.send(f"<@!{message.author.id}>, не удалось отправить сообщение в личные сообщения, проверьте свои настройки.")
        await message.delete()

    async def rlist(self, client, message, command, messageArray, lang_u):
        #if str(message.author.id) not in config.ADMINS:
            #    return None
        #    return message.channel.send("Access denied. This part of the command is incomplete.")
        
        commands = config.commands
        commandsx = [item for sublist in commands for item in sublist]
        commandsrlist = list(filter(lambda x: check_rlist(x), commandsx))
        e = discord.Embed(title="Помощь", description="```", color=discord.Color(0x2F3136))

        e = discord.Embed(title="Команды-эмоции", description="", color=discord.Color(0x2F3136))
        n = 1
        probels_c = 1
        k = 0
        e.description += "```"
        
        for cmd in commandsrlist:
            if probels_c < len(cmd[0]):
                probels_c = len(cmd[0])
            k += 1
        count = int(k / 10)
        while k / 10 - count > 0:
            count += 1
        o = 0
        probels_c += 1
        for cmd in commandsrlist:
            try:
                if o < int(count):
                    probels = await probels_count(cmd[0], probels_c)
                    e.description += f"{config.PREFIX}{cmd[0]}{probels}"
                    o += 1
                elif o >= int(count):
                    probels = await probels_count(cmd[0], probels_c)
                    e.description += f"\n{config.PREFIX}{cmd[0]}{probels}"
                    o = 1
            except:
                pass
        e.description += "```"
        try:
            await message.author.send(embed=e)
        except:
            await message.channel.send(f"<@!{message.author.id}>, не удалось отправить сообщение в личные сообщения, проверьте свои настройки.")
        try:
            await message.delete()
        except:
            pass
        