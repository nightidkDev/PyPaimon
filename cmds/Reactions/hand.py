import datetime
import pymongo
import os
import discord
import time
import sys
import random
sys.path.append("../../")
import config 
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

sdb = db.u_settings
susers = db.prof_ec_users

def init():
    return [["hand", hand, "all", "all", "rlist"]]

async def hand(client, message, command, messageArray, lang_u):

    if sdb.count_documents({ "id": str(message.author.id), "guild": str(message.guild.id) }) == 0:
        sdb.insert_one({ "id": str(message.author.id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

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
        if len(message.mentions) == 0:
            if lang_u == "ru":
                e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, укажи ник кого ты хочешь **взять за руку**.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
            elif lang_u == "en":
                e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, enter nick who do you want to **take a hand**.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed=e)
        if message.mentions[0].id == message.author.id:
            if lang_u == "ru":
                e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, одиночество - сволочь.", color=discord.Color(0x2F3136))
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
            if user_m["partner"] == str(message.author.id):
                if user_m_s["command_hand_marry"] == 0:
                    photo = config.hand
                    e = discord.Embed(title="Реакция: взять за руку", description=f"<@{message.author.id}> взял за руку <@{message.mentions[0].id}>", color=discord.Color(0x2F3136))
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

                    susers.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "money": author_m["money"] - config.reaction_two, "moneystats": ms } })
                    return await message.channel.send(embed=e)
            else:
                if user_m_s["deny_all_marry"] == 1:
                    e = discord.Embed(title="Авто-отказ", description="Данный пользователь запретил использовать на себе эту команду всем, кроме партнера в браке.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    return await message.channel.send(embed=e)

        if lang_u == "ru":
            e = discord.Embed(title="Реакция: взять за руку", description=f"<@{str(message.mentions[0].id)}>, <@{message.author.id}> тебя хочет **взять за руку**. Что ответишь?", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            message_s = await message.channel.send(embed=e)
            await message_s.add_reaction("✅")
            await message_s.add_reaction("❌")
        #elif lang_u == "en":
        #    e = discord.Embed(title="Reaction: take a hand", description=f"<@{str(message.mentions[0].id)}>, <@{message.author.id}> wants to **take your hand**. What do you say?", color=discord.Color(0x2F3136))
        #    e.timestamp = datetime.datetime.utcnow()
        #    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        #    message_s = await message.channel.send(embed=e)
        #    await message_s.add_reaction("✅")
        #    await message_s.add_reaction("❌")
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
        db.prof_ec_users.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "money": author_m["money"] - config.reaction_two } })
        coll = db.reactions
        coll.insert_one({"message_id": str(message_s.id), "id": str(message.author.id), "mention_id": str(message.mentions[0].id), "time": int(time.time()) + 30, "react": 6, "guild_id": str(message.guild.id), "channel_id": str(message.channel.id), "lang": str(lang_u), "type": "reaction"})