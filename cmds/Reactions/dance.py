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

sdb = db.u_settings
susers = db.prof_ec_users

def init():
    return [["dance", dance, "all", "all", "rlist"]]

async def dance(client, message, command, messageArray, lang_u):
    coll = db.prof_ec_users
    data = coll.find_one({"disid": str(message.author.id), "guild": str(message.guild.id)})

    mm = message.mentions
    #mm = list(filter(lambda x: x.bot is False, message.mentions))
    if len(mm) > 0:
        while message.author in mm:
            mm.remove(message.author)
    if len(mm) == 0:
        if data["money"] < config.reaction_one:
            if lang_u == "ru":
                e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            else:
                e = discord.Embed(title="", description=f"Not enough stars.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        photo = [
                    "https://cdn.discordapp.com/attachments/666234650758348820/712228890986151956/BHIZ.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712228893989404672/11704.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712228895415599124/gamereviews-anime-reviews.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712228897235664906/1502306599_Anime-anime-gif-Eromanga-Sensei-Izumi-Sagiri-3995135.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712228898884026368/9M1F.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828208496046374912/image1.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828208496322281512/image2.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828208496553623602/image3.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828208496825860096/image4.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828208497345822730/image5.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828208497815453726/image6.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828208498172755988/image7.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826448550413074472/b49612e1d15b91012f13515736357903.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826447284396228648/2b8737f37a4dcdcceb3f71148f214832.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845005220697997342/image054-4.gif"
                ]

        if lang_u == "ru":
            e = discord.Embed(title="Реакция: танец", description=f"<@{str(message.author.id)}> танцует.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_one} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        elif lang_u == "en":
            e = discord.Embed(title="Reaction: dance", description=f"<@{str(message.author.id)}> is dancing.", color=discord.Color(0x2F3136))
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
    else:

        if sdb.count_documents({ "id": str(message.author.id), "guild": str(message.guild.id) }) == 0:
            sdb.insert_one({ "id": str(message.author.id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })
        if sdb.count_documents({ "id": str(mm[0].id), "guild": str(message.guild.id) }) == 0:
            sdb.insert_one({ "id": str(mm[0].id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

        user_m_s = sdb.find_one({ "id": str(mm[0].id), "guild": str(message.guild.id) })
        user_m = susers.find_one({ "disid": str(mm[0].id), "guild": str(message.guild.id) })

        if str(message.author.id) in user_m["ignore_list"]:
            return None

        if user_m["partner"] != "":
            if user_m["partner"] == str(message.author.id):
                if user_m_s["command_dance_marry"] == 0:
                    photo = config.dance
                    e = discord.Embed(title="Реакция: танец", description=f"<@{str(message.author.id)}> танцует с <@{str(mm[0].id)}>", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_image(url=random.choice(photo))
                    author_m = susers.find_one({"disid": str(message.author.id), "guild": f"{message.guild.id}"})["money"]
                    susers.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "money": author_m - config.reaction_two } })
                    return await message.channel.send(embed=e)

        if data["money"] < config.reaction_two:
            if lang_u == "ru":
                e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            else:
                e = discord.Embed(title="", description=f"Not enough stars.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        e = discord.Embed(title="Реакция: танец", description=f"<@{str(mm[0].id)}>, с тобой хочет **потанцевать** <@{message.author.id}>. Что ответишь?", color=discord.Color(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        message_s = await message.channel.send(embed=e)
        await message_s.add_reaction("✅")
        await message_s.add_reaction("❌")
        
        author_m = db.prof_ec_users.find_one({"disid": str(message.author.id), "guild": f"{message.guild.id}"})

        ms = author_m["moneystats"]
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

        db.prof_ec_users.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "money": author_m["money"] - config.reaction_two, "moneystats": ms } })
        coll = db.reactions
        coll.insert_one({"message_id": str(message_s.id), "id": str(message.author.id), "mention_id": str(mm[0].id), "time": int(time.time()) + 30, "react": 5, "guild_id": str(message.guild.id), "channel_id": str(message.channel.id), "lang": str(lang_u), "type": "reaction"})