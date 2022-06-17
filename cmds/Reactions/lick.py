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
    return [["lick", lick, "all", "all", "rlist"]]

async def lick(client, message, command, messageArray, lang_u):
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
                    "https://cdn.discordapp.com/attachments/666234650758348820/712227416038441050/94f653381e7224a4a9010a8218204cb02792cf40_hq.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712227428621353001/tenor_6.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712227436087214160/BQM6jEZ-UJLgGUuvrNkYUJ_8MjNri87XDbXHwA4hgSL4CU8zqcPJsfyO7Y1G7XCVdM8FbLGIVo6B8OcbolGTRg.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712227451706802258/G1T0.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712227650235662336/224b3367affb1ed0dcbead814f3f4ebf89b35a54r1-542-307_hq.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712227654304006184/Kurumi_licks_shidos_wound.gif",
                    "https://cdn.discordapp.com/attachments/784467101498343434/828233408097288232/image1.gif"
                ]

        if len(message.mentions) == 0:
            
            if lang_u == "ru":
                e = discord.Embed(title="Реакция: лизнуть", description=f"<@{str(message.author.id)}> лизнул(-а) всех.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="Reaction: lick", description=f"<@{str(message.author.id)}> licked all.", color=discord.Color(0x2F3136))
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

        if sdb.count_documents({ "id": str(message.mentions[0].id), "guild": str(message.guild.id) }) == 0:
            sdb.insert_one({ "id": str(message.mentions[0].id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

        user_m_s = sdb.find_one({ "id": str(message.mentions[0].id), "guild": str(message.guild.id) })
        user_m = susers.find_one({ "disid": str(message.mentions[0].id), "guild": str(message.guild.id) })

        if str(message.author.id) in user_m["ignore_list"]:
            return None

        if user_m["partner"] != "":
            if user_m["partner"] != str(message.author.id):
                if user_m_s["deny_all_marry"] == 1:
                    e = discord.Embed(title="Авто-отказ", description="Данный пользователь запретил использовать на себе эту команду всем, кроме партнера в браке.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    return await message.channel.send(embed=e)
        if lang_u == "ru":
            e = discord.Embed(title="Реакция: лизнуть", description=f"<@{str(message.author.id)}> лизнул(-а) <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{message.author.display_name} • {config.reaction_two} примогемов", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        elif lang_u == "en":
            e = discord.Embed(title="Reaction: lick", description=f"<@{str(message.author.id)}> licked <@{str(message.mentions[0].id)}>", color=discord.Color(0x2F3136))
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