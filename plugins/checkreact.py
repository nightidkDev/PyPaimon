from threading import Condition
import discord
import time
import datetime
import sys
import time
import pymongo
import sqlite3
sys.path.append("../../")
import config
from libs import Builders
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

async def checkreactduels(client):
    try:
        con = sqlite3.connect("duels.db", check_same_thread=False)
        cur = con.cursor()
        info = cur.execute(f"SELECT * FROM duels").fetchall()
        for x in info:
            if x[3] <= int(time.time()):
                if x[7] == "duel":
                    continue
                guild = client.get_guild(x[4])
                channel = guild.get_channel(x[5])
                message = await channel.fetch_message(x[0])
                member = guild.get_member(x[1])
                member2 = guild.get_member(x[2])
                e = discord.Embed(title="Реакция: игнор", description=f"<@{str(member2.id)}> тебя проигнорировал(-а) :c", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                await message.clear_reactions()
                await message.edit(embed=e)
                cur.execute(f"DELETE FROM duels WHERE message_id={message.id}")
                con.commit()
        con.close()
    except BaseException as e:
        print(f"Error duels: {e}")


async def checkreact(client):
    coll = db.reactions
    datas = coll.find({})
    for data in datas:
        if data["time"] <= int(time.time()):
            try:
                server_coll = db.server
                if data["type"] == "war_clan":
                    clans = db.clans
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channels_id"][0]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["member"]))
                    clan1 = int(data["clan_id"])
                    clan2 = int(data["clan_id_opponent"])
                    await message.clear_reactions()
                    e = discord.Embed(title="Война группировок", description=f"Действие отменено из-за неактивности.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e)
                    clans.update_one({ "id": clan1 }, { "$set": { "war_status": 0 } })
                    clans.update_one({ "id": clan2 }, { "$set": { "war_status": 0 } })
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "war_clan_opponent":
                    clans = db.clans
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channels_id"][1]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    channel2 = guild.get_channel(int(data["channels_id"][0]))
                    message2 = await channel2.fetch_message(int(data["message_id2"]))
                    member = guild.get_member(int(data["member"]))
                    member2 = guild.get_member(int(data["member2"]))
                    clan1 = int(data["clan_id"])
                    clan2 = int(data["clan_id_opponent"])
                    await message.clear_reactions()
                    e = discord.Embed(title="Война группировок", description=f"Действие отменено из-за неактивности.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member2.display_name}", icon_url=member2.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(content="", embed=e)
                    e = discord.Embed(title="Война группировок", description=f"Действие отменено из-за неактивности.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member2.display_name}", icon_url=member2.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message2.edit(embed=e)
                    clans.update_one({ "id": clan1 }, { "$set": { "war_status": 0 } })
                    clans.update_one({ "id": clan2 }, { "$set": { "war_status": 0 } })
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "pages_shop_r": 
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    await message.clear_reactions()
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "pages_shop_w":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    await message.clear_reactions()
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "pages_shop_c":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    await message.clear_reactions()
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "pages_shop_category":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    await message.clear_reactions()
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "invite_clan":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["invited"]))
                    member2 = guild.get_member(int(data["inviter"]))
                    await message.clear_reactions()
                    e = discord.Embed(title="Приглашение в группировку", description=f"<@{str(member.id)}> проигнорировал приглашение.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member2.display_name}", icon_url=member2.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "transfer_clan":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["author"]))
                    await message.clear_reactions()
                    e = discord.Embed(title="Передача прав группировки", description=f"Время ответа вышло, передача отменена.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "delete_clan":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["author"]))
                    await message.clear_reactions()
                    e = discord.Embed(title="Удаление группировки", description=f"Время ответа вышло, удаление отменено.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "spots_clan":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["author"]))
                    await message.clear_reactions()
                    e = discord.Embed(title="", description=f"Время ответа вышло.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    e.set_author(name="Покупка дополнительных мест")
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "leave_clan":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["author"]))
                    await message.clear_reactions()
                    e = discord.Embed(title="Уход из группировки", description=f"Время ответа вышло.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "rename_clan":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["author"]))
                    await message.clear_reactions()
                    e = discord.Embed(title="Изменение названия группировки", description=f"Время ответа вышло, название оставлено.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "create_clan":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["owner_clan"]))
                    await message.clear_reactions()
                    e = discord.Embed(title="Создание группировки", description=f"Время для ответа вышло.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "shop_clan":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["author"]))
                    title = db.clans.find_one({"id": int(data["clan"]) })["title"]
                    await message.clear_reactions()
                    e = discord.Embed(title="", description=f"Время для покупки вышло.", color=discord.Color(0x2F3136))
                    e.set_author(name=f"Магазин группировки {title}")
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                elif data["type"] == "role":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["for_id"]))
                    lang = server_coll.find_one({ "server": f"{guild.id}" })["lang"]
                    if lang == "ru":
                        e = discord.Embed(title="Магазин Паймон", description=f"Время для покупки вышло.", color=discord.Color(0x2F3136))
                    else:
                        e = discord.Embed(title="Shop", description=f"Time to buy is up.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                    return None
                elif data["type"] == "waifu":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["for_id"]))
                    lang = server_coll.find_one({ "server": f"{guild.id}" })["lang"]
                    if lang == "ru":
                        e = discord.Embed(title="Магазин Паймон", description=f"Время для покупки вышло.", color=discord.Color(0x2F3136))
                    else:
                        e = discord.Embed(title="Shop", description=f"Time to buy is up.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                    return None
                elif data["type"] == "custom":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["for_id"]))
                    lang = server_coll.find_one({ "server": f"{guild.id}" })["lang"] 
                    if lang == "ru":
                        e = discord.Embed(title="Магазин Паймон", description=f"Время для покупки вышло.", color=discord.Color(0x2F3136))
                    else:
                        e = discord.Embed(title="Shop", description=f"Time to buy is up.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                    return None
                elif data["type"] == "marry":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))

                    member = guild.get_member(int(data["author"]))
                    member2 = guild.get_member(int(data["for_id"]))
                    lang = db.server.find_one({ "server": f"{guild.id}" })["lang"]
                    if lang == "ru":
                        e = discord.Embed(title="Свадьба: игнор", description=f"<@{str(member2.id)}> тебя проигнорировал(-а) :c", color=discord.Color(0x2F3136))
                    else:
                        e = discord.Embed(title="Marry: ignore", description=f"<@{str(member2.id)}> ignored you :c", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                    return None
                elif data["type"] == "reaction":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))

                    member = guild.get_member(int(data["id"]))
                    member2 = guild.get_member(int(data["mention_id"]))
                
                    lang = server_coll.find_one({ "server": f"{guild.id}" })["lang"]

                    if lang == "ru":
                        e = discord.Embed(title="Реакция: игнор", description=f"<@{str(member2.id)}> тебя проигнорировал(-а) :c", color=discord.Color(0x2F3136))
                    else:
                        e = discord.Embed(title="Reaction: ignore", description=f"<@{str(member2.id)}> ignored you :c", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=e)
                    if data["react"] != 4:
                        author_m = db.prof_ec_users.find_one({"disid": str(member.id), "guild": f"{member.guild.id}"})
                        ms = author_m["moneystats"]
                        ms["1d"] += config.reaction_two
                        ms["7d"] += config.reaction_two
                        ms["14d"] += config.reaction_two
                        ms["all"] += config.reaction_two
                        if ms["history_1d"]["reactions"]["view"] == 0:
                            ms["history_1d"]["reactions"]["view"] = 1
                        ms["history_1d"]["reactions"]["count"] += config.reaction_two
                        if ms["history"]["reactions"]["view"] == 0:
                            ms["history"]["reactions"]["view"] = 1
                        ms["history"]["reactions"]["count"] += config.reaction_two
                        db.prof_ec_users.update_one({"disid": str(member.id), "guild": str(member.guild.id)}, { "$set": { "money": author_m["money"] + config.reaction_two, "moneystats": ms } })
                    coll.delete_one({ "message_id": data["message_id"] })
                    return None
                elif data["type"] == "love_room_create":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["for_id"]))
                    lang = server_coll.find_one({ "server": f"{guild.id}" })["lang"]
                    if lang == "ru":
                        e = discord.Embed(title="Любовная комнатка: Покупка", description=f"Время для покупки вышло.", color=discord.Color(0x2F3136))
                    else:
                        e = discord.Embed(title="Love Room: Purchase", description=f"Time to buy is up.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=e)
                    coll.delete_one({ "message_id": data["message_id"] })
                    return None
            except BaseException as e:
                print(f"Error reactions: {e}")
