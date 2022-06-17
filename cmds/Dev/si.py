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
from libs import Profile
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def check(member, guild, role):
    role_g = guild.get_role(int(role))
    if role_g in member.roles:
        return "надето"
    else:
        return "снято"

def check_c(member, card):
    if int(card) == member["background"]:
        return " - надето"
    else:
        return ""


def check_w(member, guild, role):
    role_g = guild.get_role(int(role))
    if role_g in member.roles:
        return "надето"
    else:
        return "снято"

def init():
    return [["si|seeinventory", seeinventory, "all", "owner"]]

async def seeinventory(client, message, command, messageArray, lang_u):
    if str(message.author.id) not in config.ADMINS:
        return

    checku = await Profile.Profile().check_member(message.guild, messageArray)
    check_name = await Profile.Profile().check_member_name(message, messageArray)

    user = message.mentions[0] if len(message.mentions) != 0 else checku if checku is not None else check_name if check_name is not None else message.author
    if user is None:
        e = discord.Embed(title="", description=f"Пользователь не найден.", color=discord.Color(0x2F3136))
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await message.reply(embed=e)

    coll_user = db.prof_ec_users
    bgn = db.backgrounds
    userb = coll_user.find_one({ "disid": str(user.id), "guild": f"{message.guild.id}" })
    e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
    e.set_author(name=f"Инвентарь - {user}")
    inv = ""
    inv_c = 0
    for item in userb["inv"]:
        if item["type"] == "role":
            role = item["id"]
            inv += str(inv_c + 1) + f". <@&{role}> - {check(user, message.guild, role)}\n"
        elif item["type"] == "background":
            card = item["id"]
            bgn_item = bgn.find_one({ "id": card }) 
            custom = client.get_emoji(int(bgn_item["emoji"]))
            custom_name = bgn_item["name"]
            inv += str(inv_c + 1) + f". {custom} **{custom_name}**{check_c(userb, card)}\n"
        elif item["type"] == "waifu":
            role = item["id"]
            inv += str(inv_c + 1) + f". <@&{role}> - {check_w(user, message.guild, role)}\n"
            
            
        inv_c += 1
    if inv_c == 0:
        inv += "Пусто\n"
    e.description = inv
    e.timestamp = datetime.datetime.utcnow()
    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    await message.channel.send(embed=e)
    e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
    


    

