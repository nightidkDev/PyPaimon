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
    return [["shoot", shoot, "all", "all", "rlist"]]

async def shoot(client, message, command, messageArray, lang_u):
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
                    "https://media.discordapp.net/attachments/666234650758348820/773145448596766720/22b9e5f6f2121cc52a45e35a99f54961.gif?width=720&height=405",
                    "https://media.discordapp.net/attachments/666234650758348820/773145449166798878/original_13.gif?width=450&height=229",
                    "https://media.discordapp.net/attachments/666234650758348820/773145451720474624/4z90.gif?width=450&height=253",
                    "https://media.discordapp.net/attachments/666234650758348820/773145453851050004/ce2d099cf5a1bd8370d7ed89030aa086.gif?width=450&height=337",
                    "https://media.discordapp.net/attachments/666234650758348820/773145456527671336/171023_6670.gif?width=884&height=567",
                    "https://cdn.discordapp.com/attachments/666234650758348820/773145450899177482/2z23.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825457595565211698/ce2d099cf5a1bd8370d7ed89030aa086.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825457570134360094/1893860c9a8c22009ab8740b7b0ec1f8.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825457535850381322/104d6a4d57fcc458f72466355635ad13.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828202387968622592/image0.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828202388217004062/image1.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828202388463812608/image2.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828202388753088512/image3.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828203265668939776/image0.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828203265912864768/image1.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845301160637366272/tumblr_01b9e74e9ee929c3a2504f960725d91d_e5783a66_540.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845002260630339614/14043.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845002263139582012/127816.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845002267215527966/127935.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845004214812016660/tenor_59.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845301160637366272/tumblr_01b9e74e9ee929c3a2504f960725d91d_e5783a66_540.gif"
                ]
        if len(message.mentions) == 0:
            

            if lang_u == "ru":
                e = discord.Embed(title="Реакция: стрельба", description=f"<@{str(message.author.id)}> стреляет.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="Reaction: shoot", description=f"<@{str(message.author.id)}> shooting.", color=discord.Color(0x2F3136))
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
            e = discord.Embed(title="Реакция: стрельба", description=f"<@{str(message.author.id)}> стреляет в <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        elif lang_u == "en":
            e = discord.Embed(title="Reaction: shoot", description=f"<@{str(message.author.id)}> shoots <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
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

