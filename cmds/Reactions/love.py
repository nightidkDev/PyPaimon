import datetime
import pymongo
import os
import nextcord
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
    return [["love", love, "all", "all", "rlist"]]

async def love(client, message, command, messageArray, lang_u):
    coll = db.prof_ec_users
    data = coll.find_one({"disid": str(message.author.id), "guild": str(message.guild.id)})
    if data["money"] < config.reaction_two:
        if lang_u == "ru":
            e = nextcord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
        else:
            e = nextcord.Embed(title="", description=f"Not enough stars.", color=discord.Color(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        return await message.channel.send(embed = e)
    else:
        money_emoji = client.get_emoji(746756714484727828)
        if len(message.mentions) == 0:
            photo = os.listdir('assets/Reactions/love')
            c_p = random.choice(photo)
            file = discord.File(f"assets/Reactions/love/{c_p}", filename=f"{c_p}")

            if lang_u == "ru":
                e = nextcord.Embed(title="Реакция: признание в любви", description=f"<@{str(message.author.id)}> признается в любви всем.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=f"attachment://{c_p}")
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                return await message.channel.send(file=file, embed=e)
            elif lang_u == "en":
                e = nextcord.Embed(title="Reaction: declaration of love", description=f"<@{str(message.author.id)}> declares his love to everyone.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=f"attachment://{c_p}")
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} stars", icon_url=message.author.avatar_url)
                return await message.channel.send(file=file, embed=e)
        if message.mentions[0].id == message.author.id:
            if lang_u == "ru":
                e = nextcord.Embed(title="", description=f"<@{str(message.author.id)}>, не лучшая идея.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = nextcord.Embed(title="", description=f"<@{str(message.author.id)}>, not a good idea.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
        photo = os.listdir('assets/Reactions/love')
        c_p = random.choice(photo)
        file = discord.File(f"assets/Reactions/love/{c_p}", filename=f"{c_p}")

        user_m = users.find_one({ "disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" })

        if str(message.author.id) in user_m["ignore_list"]:
            return None

        if lang_u == "ru":
            e = nextcord.Embed(title="Реакция: признание в любви", description=f"<@{str(message.author.id)}> признается в любви <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=f"attachment://{c_p}")
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(file=file, embed=e)
        elif lang_u == "en":
            e = nextcord.Embed(title="Reaction: declaration of love", description=f"<@{str(message.author.id)}> confesses his love to <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=f"attachment://{c_p}")
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} stars", icon_url=message.author.avatar_url)
            await message.channel.send(file=file, embed=e)

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