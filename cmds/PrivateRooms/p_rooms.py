import datetime
import pymongo
import os
import discord
import time
import random
import sys
sys.path.append("../../")
from libs import Builders
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
privates = db.privates

def init():
    return [
               ["voicelimit|vlimit|vlim|vl", control().limit, "flood", "all"],
               ["voicename|vname|vn", control().name, "flood", "all"],
               ["voiceban|vban|vb", control().ban, "flood", "all"],
               ["voiceunban|vunban|vub", control().unban, "flood", "all"]
           ]

class control:
    async def limit(self, client, message, command, messageArray, lang_u):
        e = discord.Embed(color=discord.Colour(0x2F3136))
        e.set_author(name=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        if message.author.voice == None:
            e.description = "Ты не находишься в голосовом канале."
            return await message.channel.send(embed=e)
        owner_room = None
        if privates.count_documents({"id": str(message.author.voice.channel.id)}) != 0:
            owner_room = message.guild.get_member(int(privates.find_one({"id": str(message.author.voice.channel.id)})["owner"]))
        if privates.count_documents({"owner": str(message.author.id), "guild": str(message.guild.id)}) == 0 or message.author != owner_room:
            e.description = "Ты находишься не в своем личном мире."
            return await message.channel.send(embed=e)
        if len(messageArray) == 0 or messageArray[0] == "":
            e.description = "Укажите лимит, который нужно поставить. (Максимальный лимит: 99)\n`0` для удаления лимита."
            return await message.channel.send(embed=e)
        try:
            limit = int(messageArray[0])
        except:
            e.description = "Лимит может состоять только из чисел от 0 до 99!"
            return await message.channel.send(embed=e)
        if limit < 0 or limit >= 100:
            e.description = "Укажите лимит, который нужно поставить. (Максимальный лимит: 99)\n`0` для удаления лимита."
            return await message.channel.send(embed=e)
        try:
            channel = message.author.voice.channel
            await channel.edit(user_limit=limit)
            e.description = "Лимит изменен."
            await message.channel.send(embed=e)
        except:
            pass

    async def name(self, client, message, command, messageArray, lang_u):
        e = discord.Embed(color=discord.Colour(0x2F3136))
        e.set_author(name=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        if message.author.voice == None:
            e.description = "Ты не находишься в голосовом канале."
            return await message.channel.send(embed=e)
        owner_room = None
        if privates.count_documents({"id": str(message.author.voice.channel.id)}) != 0:
            owner_room = message.guild.get_member(int(privates.find_one({"id": str(message.author.voice.channel.id)})["owner"]))
        if privates.count_documents({"owner": str(message.author.id), "guild": str(message.guild.id)}) == 0 or message.author != owner_room:
            e.description = "Ты находишься не в своем личном мире."
            return await message.channel.send(embed=e)
        if len(messageArray) == 0 or messageArray[0] == "":
            e.description = "Укажите название, котороу нужно установить."
            return await message.channel.send(embed=e)
        name_i = " ".join(messageArray)
        if len(name_i) > 999:
            e.description = "Максимальный лимит символов в названии - 999."
            return await message.channel.send(embed=e)
        try:
            channel = message.author.voice.channel
            name = channel.name[:2] + name_i
            await channel.edit(name=name)
            e.description = "Название изменено."
            await message.channel.send(embed=e)
        except:
            e.description = "Что то пошло не так при смене названия твоего личного мира, возможно ты слишком часто используешь эту команду. Подожди 2 минуты и попробуй снова!"
            await message.channel.send(embed=e)

    async def ban(self, client, message, command, messageArray, lang_u):
        e = discord.Embed(color=discord.Colour(0x2F3136))
        e.set_author(name=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        if message.author.voice == None:
            e.description = "Ты не находишься в голосовом канале."
            return await message.channel.send(embed=e)
        owner_room = None
        if privates.count_documents({"id": str(message.author.voice.channel.id)}) != 0:
            owner_room = message.guild.get_member(int(privates.find_one({"id": str(message.author.voice.channel.id)})["owner"]))
        if privates.count_documents({"owner": str(message.author.id), "guild": str(message.guild.id)}) == 0 or message.author != owner_room:
            e.description = "Ты находишься не в своем личном мире."
            return await message.channel.send(embed=e)
        if len(messageArray) == 0 or len(message.mentions) == 0:
            e.description = "Укажите пользователя, которого хотите забанить в своем личном мире."
            return await message.channel.send(embed=e)
        if message.mentions[0] == message.author:
            e.description = "Укажите пользователя, которого хотите забанить в своем личном мире, а не себя."
            return await message.channel.send(embed=e)
        if message.mentions[0].voice == None or message.mentions[0].voice.channel != message.author.voice.channel:
            e.description = "Пользователь не находится в твоем личном мире."
            return await message.channel.send(embed=e)
        voice = message.author.voice.channel
        user = message.mentions[0]
        create_voice = message.guild.get_channel(768372905146843147)
        await voice.set_permissions(user, connect=False,
                                          speak=False)
        try:
            await user.edit(voice_channel=create_voice)
        except:
            pass
        e.description = f"<@!{user.id}> был забанен в твоем личном мире."
        await message.channel.send(embed=e)
    
    async def unban(self, client, message, command, messageArray, lang_u):
        e = discord.Embed(color=discord.Colour(0x2F3136))
        e.set_author(name=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        if message.author.voice == None:
            e.description = "Ты не находишься в голосовом канале."
            return await message.channel.send(embed=e)
        owner_room = None
        if privates.count_documents({"id": str(message.author.voice.channel.id)}) != 0:
            owner_room = message.guild.get_member(int(privates.find_one({"id": str(message.author.voice.channel.id)})["owner"]))
        if privates.count_documents({"owner": str(message.author.id), "guild": str(message.guild.id)}) == 0 or message.author != owner_room:
            e.description = "Ты находишься не в своем личном мире."
            return await message.channel.send(embed=e)
        if len(messageArray) == 0 or len(message.mentions) == 0:
            e.description = "Укажите пользователя, которого хотите забанить в своем личном мире."
            return await message.channel.send(embed=e)
        if message.mentions[0] == message.author:
            e.description = "Укажите пользователя, которого хотите забанить в своем личном мире, а не себя."
            return await message.channel.send(embed=e)
        if message.author.voice.channel.permissions_for(message.mentions[0]).connect == True:
            e.description = "Пользователь не заблокирован в твоем личном мире."
            return await message.channel.send(embed=e)
        voice = message.author.voice.channel
        user = message.mentions[0]
        await voice.set_permissions(user, overwrite=None)
        e.description = f"<@!{user.id}> был разбанен в твоем личном мире."
        await message.channel.send(embed=e)

