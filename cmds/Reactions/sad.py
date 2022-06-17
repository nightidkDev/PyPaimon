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
    return [["sad", sad, "all", "all", "rlist"]]

async def sad(client, message, command, messageArray, lang_u):
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
        photo = ["https://cdn.discordapp.com/attachments/727839937738702919/737714608881795152/559b9944029d2c2b17acabe36d9fee99.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/737714608432873573/e5198467133be2340aceee78093eef41.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/737714612262404220/4e77f6bb695384cc88042514b46ffe3365c8cb17r1-500-341_hq.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/737714615546544148/orig_7.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/737714614288121966/orig_8.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/737714613944057936/orig_9.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/737714618411253931/1521299328_tumblr_nv1v2u95Lg1uv28x7o1_500.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/737714617375260774/b9bcce6631239cd31b2e913e328f495075b44ae6r1-600-338_hq.gif",
                "https://cdn.discordapp.com/attachments/727839937738702919/737714619942043729/original_8.gif",
                "https://media.discordapp.net/attachments/784467101498343434/800445356033966110/image0.gif?width=414&height=224", # ;
                "https://cdn.discordapp.com/attachments/811515393860042773/825458508392300544/341d3ac321d2168961496f8f4efd7f29.gif",
                "https://cdn.discordapp.com/attachments/811515393860042773/825458451475202068/72a14c59eeb57e0ac6bed3615e7c7634.gif",
                "https://media.discordapp.net/attachments/811515393860042773/825457292450725888/848dc1621d2141df83c7f7fa7b85830c.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216343378788392/image0.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216344225906708/image1.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216344835129344/image2.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216345736118322/image3.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216347280408617/image4.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216347728412701/image5.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216348064350248/image6.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216348567535686/image7.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216349926752256/image8.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216350270554132/image9.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216460107055124/image0.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216460295667732/image1.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216460529893426/image2.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216461863419914/image3.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216462820769792/image4.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216463533539378/image5.gif",
                "https://cdn.discordapp.com/attachments/784467101498343434/828216464045637652/image6.gif"
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
            e = discord.Embed(title="Реакция: грустить", description=f"<@{str(message.author.id)}> грустит{userwith}", color=discord.Color(0x2F3136))
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