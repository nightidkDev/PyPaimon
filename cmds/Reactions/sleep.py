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
    return [["sleep", sleep, "all", "all", "rlist"]]

async def sleep(client, message, command, messageArray, lang_u):
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
        else:
            money_emoji = client.get_emoji(746756714484727828)
            photo = ["https://cdn.discordapp.com/attachments/666234650758348820/712761884889317496/e13a45584bb5427a225d1e229e9c714ce1ffd8dar1-640-360_hq.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712761883089829928/image_860808180310365716111.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712761888030851092/PliT.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712761892355178516/9qBu.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712761892959158353/dc5cd3670390cb757c9f7c52591d3c09.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712761894384959580/orig_6.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/797249398895411210/image0.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/797249427165282304/image0.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/800443270177882142/image2.gif",
                    "https://media.discordapp.net/attachments/811515393860042773/825457982971969566/a47e33d3aeca8945d4cd4c39025e9088.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232872351105044/image0.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232872649424906/image1.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232872963342366/image2.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232873340567552/image3.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232873650814983/image4.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232873983082546/image5.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232874284285992/image6.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232874880794635/image7.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232875321065482/image8.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232875509284864/image9.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232991686787082/image0.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232991968854066/image1.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232992304267284/image2.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232992743882793/image3.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232993000259604/image4.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232993452982292/image5.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232993935982592/image6.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828232994233647144/image7.gif",
                    "https://cdn.discordapp.com/attachments/840305937184587836/840306757292130354/anime-sleep-80.gif",
                    "https://cdn.discordapp.com/attachments/840305937184587836/840306756835737640/20210507_221851.gif",
                    "https://cdn.discordapp.com/attachments/768157522825183263/845002868042104832/127988.gif"
                    ]

            if lang_u == "ru":
                e = discord.Embed(title="Реакция: спать", description=f"<@{str(message.author.id)}> наелся и спит.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_one} примогемов", icon_url=message.author.avatar_url)
                await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="Reaction: sleep", description=f"<@{str(message.author.id)}> is **sleeping**.", color=discord.Color(0x2F3136))
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
        if data["money"] < config.reaction_two:
            if lang_u == "ru":
                e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            else:
                e = discord.Embed(title="", description=f"Not enough stars.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
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
                if user_m_s["command_sleep_marry"] == 0:
                    photo = config.sleep
                    e = discord.Embed(title="Реакция: спать", description=f"<@{str(message.author.id)}> спит с <@{str(mm[0].id)}>", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_image(url=random.choice(photo))
                    author_m = susers.find_one({"disid": str(message.author.id), "guild": f"{message.guild.id}"})
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
                    susers.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "money": author_m["money"] - config.reaction_two } })
                    return await message.channel.send(embed=e)
            else:
                if user_m_s["deny_all_marry"] == 1:
                    e = discord.Embed(title="Авто-отказ", description="Данный пользователь запретил использовать на себе эту команду всем, кроме партнера в браке.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    return await message.channel.send(embed=e)

        if data["money"] < config.reaction_two:
            if lang_u == "ru":
                e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            else:
                e = discord.Embed(title="", description=f"Not enough stars.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        
        e = discord.Embed(title="Реакция: спать", description=f"<@{str(mm[0].id)}>, с тобой хочет **уснуть** <@{message.author.id}>. Что ответишь?", color=discord.Color(0x2F3136))
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
        coll.insert_one({"message_id": str(message_s.id), "id": str(message.author.id), "mention_id": str(mm[0].id), "time": int(time.time()) + 30, "react": 8, "guild_id": str(message.guild.id), "channel_id": str(message.channel.id), "lang": str(lang_u), "type": "reaction"})