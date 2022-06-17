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
    return [["tea", tea, "all", "all", "rlist"]]

async def tea(client, message, command, messageArray, lang_u):
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
        photo = [
            "https://cdn.discordapp.com/attachments/805200807208419338/840315054742175754/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f776174747061642d6d656469612d736572766963652f53746f.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840314983774683226/original_27.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840314561302626304/original_26.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840314559746146324/result_5869.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840314558370545664/Why_You_Should_Be_Drinking_Tea_Instead_Of_Coffee.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840314558265819146/tea_time___Tumblr.gif",
            "https://cdn.discordapp.com/attachments/768157522825183263/845002692481122353/1989f7c0ba9805108a5b90c563f45733.gif"
        ]

        userwith = ""

        mm = message.mentions
        if len(mm) > 0:
            while message.author in mm:
                mm.remove(message.author)

            user_m = susers.find_one({ "disid": str(mm[0].id), "guild": str(message.guild.id) })

            if str(message.author.id) not in user_m["ignore_list"]:
                userwith = f" с <@!{mm[0].id}>"

        if lang_u == "ru":
            e = discord.Embed(title="Реакция: пить чай", description=f"<@{str(message.author.id)}> пьёт чай{userwith}", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_one} примогемов", icon_url=message.author.avatar_url)
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