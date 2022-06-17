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
susers = db.prof_ec_users

def init():
    return [["depression", depression, "all", "all", "rlist"]]

async def depression(client, message, command, messageArray, lang_u):
    coll = db.prof_ec_users
    data = coll.find_one({"disid": str(message.author.id), "guild": str(message.guild.id)})
    if data["money"] < config.reaction_one:
        if lang_u == "ru":
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
        else:
            e = discord.Embed(title="", description=f"Not enough stars.", color=discord.Color(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        return await message.channel.send(embed = e)
    else:
        money_emoji = client.get_emoji(746756714484727828)
        photo = ["https://cdn.discordapp.com/attachments/727839937738702919/738353197126516803/1wnj.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/738353197172785152/a795b47a0206ede9ea43cebf29387af0b1a0dd96r1-600-300_hq.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/738353200079306872/69ea97ceff9e42ed3eb55fbd6f26f67c6476838fr1-500-281_hq.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/738353195176296557/original_9.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/738353200498999366/orig_10.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/738353204802093066/DVY.gif",
                "https://media.discordapp.net/attachments/784467101498343434/800445356033966110/image0.gif?width=414&height=224", # ;
                "https://media.discordapp.net/attachments/811515393860042773/825458394885259274/8e738050d427a765328b042525db154e.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825457476013916180/ca5f4e343c333f08c8a8286681f04885.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825457292450725888/848dc1621d2141df83c7f7fa7b85830c.gif"
                ]

        userwith = ""

        mm = message.mentions
        if len(mm) > 0:
            while message.author in mm:
                mm.remove(message.author)

            user_m = susers.find_one({ "disid": str(mm[0].id), "guild": str(message.guild.id) })

            if str(message.author.id) not in user_m["ignore_list"]:
                userwith = f" из-за <@!{mm[0].id}>"

        if lang_u == "ru":
            e = discord.Embed(title="Реакция: депрессия", description=f"<@{str(message.author.id)}> впал в депрессию{userwith}", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_one} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        elif lang_u == "en":
            e = discord.Embed(title="Reaction: depression", description=f"<@{str(message.author.id)}> is in depression.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_one} stars", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)

        ms = data["moneystats"]
        ms["1d"] -= config.reaction_one
        ms["7d"] -= config.reaction_one
        ms["14d"] -= config.reaction_one
        ms["all"] -= config.reaction_one
        if ms["history_1d"]["reactions"]["view"] == 0:
            ms["history_1d"]["reactions"]["view"] = 1
        ms["history_1d"]["reactions"]["count"] -= config.reaction_one
        if ms["history"]["reactions"]["view"] == 0:
            ms["history"]["reactions"]["view"] = 1
        ms["history"]["reactions"]["count"] -= config.reaction_one

        db.prof_ec_users.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "money": data['money'] - config.reaction_one, "moneystats": ms } })