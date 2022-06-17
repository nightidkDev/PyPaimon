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
    return [["cry", cry, "all", "all", "rlist"]]

async def cry(client, message, command, messageArray, lang_u):
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
        photo = ["https://cdn.discordapp.com/attachments/666234650758348820/712230119552319529/Iiuj.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712230122685464596/b6d941a6f92b1e846cc5d0d78403daea25fa489cr1-540-300_hq.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712230123633377291/original_7.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712230128033464400/original_6.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712230127605383289/tenor_10.gif",
                "https://cdn.discordapp.com/attachments/666234650758348820/712230131195969556/anime-cry-cute-gif-Favim.com-2453915.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/800444804701618256/image0.gif",
                "https://media.discordapp.net/attachments/784467101498343434/800849528202461224/image2.gif?width=486&height=270",
                "https://media.discordapp.net/attachments/784467101498343434/800849529074745385/image4.gif?width=486&height=274",
                "https://media.discordapp.net/attachments/811515393860042773/825458346122412032/27c15046636bb316aca02ffa2a70d266.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825458058913513522/ec193175c8fa6dd1fcba890c62b95818.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825457390308032512/837cc3072c337bf0edc3c3b6b6cb6fe8.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825456956486451243/de72ce0a56aa4f3f19ca6ad9132f61a3.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218870631759902/image0.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218870959570974/image1.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218871252123698/image2.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218871545987073/image3.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218872272125962/image4.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218872803885086/image5.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218873622560788/image6.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218873852592139/image7.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218874251182081/image8.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218874574929940/image9.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218968082481212/image0.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218968598249472/image1.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828218969257148446/image2.gif",
                "https://cdn.discordapp.com/attachments/811515393860042773/826447305757687808/730c2ea85a354d0f67f3bd37433a5266.gif",
                "https://cdn.discordapp.com/attachments/768157522825183263/845004708556308501/tenor_72.gif"
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
            e = discord.Embed(title="Реакция: плакать", description=f"<@{str(message.author.id)}> плачет{userwith}", color=discord.Color(0x2F3136))
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