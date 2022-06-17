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
    return [["coffee", coffee, "all", "all", "rlist"]]

async def coffee(client, message, command, messageArray, lang_u):
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
            "https://cdn.discordapp.com/attachments/805200807208419338/840313664246775857/----------_Dulceria_Crew_By----------.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840313666367914024/p_r_i_n_c_e_mark_lee.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840313671133823016/anime_food___Tumblr_discovered_by_Naho_on_We_Heart_It.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840313672114896926/DO_YOU_Namjin_-_kpopawards2017.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840313673242247228/Animated_gif_in_gifs_collection_by_j_s_on_We_Heart_It.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840313676212207666/SEXTAPE___-_setters__-_-_five_.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840313676685639680/f1d022bd1260736c.gif",
            "https://cdn.discordapp.com/attachments/805200807208419338/840313677881409566/15_DELICIOUS_AND_INSTAGRAMABLE_CAFES_IN_SINGAPORE.gif"
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
            e = discord.Embed(title="Реакция: пить кофе", description=f"<@{str(message.author.id)}> пьёт кофе{userwith}", color=discord.Color(0x2F3136))
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