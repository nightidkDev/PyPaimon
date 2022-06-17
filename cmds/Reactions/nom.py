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

users = db.prof_ec_users

def init():
    return [["nom", nom, "all", "all", "rlist"]]

async def nom(client, message, command, messageArray, lang_u):
    coll = db.prof_ec_users
    data = coll.find_one({"disid": str(message.author.id), "guild": str(message.guild.id)})
    if data["money"] < config.reaction_two:
        if lang_u == "ru":
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
        else:
            e = discord.Embed(title="", description=f"Not enough stars.", color=discord.Color(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        return await message.channel.send(embed = e)
    else:
        money_emoji = client.get_emoji(746756714484727828)
        photo = [
                    "https://media.discordapp.net/attachments/666234650758348820/712203665510760468/1yS5.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712203669864448000/1512581610_c8e.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712203668744568882/32Ph.gif?width=1213&height=684",
                    "https://media.discordapp.net/attachments/666234650758348820/712203672947523604/tumblr_inline_omdfcb660c1ruqj29_540.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712203672720769114/2yNA.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712203673245319198/tstDeBP.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712203682598617158/2uIY.gif?width=1215&height=684",
                    "https://media.discordapp.net/attachments/784467101498343434/800849525295153172/image0.gif?width=486&height=274",
                    "https://media.discordapp.net/attachments/811515393860042773/825457846320758794/89aac22b1bbbf94983c33dd03b87ae7f.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825457797399314450/92efa4924960e9f1d4991d81a3049dd4.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826447430261800970/a779cee208d9443b087e4e214edd3cb3.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845002562028830754/141047.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845004579463626772/tenor_82.gif"
                ]
        if len(message.mentions) == 0:
           

            if lang_u == "ru":
                e = discord.Embed(title="Реакция: покормить", description=f"<@{str(message.author.id)}> покормил(-а) всех.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="Reaction: feed", description=f"<@{str(message.author.id)}> fed all.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} stars", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
        if message.mentions[0].id == message.author.id:
            if lang_u == "ru":
                e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, не лучшая идея.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, not a good idea.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)

        user_m = users.find_one({ "disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" })

        if str(message.author.id) in user_m["ignore_list"]:
            return None

        if lang_u == "ru":
            e = discord.Embed(title="Реакция: покормить", description=f"<@{str(message.author.id)}> покормил(-а) <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        elif lang_u == "en":
            e = discord.Embed(title="Reaction: feed", description=f"<@{str(message.author.id)}> fed <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} stars", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)

        ms = data["moneystats"]
        ms["1d"] -= config.reaction_two
        ms["7d"] -= config.reaction_two
        ms["14d"] -= config.reaction_two
        ms["all"] -= config.reaction_two
        if ms["history_1d"]["reactions"]["view"] == 0:
            ms["history_1d"]["reactions"]["view"] = 1
        ms["history_1d"]["reactions"]["count"] -= config.reaction_two
        if ms["history"]["reactions"]["view"] == 0:
            ms["history"]["reactions"]["view"] = 1
        ms["history"]["reactions"]["count"] -= config.reaction_two

        db.prof_ec_users.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "money": data['money'] - config.reaction_two, "moneystats": ms } })