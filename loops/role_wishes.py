import discord
from discord.ext import commands
from discord_components import *
import datetime
import time
import random
import os
import sys
sys.path.append("../../")
import config

# DataBase
import pymongo
login_url = config.uri2
mongoclient = pymongo.MongoClient(login_url)
db = mongoclient.aimi
roles_wishes = db.roles_wishes
special_wishes = db.special_wishes
chats_wishes = db.chats_wishes
voices_wishes = db.voices_wishes
banners_wishes = db.banners_wishes
packs_wishes = db.packs_wishes

async def role_wishes(bot):
    for role in roles_wishes.find():
        x = int(time.time())
        if role["timeout"] <= x:
            guild = bot.get_guild(604083589570625555)
            rolew = guild.get_role(int(role['roleID']))
            try:
                await rolew.delete()
            except:
                pass
            roles_wishes.delete_one({ "roleID": role['roleID'] })

async def specials_wishes(bot):
    for special in special_wishes.find():
        x = int(time.time())
        if special["timeout"] <= x:
            guild = bot.get_guild(604083589570625555)
            rolew = guild.get_role(config.specialRoleID)
            member = guild.get_member(int(special["id"]))
            await member.remove_roles(rolew)
            special_wishes.delete_one({ "id": special['id'] })

async def chat_wishes(bot):
    for chat in chats_wishes.find():
        x = int(time.time())
        if chat["timeout"] <= x:
            guild = bot.get_guild(604083589570625555)
            try:
                channel = guild.get_channel(int(chat['chatID']))
                await channel.delete()
            except:
                pass
            chats_wishes.delete_one({ "chatID": chat['chatID'] })

async def voice_wishes(bot):
    for voice in voices_wishes.find():
        x = int(time.time())
        if voice["timeout"] <= x:
            guild = bot.get_guild(604083589570625555)
            try:
                channel = guild.get_channel(int(voice['voiceID']))
                await channel.delete()
            except:
                pass
            voices_wishes.delete_one({ "voiceID": voice['voiceID'] })

async def voice_wishes_hour(bot):
    for voice in voices_wishes.find():
        x = int(time.time())
        if voice["timeoutHour"] <= x:
            guild = bot.get_guild(604083589570625555)
            try:
                channel = guild.get_channel(int(voice['voiceID']))
                if len(channel.members) > 0:
                    voices_wishes.update_one({ "voiceID": voice['voiceID'] }, { "$inc": { "timeoutHour": 3600 } })
                else:
                    try:
                        await channel.delete()
                    except:
                        pass
            except:
                pass
            