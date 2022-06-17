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
    return [["poke", poke, "all", "all", "rlist"]]

async def poke(client, message, command, messageArray, lang_u):
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
                    "https://media.discordapp.net/attachments/666234650758348820/712205578134356019/bun.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712205583524298789/ClosedSomeLhasaapso-size_restricted.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712205584845242399/JTSO.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712205584224747610/Omake_Gif_Anime_-_Release_the_Spyce_-_Episode_2_-_Fu_Pokes_Momo.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712205584820076634/EnlightenedInferiorAfricanaugurbuzzard-size_restricted.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828205695899795476/image0.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828205696243335168/image1.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828205696590807090/image2.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828205696998572102/image3.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828205697413021766/image4.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828205698240348170/image5.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826447527422853150/ae62324b1de9d2422a45557ac0551e48.gif"
                ]
        if len(message.mentions) == 0:
            

            if lang_u == "ru":
                e = discord.Embed(title="Реакция: ткнуть", description=f"<@{str(message.author.id)}> ткнул(-а) всех.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="Reaction: poke", description=f"<@{str(message.author.id)}> poked all.", color=discord.Color(0x2F3136))
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
            e = discord.Embed(title="Реакция: ткнуть", description=f"<@{str(message.author.id)}> ткнул(-а) <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        elif lang_u == "en":
            e = discord.Embed(title="Reaction: poke", description=f"<@{str(message.author.id)}> poked <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
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