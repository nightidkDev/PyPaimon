import datetime
import pymongo
import os
import discord
import time
import re
import sys
import json
sys.path.append("../../")
import config 
from libs import Profile
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
users = db.prof_ec_users

def toFixed(numObj, digits=0):
    return float(f"{numObj:.{digits}f}")
        
def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}d {h:02d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{h:02d}:{m:02d}:{s:02d}"    

def money_kkk(number):

    str_m = "{:,}".format(int(number))
    return str_m.replace(",", " ")
        
def init():
    return [["bal|balance|$", bal, "flood", "all"]]
        

async def bal(client, message, command, messageArray, lang_u):
    check = await Profile.Profile().check_member(message.guild, messageArray)
    check_name = await Profile.Profile().check_member_name(message, messageArray)

    user = message.mentions[0] if len(message.mentions) != 0 else check if check is not None else check_name if check_name is not None else message.author


    money_l = users.find_one({ "disid": str(user.id), "guild": f"{message.guild.id}" })["money"]
    #money_d = users.find_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" })["donate_money"]
    money_emoji = client.get_emoji(int(config.MONEY_EMOJI))
    money_l = money_kkk(int(money_l))
    if user.id == 252378040024301570:
        d = None
        with open('cmds/Dev/info.json', "r") as f:
            d = json.load(f)
        if d["dev"]["state"] == 1:
            money_l = "@Unlimited"

    if user.id == 856847328043859978:
        money_l = "Неизвестно."

    e = discord.Embed(title=f"Баланс • {user.name}", description="", color=discord.Color(0x2F3136))
    e.add_field(name=f"{money_emoji} Примогемы", value=f"```css\n{money_l}\n```", inline=True)
    e.set_thumbnail(url=user.avatar_url)
    e.timestamp = datetime.datetime.utcnow()
    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    await message.channel.send(embed=e)