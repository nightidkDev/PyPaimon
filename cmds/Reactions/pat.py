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
    return [["pat", pat, "all", "all", "rlist"]]

async def pat(client, message, command, messageArray, lang_u):
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
                    "https://media.discordapp.net/attachments/666234650758348820/712224876496420895/184357.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712224878207565824/H69F.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712224880459776120/-----GIF---17.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712224879713452037/127889.gif?width=796&height=684",
                    "https://media.discordapp.net/attachments/666234650758348820/712224886239526982/2e27d5d124bc2a62ddeb5dc9e7a73dd8.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712224885438677003/GrouchyIllinformedBelugawhale-size_restricted.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712224887271325747/1449626448-03ba1a47240ed474400d16e8152b4f1b.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712224896326959114/8SV8.gif?width=1216&height=684",
                    "https://cdn.discordapp.com/attachments/784467101498343434/800443272161787955/image0.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828233407669993472/image0.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826448086523052102/8bc7b7d341dcf81598cd0069d2219a5b.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826448015341387836/34a1d8c67e7b373de17bbfa5b8d35fc0.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826447686189973584/c473e78b40260870a027be7523e689e7.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826448015341387836/34a1d8c67e7b373de17bbfa5b8d35fc0.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845002354923274280/2482.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845002427978481756/127714.gif"
                ]

        if len(message.mentions) == 0:
            
            if lang_u == "ru":
                e = discord.Embed(title="Реакция: погладить", description=f"<@{str(message.author.id)}> погладил(-а) всех.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="Reaction: pat", description=f"<@{str(message.author.id)}> pats all.", color=discord.Color(0x2F3136))
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
            e = discord.Embed(title="Реакция: погладить", description=f"<@{str(message.author.id)}> погладил(-а) <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        elif lang_u == "en":
            e = discord.Embed(title="Reaction: pat", description=f"<@{str(message.author.id)}> pats <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
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