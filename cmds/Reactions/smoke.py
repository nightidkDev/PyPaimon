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
    return [["smoke", smoke, "all", "all", "rlist"]]

async def smoke(client, message, command, messageArray, lang_u):
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
        photo = ["https://cdn.discordapp.com/attachments/666234650758348820/712228249371148328/original_4.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712238202529906698/image0334.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712237160450883584/image02.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712228254341398568/4a7223ed3d66c7ca8aff06321b40049c537c8e1d_hq.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712228257059045396/bf2c441173e401cfcb185a14bf32c655.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712228258737029170/1497194262_1000x1000_cd.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712228263896023050/original_5.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825457647729115166/be3c3d8c776dc2e7b94841aec29d4b41.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825457509141053460/36911dfbfd85a157e3410816e1949279.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825457440241352754/7caa641bc9c5f0a1f1b2d8c1e7a88787.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229139865272320/image0.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229140108279808/image1.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229140456275968/image2.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229140737556510/image3.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229141240348742/image4.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229141630812160/image5.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229141978808340/image6.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229142490251285/image7.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229142797484052/image8.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229143165796373/image9.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229185121550336/image0.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229185544781854/image1.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229185808891916/image2.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229186128838656/image3.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828229186417328168/image4.gif",
                "https://cdn.discordapp.com/attachments/841720836867883019/843043580696330270/image0.gif",
                "https://cdn.discordapp.com/attachments/841720836867883019/843043581085483008/image1.gif"
                ]

        userwith = ""

        mm = message.mentions
        if len(mm) > 0:
            while message.author in mm:
                mm.remove(message.author)

            user_m = susers.find_one({ "disid": str(mm[0].id), "guild": str(message.guild.id) })

            if str(message.author.id) not in user_m["ignore_list"]:
                userwith = f" c <@!{mm[0].id}>"

        if lang_u == "ru":
            e = discord.Embed(title="Реакция: курить", description=f"<@{str(message.author.id)}> курит{userwith}", color=discord.Color(0x2F3136))
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