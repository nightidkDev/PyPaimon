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
    return [["hit", hit, "all", "all", "rlist"]]

async def hit(client, message, command, messageArray, lang_u):
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
        if len(message.mentions) == 0:
            photo = ["https://media.discordapp.net/attachments/666234650758348820/712226611428065280/98b3-icmpfxa2290835.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712226616037867600/orig_2.gif?width=1216&height=684",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712226615454859284/7zBH.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712226617266798642/WhichFlatAnteater-max-1mb.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712226619892432977/tenor_5.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/800443270529941595/image3.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825456432773333033/ec5a139df9a9edcbf8f3ae1ff15bc192.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845003851504943194/tenor_38.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845003189291974706/148627.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845003469370032139/148520.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845003476110540850/148590.gif"
                    ]

            if lang_u == "ru":
                e = discord.Embed(title="Реакция: ударить", description=f"<@{str(message.author.id)}> ударил(-а) всех.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="Reaction: hit", description=f"<@{str(message.author.id)}> hit all.", color=discord.Color(0x2F3136))
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
        photo = ["https://media.discordapp.net/attachments/666234650758348820/712226611428065280/98b3-icmpfxa2290835.gif",
                "https://media.discordapp.net/attachments/666234650758348820/712226616037867600/orig_2.gif?width=1216&height=684",
                "https://cdn.discordapp.com/attachments/666234650758348820/712226615454859284/7zBH.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712226617266798642/WhichFlatAnteater-max-1mb.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712226619892432977/tenor_5.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/800443270529941595/image3.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825456432773333033/ec5a139df9a9edcbf8f3ae1ff15bc192.gif"
                ]

        user_m = users.find_one({ "disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" })

        if str(message.author.id) in user_m["ignore_list"]:
            return None

        if lang_u == "ru":
            e = discord.Embed(title="Реакция: ударить", description=f"<@{str(message.author.id)}> ударил(-а) <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        elif lang_u == "en":
            e = discord.Embed(title="Reaction: hit", description=f"<@{str(message.author.id)}> hit <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
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