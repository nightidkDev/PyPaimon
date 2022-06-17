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
    return [["inv|inventory", inv_c().open, "flood", "all", "help", "инвентарь"],
                    ["eq|equip", inv_c().equip, "flood", "all", "help", "надеть предмет"],
                    ["uneq|unequip", inv_c().unequip, "flood", "all", "help", "снять предмет"]
                   ]

class inv_c:
    def __init__(self):
        pass

    async def open(self, client, message, command, messageArray, lang_u):
        coll_user = db.prof_ec_users
        bgn = db.backgrounds
        user = coll_user.find_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" })
        e = discord.Embed(title="Инвентарь", description="", color=discord.Color(0x2F3136))
        inv = ""
        inv_c = 0
        for item in user["inv"]:
            if item["type"] == "role":
                role = item["id"]
                inv += str(inv_c + 1) + f". <@&{role}> - {check(message.author, message.guild, role)}\n"
            elif item["type"] == "background":
                card = item["id"]
                bgn_item = bgn.find_one({ "id": card }) 
                custom = client.get_emoji(int(bgn_item["emoji"]))
                custom_name = bgn_item["name"]
                inv += str(inv_c + 1) + f". {custom} **{custom_name}**{check_c(user, card)}\n"
            elif item["type"] == "waifu":
                role = item["id"]
                inv += str(inv_c + 1) + f". <@&{role}> - {check_w(message.author, message.guild, role)}\n"
                
                
            inv_c += 1
        if inv_c == 0:
            inv += "Пусто\n"
        e.description = inv
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        await message.channel.send(embed=e)
        e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
        
    
    async def equip(self, client, message, command, messageArray, lang_u):
        coll = db.prof_ec_users
        bgn = db.backgrounds
        inv = coll.find_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" })
        len_inv = len(inv["inv"])
        ri = None
        item = None
        if len(messageArray) == 0 or messageArray[0] == "":
            e = discord.Embed(title="", description=f"Укажите индекс предмета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        try:
            ri = int(messageArray[0])
        except:
            e = discord.Embed(title="", description=f"Укажите индекс предмета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        if ri > len_inv or ri == 0:
            e = discord.Embed(title="", description=f"Укажите индекс предмета в инвентаре.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        item = inv["inv"][ri - 1]
        if item["type"] == "role":
            role_g = message.guild.get_role(int(item["id"]))
            if role_g in message.author.roles:
                e = discord.Embed(title="", description=f"Эта роль уже надета.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            await message.author.add_roles(role_g)
            e = discord.Embed(title="Инвентарь", description=f"Роль <@&{role_g.id}> успешно была добавлена.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
        elif item["type"] == "waifu":
            items = list(inv["inv"])
            items = list(filter(lambda x: x["type"] == "waifu", items))
            items = list(map(lambda x: x["equip"] == 1, items))
            #print(items)
            if True in items:
                e = discord.Embed(title="", description=f"Одна из ролей вайфу уже надета.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            role_g = message.guild.get_role(int(item["id"]))
            if role_g in message.author.roles:
                e = discord.Embed(title="", description=f"Эта роль вайфу уже надета.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            await message.author.add_roles(role_g)
            e = discord.Embed(title="Инвентарь", description=f"Вайфу <@&{role_g.id}> успешно была добавлена.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
            i = inv["inv"]
            i[ri - 1] = { "type": "waifu", "id": item["id"], "equip": 1 }
            coll.update_one({ "disid": str(message.author.id), "guild": str(message.guild.id) }, { "$set": { "inv": i } })
        elif item["type"] == "background":
            card = item["id"]
            bgn_item = bgn.find_one({ "id": card }) 
            custom = client.get_emoji(int(bgn_item["emoji"]))
            custom_name = bgn_item["name"]
            if card == inv["background"]:
                e = discord.Embed(title="", description=f"Эта карточка уже надета.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            coll.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "background": card } })
            e = discord.Embed(title="Инвентарь", description=f"Карточка {custom} **{custom_name}** успешно была надета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
        
    async def unequip(self, client, message, command, messageArray, lang_u):
        coll = db.prof_ec_users
        bgn = db.backgrounds
        inv = coll.find_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" })
        len_inv = len(inv["inv"])
        ri = None
        item = None
        if len(messageArray) == 0 or messageArray[0] == "":
            e = discord.Embed(title="", description=f"Укажите индекс предмета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        try:
            ri = int(messageArray[0])
        except:
            e = discord.Embed(title="", description=f"Укажите индекс предмета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        if ri > len_inv or ri == 0:
            e = discord.Embed(title="", description=f"Укажите индекс предмета в инвентаре.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        item = inv["inv"][ri - 1]
        if item["type"] == "role":
            role_g = message.guild.get_role(int(item["id"]))
            if role_g not in message.author.roles:
                e = discord.Embed(title="", description=f"Эта роль уже снята.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            await message.author.remove_roles(role_g)
            e = discord.Embed(title="Инвентарь", description=f"Роль <@&{role_g.id}> успешно была удалена.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
        elif item["type"] == "waifu":
            role_g = message.guild.get_role(int(item["id"]))
            if role_g not in message.author.roles:
                e = discord.Embed(title="", description=f"Эта роль вайфу уже снята.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            await message.author.remove_roles(role_g)
            e = discord.Embed(title="Инвентарь", description=f"Вайфу <@&{role_g.id}> успешно была удалена.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
            i = inv["inv"]
            i[ri - 1] = { "type": "waifu", "id": item["id"], "equip": 0 }
            coll.update_one({ "disid": str(message.author.id), "guild": str(message.guild.id) }, { "$set": { "inv": i } })
        elif item["type"] == "background":
            card = item["id"]
            bgn_item = bgn.find_one({ "id": card }) 
            custom = client.get_emoji(int(bgn_item["emoji"]))
            custom_name = bgn_item["name"]
            if card != inv["background"]:
                e = discord.Embed(title="", description=f"Эта карточка уже снята.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            coll.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "background": 0 } })
            e = discord.Embed(title="Инвентарь", description=f"Карточка {custom} **{custom_name}** успешно была снята.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
