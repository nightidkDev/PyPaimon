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
    return [["setlevel", setlevel, "all", "owner"]]

async def setlevel(client, message, command, messageArray, lang_u):
    if str(message.author.id) not in config.ADMINS:
        return

    users = db.prof_ec_users

    try:
        level = int(messageArray[0]) - 1
        lvl = int(messageArray[0])
    except:
        return await message.channel.send("err")
    if lvl <= 0: 
        return await message.channel.send("err")
    exp = 5 * (level * level) + 50 * level + 100
    nlvl_ins = lvl * 10 + 45

    ranks = [
                [100, "775802151405355048"],
                [90, "775800915537166346"],
                [80, "775797926869598249"],
                [70, "775797342862573638"],
                [60, "775796352163774496"],
                [50, "775795871454724096"],
                [40, "775795087631450112"],
                [30, "775794183767851059"],
                [20, "775788094368251944"],
                [10, "775786187604361256"],
                [5, "775785658286997514"]                        
            ]
    last_role = None
    index_role = None
    role_lvl = None
    for rank in ranks:
        if lvl >= rank[0]:
            role_lvl = message.guild.get_role(int(rank[1]))
            index_role = ranks.index([rank[0], rank[1]])
            
            if str(message.author.id) not in []:
                if role_lvl not in message.author.roles:
                    await message.author.add_roles(role_lvl)
            break
    if index_role != len(ranks) - 1:
        for rank in ranks:
            role_check = message.guild.get_role(int(rank[1]))
            if role_check in message.author.roles:
                if role_lvl == role_check:
                    continue
                await message.author.remove_roles(role_check)
        
            
    
    users.update_one({ "disid": f"{message.author.id}", "guild": "604083589570625555" }, { "$set": { "exp": 0, "nexp": str(exp), "lvl": lvl, "nlvl": str(nlvl_ins) } })

    await message.channel.send(f"Был установлен {lvl} уровень.")
    


    

