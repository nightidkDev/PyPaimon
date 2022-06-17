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

def init():
    return [["language|lang", language().switch, "flood", "all"]]

class language:
    def __init__(self):
        pass
    async def switch(self, client, message, command, messageArray, lang):
        if message.author.guild_permissions.administrator == False:
            if lang == "ru":
                return await message.channel.send("Данная команда доступна только для администраторов сервера.")
            else:
                return await message.channel.send("This command is only available for server administrators.")
        if db.server.count_documents({"server": f"{message.guild.id}"}) == 0:
            if message.guild.region == discord.VoiceRegion.russia:
                db.server.insert_one({"server": str(message.guild.id), "roleid_mute": str(role.id), "prefix": ".", "lang": "ru", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "Ты получил {level} уровень на сервере {server}!", "lvlChannelType": "dm", "lvlChannel": "" })
            else:
                db.server.insert_one({"server": str(message.guild.id), "roleid_mute": str(role.id), "prefix": ".", "lang": "en", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "You got {level} level on the {server} server!", "lvlChannelType": "dm", "lvlChannel": "" })
        if len(messageArray) == 0:
            if lang == "en":
                e = discord.Embed(title="Language", description=f"Selected language: English\n\nЧтобы его сменить на Русский пропишите: .lang ru", color=discord.Color(0x2F3136))
            elif lang == "ru":
                e = discord.Embed(title="Язык", description=f"Выбранный язык: Русский\n\nTo change it to English write this: .lang en", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed=e)
        if messageArray[0] != "ru" and messageArray[0] != "en":
            if lang == "en":
                e = discord.Embed(title="Invalid input", description=f"Choose either 'en' or 'ru'", color=discord.Color(0x2F3136))
            elif lang == "ru":
                e = discord.Embed(title="Неверный ввод", description=f"Выберите либо 'en', либо 'ru'", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed=e)
        if messageArray[0] == "ru":
            if lang == "ru":
                e = discord.Embed(title="Ошибка", description=f"На сервере уже установленный данный язык.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            else:
                coll = db.server
                coll.update_one({ "server": f"{message.guild.id}" }, {'$set': {"lang": 'ru'}})
                e = discord.Embed(title="Смена языка", description=f"Язык изменён на Русский", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=e)
        if messageArray[0] == "en":
            if lang == "en":
                e = discord.Embed(title="Error", description=f"Server language is already English", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=e)
            else:
                coll = db.server
                coll.update_one({ "server": f"{message.guild.id}" }, {'$set': {"lang": 'en'}})
                e = discord.Embed(title="Changing the language", description=f"Language changed to English", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=e)
