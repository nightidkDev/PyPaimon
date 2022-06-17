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
    return [["slap", slap, "all", "all", "rlist"]]

async def slap(client, message, command, messageArray, lang_u):
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
                    "https://media.discordapp.net/attachments/666234650758348820/712225610541563984/K02.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712225609069363250/5LYzTBVoS196gvYvw3zjwD-om80ggkseptSOdWG-fEI.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712225609668886598/UwmX.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712225614345797642/79zo.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712225618787565578/CXfX.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712225618518868038/9fa.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712225622499524678/02FZDnA.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825457746799099914/7189b36e4a0ef770cda47d2f65747ef1.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825457002792747009/e84534efbb0367f78f616f0c904dc35c.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825456364158713856/b6e39e693be3968d212b0fe5754f85db.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825456309004271636/568799ded41fed64cc227b8f467332c0.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826447386364346449/ecb46c7f3c00d90eb899aef0fbd0146a.gif"
                ]
        if len(message.mentions) == 0:
            

            if lang_u == "ru":
                e = discord.Embed(title="Реакция: дать пощёчину", description=f"<@{str(message.author.id)}> дал(-а) всем пощёчину.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="Reaction: slap", description=f"<@{str(message.author.id)}> slap all.", color=discord.Color(0x2F3136))
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
            e = discord.Embed(title="Реакция: дать пощёчину", description=f"<@{str(message.author.id)}> дал(-а) пощёчину <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        elif lang_u == "en":
            e = discord.Embed(title="Reaction: slap", description=f"<@{str(message.author.id)}> slap <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
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