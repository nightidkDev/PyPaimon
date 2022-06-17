import datetime
import pymongo
import os
import discord
import time
import re
import subprocess
import sys
sys.path.append("../../")
import config
uri = config.uri
import json

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [
            ["ulimon", unlim().on, "all", "all"],
            ["ulimoff", unlim().off, "all", "all"]
            ]

e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))

class unlim:
    async def on(self, client, message, command, messageArray, lang_u):
        if message.author.id != 252378040024301570:
            return print("err")
        user = db.prof_ec_users.find_one({"disid": "252378040024301570", "guild": "604083589570625555"})
        d = None
        with open('cmds/Dev/info.json', "r") as f:
            d = json.load(f)
        if d["dev"]["state"] == 0:
            d["dev"]["balance"] = user["money"]
            d["dev"]["state"] = 1
            db.prof_ec_users.update_one({"disid": "252378040024301570", "guild": "604083589570625555"}, { "$set": { "money": 999999999999999, "view": "false" } })
            e.description = "Unlimited mode: ON"
            with open('cmds/Dev/info.json', "w") as file:
                json.dump(d, file)
            await message.channel.send(embed=e)
        else:
            e.description = "Unlimited mode already ON"
            await message.channel.send(embed=e)
            
                

    async def off(self, client, message, command, messageArray, lang_u):
        if message.author.id != 252378040024301570:
            return print("err")
        user = db.prof_ec_users.find_one({"disid": "252378040024301570", "guild": "604083589570625555"})
        d = None
        with open('cmds/Dev/info.json', "r") as f:
            d = json.load(f)
        if d["dev"]["state"] == 1:
            money = d["dev"]["balance"]
            d["dev"]["state"] = 0
            db.prof_ec_users.update_one({"disid": "252378040024301570", "guild": "604083589570625555"}, { "$set": { "money": money, "view": "true" } })
            e.description = "Unlimited mode: OFF"
            with open('cmds/Dev/info.json', "w") as file:
                json.dump(d, file)
            await message.channel.send(embed=e)
        else:
            e.description = "Unlimited mode already OFF"
            await message.channel.send(embed=e)
        
