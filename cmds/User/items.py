import datetime
import pymongo
import os
import discord
from discord import Embed
import time
import random
import sys
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

users = db.prof_ec_users

def check_bar(member, bar):
    if int(bar) == member["theme"]:
        return "Надето"
    else:
        return "Снято"

def init():
    return [
                ["market", market().open, "flood", "owner"],
                ["items", items_inv().open, "flood", "owner"],
                ["set", items_inv().seti, "flood", "owner"],
                ["unset", items_inv().unseti, "flood", "owner"],
                ["cases", cases().open, "flood", "owner"]
            ]

class items_inv:
    def __init__(self):
        pass

    async def open(self, client, message, command, messageArray, lang_u):
        user = users.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
        items_list = user["inv"]
        items_str = "\n".join(f"{i + 1}. {items_list[i]['name']}" for i in range(len(items_list)))
        if items_str == "":
            items_str = "Ничего нет."
        e = Embed(title="Инвентарь предметов", description=items_str, color=discord.Color(0x2F3136))
        await message.channel.send(embed=e)

    async def seti(self, client, message, command, messageArray, lang_u):
        pass

    async def unseti(self, client, message, command, messageArray, lang_u):
        pass

class market:
    def __init__(self):
        pass

    async def open(self, client, message, command, messageArray, lang_u):
        pass

class cases:
    def __init__(self):
        pass

    async def open(self, client, message, command, messageArray, lang_u):
        pass
