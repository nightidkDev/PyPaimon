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
users_db = db.prof_ec_users

def init():
    return [
               ["fixview", view().fix, "all", "owner"]
           ]

class view:

    async def fix(self, client, message, command, messageArray, lang_u):
        guild = client.get_guild(604083589570625555)
        users = users_db.find({"view": "false", "guild": "604083589570625555" })
        lb_role = guild.get_role(767626360965038080)
        for user in users:
            member = guild.get_member(int(user["disid"]))
            if member == None:
                continue
            if lb_role in member.roles:
                continue
            if member.id == 418831356374810644:
                continue
            users_db.update_one({"disid": user["disid"], "guild": "604083589570625555" }, { "$set": { "view": "true" } })
        
        await message.channel.send("success")