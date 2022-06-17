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
    return [["hide", hide, "all", "all", "rlist"]]

async def hide(client, message, command, messageArray, lang_u):
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
        photo = ["https://i.pinimg.com/originals/f8/eb/a7/f8eba73981eea6dd48e3630d867e6a59.gif",
                "https://thumbs.gfycat.com/EveryZealousHyracotherium-size_restricted.gif",
                "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/2998e19a-c1b5-411f-b97c-96d884bf2c15/d710f6v-1af3e17c-e1b2-438c-bd66-83a505205b1e.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvMjk5OGUxOWEtYzFiNS00MTFmLWI5N2MtOTZkODg0YmYyYzE1XC9kNzEwZjZ2LTFhZjNlMTdjLWUxYjItNDM4Yy1iZDY2LTgzYTUwNTIwNWIxZS5naWYifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.fiR331TbcTODTpctGyWQY4So21B6EjwacFb_t8M1kkU",
                "https://media1.tenor.com/images/b72bda96b449d2ad93a4cebdb42b116d/tenor.gif?itemid=13436988",
                "https://media1.tenor.com/images/39ed9fbf909547dbd808ea4b4f92061c/tenor.gif?itemid=12799738",
                "https://i.pinimg.com/originals/49/66/f0/4966f06531fa2ae23895ff5fe02f8547.gif",
                "https://cdn.discordapp.com/attachments/736150791819100240/768431694486437918/SkEODz_Ak09qGjd1TFVNDM_0tsoAGhGzt-TdJS4qgVG0mDBpFrQEjgTyJNyWirXxqZAQTPGgkgMj6I0cLnm9xw.gif",
                "https://media1.tenor.com/images/cfee6bb543427ab79202ff05ba7d0765/tenor.gif?itemid=3532023"
                ]

        userwith = ""

        mm = message.mentions
        if len(mm) > 0:
            while message.author in mm:
                mm.remove(message.author)

            user_m = susers.find_one({ "disid": str(mm[0].id), "guild": str(message.guild.id) })

            if str(message.author.id) not in user_m["ignore_list"]:
                userwith = f" от <@!{mm[0].id}>"

        if lang_u == "ru":
            e = discord.Embed(title="Реакция: прятаться", description=f"<@{str(message.author.id)}> прячется{userwith}", color=discord.Color(0x2F3136))
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