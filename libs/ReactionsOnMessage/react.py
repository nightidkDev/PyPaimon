import datetime
import random
import time
import asyncio
import sys
import numpy
import sqlite3
sys.path.append("../../")
from libs import Builders
from libs import DataBase
from plugins import funcb
import os

async def checkbuy_r(role, cost, money_emoji, user, lang):
    items = list(user["inv"])
    items = list(filter(lambda x: x["type"] == "role", items))
    items = list(map(lambda x: list(x.items())[1][1], items))
    if role in items:
        if lang == "ru":
            return "Куплено!"
        else:
            return "Purchased!"
    else:
        return f"{cost}{money_emoji}"

async def checkbuy_c(custom, cost, money_emoji, user, lang):
    items = list(user["inv"])
    items = list(filter(lambda x: x["type"] == "background", items))
    items = list(map(lambda x: list(x.items())[1][1], items))
    if custom in items:
        if lang == "ru":
            return "Куплено!"
        else:
            return "Purchased!"
    else:
        return f"{cost}{money_emoji}"

async def sleeptime(time):
    await asyncio.sleep(int(time))

def fifty_fifty():
    "Return 0 or 1 with 50% chance for each"
    return random.randrange(2)

async def react(client, discord, user, message, db, emoji, Economy, config):
    if message.author.id == client.user.id:
        con = sqlite3.connect("duels.db", check_same_thread=False)
        cur = con.cursor()
        info = cur.execute(f"SELECT * FROM duels WHERE message_id={message.id}").fetchall()
        if info:
            if info[0][2] != user.id:
                return 
            elif info[0][7] == "duel":
                return
            else:
                if str(emoji) == "✅":
                    users = db.prof_ec_users
                    money_emoji = client.get_emoji(config.MONEY_EMOJI)
                    sum = info[0][6]
                    member = message.guild.get_member(info[0][1])
                    member2 = message.guild.get_member(info[0][2])
                    author_m = users.find_one({"disid": f"{member.id}", "guild": f"{member.guild.id}"})["money"]
                    mention_m = users.find_one({"disid": f"{member2.id}", "guild": f"{member.guild.id}"})["money"]
                    if author_m < sum:
                        e = discord.Embed(title="", description=f"Невозможно завершить действие, недостаточно примогемов у отправителя.", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.clear_reactions()
                        cur.execute(f"DELETE FROM duels WHERE message_id={message.id}")
                        con.commit()
                        con.close()
                        return await message.edit(embed=e)
                    elif mention_m < sum:
                        e = discord.Embed(title="", description=f"Невозможно завершить действие, недостаточно примогемов у противника.", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.clear_reactions()
                        cur.execute(f"DELETE FROM duels WHERE message_id={message.id}")
                        con.commit()
                        con.close()
                        return await message.edit(embed=e)
                    else:
                        cur.execute(f"UPDATE duels SET time={int(time.time()) + 60}, status='duel' WHERE message_id={message.id}")
                        con.commit()
                        con.close()
                        photo = config.duel
                        e = discord.Embed(title="Реакция: дуэль", description=f"<@{str(member.id)}> сражается с <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_image(url=random.choice(photo))
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        await sleeptime(8)
                        con = sqlite3.connect("duels.db", check_same_thread=False)
                        cur = con.cursor()
                        cur.execute(f"DELETE FROM duels WHERE message_id={message.id}")
                        con.commit()
                        con.close()
                        winner = fifty_fifty()
                        if winner == 1:
                            winner = member
                            defeat = member2
                        else:
                            winner = member2
                            defeat = member
                        e2 = discord.Embed(title="Реакция: дуэль", description=f"<@{winner.id}> победил(-a) и получил(-a) {sum + sum}{money_emoji}!", color=discord.Color(0x2F3136))
                        e2.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        users = db.prof_ec_users
                        winb = users.find_one({"disid": str(winner.id), "guild": str(message.guild.id)})
                        deafb = users.find_one({"disid": str(defeat.id), "guild": str(message.guild.id)})
                        ms = winb["moneystats"]
                        ms2 = deafb["moneystats"]
                        ms["1d"] += sum
                        ms2["1d"] -= sum
                        ms["7d"] += sum
                        ms2["7d"] -= sum
                        ms["14d"] += sum
                        ms2["14d"] -= sum
                        ms["all"] += sum
                        ms2["all"] -= sum
                        if ms["history_1d"]["reactions"]["view"] == 0:
                            ms["history_1d"]["reactions"]["view"] = 1
                        ms["history_1d"]["reactions"]["count"] += sum
                        if ms["history"]["reactions"]["view"] == 0:
                            ms["history"]["reactions"]["view"] = 1
                        ms["history"]["reactions"]["count"] += sum
                        if ms2["history_1d"]["reactions"]["view"] == 0:
                            ms2["history_1d"]["reactions"]["view"] = 1
                        ms2["history_1d"]["reactions"]["count"] -= sum
                        if ms2["history"]["reactions"]["view"] == 0:
                            ms2["history"]["reactions"]["view"] = 1
                        ms2["history"]["reactions"]["count"] -= sum
                        users.update_one({"disid": str(winner.id), "guild": str(message.guild.id)}, { "$set": { "money": winb["money"] + sum, "moneystats": ms } })
                        users.update_one({"disid": str(defeat.id), "guild": str(message.guild.id)}, { "$set": { "money": deafb["money"] - sum, "moneystats": ms2 } })
                        e2.timestamp = datetime.datetime.utcnow()
                        await message.clear_reactions()
                        await message.edit(embed=e2)
                elif str(emoji) == "❌":
                    await message.clear_reactions()
                    member = message.guild.get_member(info[0][1])
                    member2 = message.guild.get_member(info[0][2])
                    e = discord.Embed(title="Реакция: отказ", description=f"<@{str(member2.id)}> тебе отказал(-а) :(", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=e)
                    cur.execute(f"DELETE FROM duels WHERE message_id={message.id}")
                    con.commit()
                    con.close()
        coll = db.reactions
        data = coll.find({"message_id": str(message.id)})
        if coll.count_documents({ "message_id": str(message.id) }) == 0:
            return None
        if message.id == int(data[0]["message_id"]):
            if data[0]["type"] == "pages_shop_r":
                if user.id == int(data[0]["for_id"]):
                    member = message.guild.get_member(int(data[0]["for_id"]))
                    guild = member.guild
                    money_emoji = client.get_emoji(config.MONEY_EMOJI)
                    coll_shop = db.shops_list
                    roles = coll_shop.find({"type": "roles", "guild": f"{message.guild.id}"}).sort("cost", 1)
                    #roles = list(roles)
                    coll_user = db.prof_ec_users
                    user_b = coll_user.find_one({"disid": str(data[0]["for_id"])})
                    lang = db.server.find_one({ "server": f"{guild.id}" })["lang"]
                    arrow_left = client.get_emoji(826568061854416946)
                    arrow_right = client.get_emoji(826567984901390366)
                    if str(emoji.id) == "826567984901390366":
                        all_len = data[0]["all_len"]
                        atnowl = data[0]["atnowl"] + 8
                        bfnowl = data[0]["bfnowl"]
                        if bfnowl + 8 < all_len:
                            bfnowl = data[0]["bfnowl"] + 8
                        else:
                            bfnowl = all_len
                        if atnowl > all_len:
                            return
                        e = discord.Embed(title=f"Магазин Паймон: Кастомизация ({data[0]['page'] + 1}/{data[0]['pages']})", description="", color=discord.Color(0x2F3136))
                        for i in range(atnowl, bfnowl):
                            role = roles[i]["id"]
                            cost = await checkbuy_r(role, str(roles[i]["cost"]), money_emoji, user_b, lang)
                            
                            e.add_field(name="Индекс", value=f"{i + 1}.", inline=True)
                            e.add_field(name="Роль", value=f"<@&{role}>", inline=True)
                            e.add_field(name="Цена", value=f"{cost}", inline=True)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        await message.clear_reactions()
                        if bfnowl < all_len:
                            await message.add_reaction(arrow_left)
                            await message.add_reaction(arrow_right)
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] + 1, "atnowl": atnowl, "bfnowl": bfnowl, "time": int(time.time()) + 15} })
                        else:
                            await message.add_reaction(arrow_left)
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] + 1, "atnowl": atnowl, "bfnowl": all_len, "time": int(time.time()) + 15} })
                    if str(emoji.id) == "826568061854416946":
                        all_len = data[0]["all_len"]
                        atnowl = data[0]["atnowl"]
                        bfnowl = data[0]["bfnowl"]
                        
                        if bfnowl - 8 >= 8:
                            if bfnowl == all_len:
                                bfnowl = bfnowl - (bfnowl - atnowl)
                            else:
                                bfnowl = bfnowl - 8
                        else:
                            bfnowl = 8
                        atnowl -= 8
                        if atnowl < 0:
                            return
                        e = discord.Embed(title=f"Магазин Паймон: Роли ({data[0]['page'] - 1}/{data[0]['pages']})", description="", color=discord.Color(0x2F3136))
                        for i in range(atnowl, bfnowl):
                            role = roles[i]["id"]
                            cost = await Economy.checkbuy_r(role, str(roles[i]["cost"]), money_emoji, user_b, lang) 
                            
                            e.add_field(name="Индекс", value=f"{i + 1}.", inline=True)
                            e.add_field(name="Роль", value=f"<@&{role}>", inline=True)
                            e.add_field(name="Цена", value=f"{cost}", inline=True)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        await message.clear_reactions()
                        if bfnowl != 8 and bfnowl != all_len:
                            await message.add_reaction(arrow_left)
                            await message.add_reaction(arrow_right)
                        else:
                            await message.add_reaction(arrow_right)
                        if bfnowl == 8:
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] - 1, "atnowl": 0, "bfnowl": 8, "time": int(time.time()) + 15 } })
                        else:
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] - 1, "atnowl": atnowl, "bfnowl": bfnowl, "time": int(time.time()) + 15 } })
            elif data[0]["type"] == "pages_shop_w":
                if user.id == int(data[0]["for_id"]):
                    member = message.guild.get_member(int(data[0]["for_id"]))
                    guild = member.guild
                    money_emoji = client.get_emoji(config.MONEY_EMOJI)
                    coll_shop = db.waifu
                    roles = list(coll_shop.find())
                    #roles = list(roles)
                    coll_user = db.prof_ec_users
                    user_b = coll_user.find_one({"disid": str(data[0]["for_id"])})
                    lang = db.server.find_one({ "server": f"{guild.id}" })["lang"]
                    arrow_left = client.get_emoji(826568061854416946)
                    arrow_right = client.get_emoji(826567984901390366)
                    if str(emoji.id) == "826567984901390366":
                        all_len = data[0]["all_len"]
                        atnowl = data[0]["atnowl"] + 8
                        bfnowl = data[0]["bfnowl"]
                        if bfnowl + 8 < all_len:
                            bfnowl = data[0]["bfnowl"] + 8
                        else:
                            bfnowl = all_len
                        if atnowl > all_len:
                            return
                        e = discord.Embed(title=f"Магазин Паймон: Вайфу | Хасубандо ({data[0]['page'] + 1}/{data[0]['pages']})", description="", color=discord.Color(0x2F3136))
                        for i in range(atnowl, bfnowl):
                            role = roles[i]["id"]
                            cost = await checkbuy_r(role, str(roles[i]["cost"]), money_emoji, user_b, lang)
                            
                            e.add_field(name="Индекс", value=f"{i + 1}.", inline=True)
                            e.add_field(name="Карточка", value=f"<@&{role}>", inline=True)
                            e.add_field(name="Цена", value=f"{cost}", inline=True)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        await message.clear_reactions()
                        if bfnowl < all_len:
                            await message.add_reaction(arrow_left)
                            await message.add_reaction(arrow_right)
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] + 1, "atnowl": atnowl, "bfnowl": bfnowl, "time": int(time.time()) + 15} })
                        else:
                            await message.add_reaction(arrow_left)
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] + 1, "atnowl": atnowl, "bfnowl": all_len, "time": int(time.time()) + 15} })
                    if str(emoji.id) == "826568061854416946":
                        all_len = data[0]["all_len"]
                        atnowl = data[0]["atnowl"]
                        bfnowl = data[0]["bfnowl"]
                        
                        if bfnowl - 8 >= 8:
                            if bfnowl == all_len:
                                bfnowl = bfnowl - (bfnowl - atnowl)
                            else:
                                bfnowl = bfnowl - 8
                        else:
                            bfnowl = 8
                        atnowl -= 8
                        if atnowl < 0:
                            return
                        e = discord.Embed(title=f"Магазин Паймон: Вайфу | Хасубандо ({data[0]['page'] - 1}/{data[0]['pages']})", description="", color=discord.Color(0x2F3136))
                        for i in range(atnowl, bfnowl):
                            role = roles[i]["id"]
                            cost = await Economy.checkbuy_r(role, str(roles[i]["cost"]), money_emoji, user_b, lang) 
                            
                            e.add_field(name="Индекс", value=f"{i + 1}.", inline=True)
                            e.add_field(name="Роль", value=f"<@&{role}>", inline=True)
                            e.add_field(name="Цена", value=f"{cost}", inline=True)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        await message.clear_reactions()
                        if bfnowl != 8 and bfnowl != all_len:
                            await message.add_reaction(arrow_left)
                            await message.add_reaction(arrow_right)
                        else:
                            await message.add_reaction(arrow_right)
                        if bfnowl == 8:
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] - 1, "atnowl": 0, "bfnowl": 8, "time": int(time.time()) + 15 } })
                        else:
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] - 1, "atnowl": atnowl, "bfnowl": bfnowl, "time": int(time.time()) + 15 } })
            elif data[0]["type"] == "pages_shop_c":
                if user.id == int(data[0]["for_id"]):
                    member = message.guild.get_member(int(data[0]["for_id"]))
                    guild = member.guild
                    money_emoji = client.get_emoji(config.MONEY_EMOJI)
                    coll_shop = db.backgrounds
                    custom = data[0]["category"]
                    coll_user = db.prof_ec_users
                    user_b = coll_user.find_one({"disid": str(data[0]["for_id"])})
                    lang = db.server.find_one({ "server": f"{guild.id}" })["lang"]
                    arrow_left = client.get_emoji(826568061854416946)
                    arrow_right = client.get_emoji(826567984901390366)
                    if str(emoji.id) == "826567984901390366":
                        if data[0]["page"] >= data[0]["pages"]:
                            return
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки ({data[0]['page'] + 1}/{data[0]['pages']})", description="", color=discord.Color(0x2F3136))
                        i = data[0]['page']
                        custom_id = custom[i]["id"] 
                        cname = custom[i]["name"]
                        cost = await checkbuy_c(custom_id, str(custom[i]["cost"]), money_emoji, user_b, lang) 
                        e.description = f"Индекс: {custom_id}\nНазвание: {cname}\nЦена: {cost}"
                        e.set_image(url=f"http://f0528562.xsph.ru/imgs/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        if data[0]["page"] + 1 < data[0]["pages"]:
                            await message.remove_reaction(arrow_right, member)
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] + 1, "time": int(time.time()) + 25} })
                        else:
                            await message.remove_reaction(arrow_right, member)
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] + 1, "time": int(time.time()) + 25} })
                    if str(emoji.id) == "826568061854416946":
                        
                        if data[0]["page"] <= 1:
                            return
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки ({data[0]['page'] - 1}/{data[0]['pages']})", description="", color=discord.Color(0x2F3136))
                        i = data[0]['page'] - 2
                        custom_id = custom[i]["id"] 
                        cname = custom[i]["name"]
                        cost = await checkbuy_c(custom_id, str(custom[i]["cost"]), money_emoji, user_b, lang) 
                        e.description = f"Индекс: {custom_id}\nНазвание: {cname}\nЦена: {cost}"
                        e.set_image(url=f"http://f0528562.xsph.ru/imgs/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        if data[0]["page"] - 1 != 1:
                            await message.remove_reaction(arrow_left, member)
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] - 1, "time": int(time.time()) + 25} })
                        else:
                            await message.remove_reaction(arrow_left, member)
                            coll.update_one({"message_id": str(message.id)}, { "$set": { "page": data[0]["page"] - 1, "time": int(time.time()) + 25} })
            elif data[0]["type"] == "pages_shop_category":
                member = message.guild.get_member(int(data[0]["for_id"]))
                money_emoji = client.get_emoji(config.MONEY_EMOJI)
                bgs = db.backgrounds
                users = db.prof_ec_users
                custom = bgs.find({ "id": { "$gte": 1 } }).sort("id", 1)
                user_b = users.find_one({"disid": str(member.id), "guild": f"{member.guild.id}"})
                custom = list(custom)
                
                if str(emoji.id) == "826888313448562758":
                    battlepass = list(filter(lambda x: x["category"] == "battlepass", custom))
                    await message.clear_reactions()
                    if len(battlepass) > 1:
                        pages_len = len(battlepass)
                        i = 0
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки - Боевой пропуск (1/{pages_len})", description="", color=discord.Color(0x2F3136))
                        custom_id = battlepass[i]["id"] 
                        cname = battlepass[i]["name"]
                        cost = await checkbuy_c(custom_id, str(battlepass[i]["cost"]), money_emoji, user_b, "ru")
                        e.description = f"Индекс: {custom_id}\nНазвание: {cname}\nЦена: {cost}"
                        e.set_image(url=f"http://f0528562.xsph.ru/imgs/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        db.reactions.delete_one({ "message_id": str(message.id) })
                        await Builders.Builder().build(client, "pages_shop_c", 30, message, member, "ru", battlepass, len(battlepass))
                elif str(emoji.id) == "826888462116061234":
                    achievements = list(filter(lambda x: x["category"] == "achievements", custom))
                    await message.clear_reactions()
                    if len(achievements) > 1:
                        pages_len = len(achievements)
                        i = 0
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки - Достижения (1/{pages_len})", description="", color=discord.Color(0x2F3136))
                        custom_id = achievements[i]["id"] 
                        cname = achievements[i]["name"]
                        cost = await checkbuy_c(custom_id, str(achievements[i]["cost"]), money_emoji, user_b, "ru")
                        e.description = f"Индекс: {custom_id}\nНазвание: {cname}\nЦена: {cost}"
                        e.set_image(url=f"http://f0528562.xsph.ru/imgs/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        db.reactions.delete_one({ "message_id": str(message.id) })
                        await Builders.Builder().build(client, "pages_shop_c", 30, message, member, "ru", achievements, len(achievements))
                elif str(emoji.id) == "826888462027194410":
                    another = list(filter(lambda x: x["category"] == "another", custom))
                    await message.clear_reactions()
                    if len(another) > 1:
                        pages_len = len(another)
                        i = 0
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки - Другое (1/{pages_len})", description="", color=discord.Color(0x2F3136))
                        custom_id = another[i]["id"] 
                        cname = another[i]["name"]
                        cost = await checkbuy_c(custom_id, str(another[i]["cost"]), money_emoji, user_b, "ru")
                        e.description = f"Индекс: {custom_id}\nНазвание: {cname}\nЦена: {cost}"
                        e.set_image(url=f"http://f0528562.xsph.ru/imgs/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        db.reactions.delete_one({ "message_id": str(message.id) })
                        await Builders.Builder().build(client, "pages_shop_c", 30, message, member, "ru", another, len(another))
                    else:
                        pages_len = len(another)
                        i = 0
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки - Другое (1/{pages_len})", description="", color=discord.Color(0x2F3136))
                        custom_id = another[i]["id"] 
                        cname = another[i]["name"]
                        cost = await checkbuy_c(custom_id, str(another[i]["cost"]), money_emoji, user_b, "ru")
                        e.description = f"Индекс: {custom_id}\nНазвание: {cname}\nЦена: {cost}"
                        e.set_image(url=f"http://f0528562.xsph.ru/imgs/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        db.reactions.delete_one({ "message_id": str(message.id) })
                elif str(emoji.id) == "826888461994557519":
                    rep = list(filter(lambda x: x["category"] == "rep", custom))
                    await message.clear_reactions()
                    if len(rep) > 1:
                        pages_len = len(rep)
                        i = 0
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки - Репутация (1/{pages_len})", description="", color=discord.Color(0x2F3136))
                        custom_id = rep[i]["id"] 
                        cname = rep[i]["name"]
                        cost = await checkbuy_c(custom_id, str(rep[i]["cost"]), money_emoji, user_b, "ru")
                        e.description = f"Индекс: {custom_id}\nНазвание: {cname}\nЦена: {cost}"
                        e.set_image(url=f"http://f0528562.xsph.ru/imgs/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        db.reactions.delete_one({ "message_id": str(message.id) })
                        await Builders.Builder().build(client, "pages_shop_c", 30, message, member, "ru", rep, len(rep))
                elif str(emoji.id) == "826888461989445672":
                    events = list(filter(lambda x: x["category"] == "events", custom))
                    await message.clear_reactions()
                    if len(events) > 1:
                        pages_len = len(events)
                        i = 0
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки - Ивенты (1/{pages_len})", description="", color=discord.Color(0x2F3136))
                        custom_id = events[i]["id"] 
                        cname = events[i]["name"]
                        cost = await checkbuy_c(custom_id, str(events[i]["cost"]), money_emoji, user_b, "ru")
                        e.description = f"Индекс: {custom_id}\nНазвание: {cname}\nЦена: {cost}"
                        e.set_image(url=f"http://f0528562.xsph.ru/imgs/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        db.reactions.delete_one({ "message_id": str(message.id) })
                        await Builders.Builder().build(client, "pages_shop_c", 30, message, member, "ru", events, len(events))
                elif str(emoji.id) == "826888462011203594":
                    characters = list(filter(lambda x: x["category"] == "characters", custom))
                    await message.clear_reactions()
                    if len(characters) > 1:
                        pages_len = len(characters)
                        i = 0
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки - Персонажи (1/{pages_len})", description="", color=discord.Color(0x2F3136))
                        custom_id = characters[i]["id"] 
                        cname = characters[i]["name"]
                        cost = await checkbuy_c(custom_id, str(characters[i]["cost"]), money_emoji, user_b, "ru")
                        e.description = f"Индекс: {custom_id}\nНазвание: {cname}\nЦена: {cost}"
                        e.set_image(url=f"http://f0528562.xsph.ru/imgs/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.edit(embed=e)
                        db.reactions.delete_one({ "message_id": str(message.id) })
                        await Builders.Builder().build(client, "pages_shop_c", 30, message, member, "ru", characters, len(characters))
            elif data[0]["type"] == "role":
                if user.id == int(data[0]["for_id"]):
                    member = message.guild.get_member(int(data[0]["for_id"]))
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        coll_user = db.prof_ec_users
                        user = coll_user.find({"disid": str(member.id), "guild": f"{member.guild.id}"})
                        if user[0]["money"] < data[0]['cost']:
                            e = discord.Embed(title="", description=f"Невозможно завершить сделку, недостаточно примогемов.", color=discord.Color(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await message.clear_reactions()
                            return await message.edit(embed=e)
                        role_id = data[0]['role_id']
                        item = { "type": "role", "id": role_id }
                        coll_user.update_one({"disid": str(member.id), "guild": f"{member.guild.id}"}, { "$push": { "inv": item } })
                        ms = user[0]["moneystats"]
                        ms["1d"] -= data[0]['cost']
                        ms["7d"] -= data[0]['cost']
                        ms["14d"] -= data[0]['cost']
                        ms["all"] -= data[0]['cost']
                        if ms["history_1d"]["shop"]["view"] == 0:
                            ms["history_1d"]["shop"]["view"] = 1
                        ms["history_1d"]["shop"]["count"] -= data[0]['cost']
                        if ms["history"]["shop"]["view"] == 0:
                            ms["history"]["shop"]["view"] = 1
                        ms["history"]["shop"]["count"] -= data[0]['cost']
                        coll_user.update_one({"disid": str(member.id), "guild": f"{member.guild.id}"}, { "$set": { "money": user[0]["money"] - data[0]['cost'], "moneystats": ms } })
                        e = discord.Embed(title="Магазин Паймон", description=f"Покупка совершена! Роль <@&{data[0]['role_id']}> была добавлена в инвентарь.", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        coll.delete_one({"message_id": data[0]["message_id"]})
                    elif str(emoji) == "❌":
                        e = discord.Embed(title="Магазин Паймон", description=f"Покупка отменена.", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        coll.delete_one({"message_id": data[0]["message_id"]})
            elif data[0]["type"] == "waifu":
                if user.id == int(data[0]["for_id"]):
                    member = message.guild.get_member(int(data[0]["for_id"]))
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        coll_user = db.prof_ec_users
                        user = coll_user.find({"disid": str(member.id), "guild": f"{member.guild.id}"})
                        if user[0]["money"] < data[0]['cost']:
                            e = discord.Embed(title="", description=f"Невозможно завершить сделку, недостаточно примогемов.", color=discord.Color(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await message.clear_reactions()
                            return await message.edit(embed=e)
                        role_id = data[0]['role_id']
                        item = { "type": "waifu", "id": role_id, "equip": 0 }
                        coll_user.update_one({"disid": str(member.id), "guild": f"{member.guild.id}"}, { "$push": { "inv": item } })
                        ms = user[0]["moneystats"]
                        ms["1d"] -= data[0]['cost']
                        ms["7d"] -= data[0]['cost']
                        ms["14d"] -= data[0]['cost']
                        ms["all"] -= data[0]['cost']
                        if ms["history_1d"]["shop"]["view"] == 0:
                            ms["history_1d"]["shop"]["view"] = 1
                        ms["history_1d"]["shop"]["count"] -= data[0]['cost']
                        if ms["history"]["shop"]["view"] == 0:
                            ms["history"]["shop"]["view"] = 1
                        ms["history"]["shop"]["count"] -= data[0]['cost']
                        coll_user.update_one({"disid": str(member.id), "guild": f"{member.guild.id}"}, { "$set": { "money": user[0]["money"] - data[0]['cost'], "moneystats": ms } })
                        e = discord.Embed(title="Магазин Паймон", description=f"Покупка совершена! Вайфу <@&{data[0]['role_id']}> была добавлена в инвентарь.", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        coll.delete_one({"message_id": data[0]["message_id"]})
                    elif str(emoji) == "❌":
                        e = discord.Embed(title="Магазин Паймон", description=f"Покупка отменена.", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        coll.delete_one({"message_id": data[0]["message_id"]})
            elif data[0]["type"] == "custom":
                if user.id == int(data[0]["for_id"]):
                    member = message.guild.get_member(int(data[0]["for_id"]))
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        coll_user = db.prof_ec_users
                        user = coll_user.find({"disid": str(member.id), "guild": f"{member.guild.id}"})
                        if user[0]["money"] < data[0]['cost']:
                            e = discord.Embed(title="", description=f"Невозможно завершить сделку, недостаточно примогемов.", color=discord.Color(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await message.clear_reactions()
                            return await message.edit(embed=e)
                        item = { "type": "background", "id": data[0]["bgn"] }
                        coll_user.update_one({"disid": str(member.id), "guild": f"{member.guild.id}"}, { "$push": { "inv": item } })
                        ms = user[0]["moneystats"]
                        ms["1d"] -= data[0]['cost']
                        ms["7d"] -= data[0]['cost']
                        ms["14d"] -= data[0]['cost']
                        ms["all"] -= data[0]['cost']
                        if ms["history_1d"]["shop"]["view"] == 0:
                            ms["history_1d"]["shop"]["view"] = 1
                        ms["history_1d"]["shop"]["count"] -= data[0]['cost']
                        if ms["history"]["shop"]["view"] == 0:
                            ms["history"]["shop"]["view"] = 1
                        ms["history"]["shop"]["count"] -= data[0]['cost']
                        coll_user.update_one({"disid": str(member.id), "guild": f"{member.guild.id}"}, { "$set": { "money": user[0]["money"] - data[0]['cost'], "moneystats": ms } })
                        custom_name = client.get_emoji(int(data[0]['name']))
                        e = discord.Embed(title="Магазин Паймон", description=f"Покупка совершена! {custom_name} была добавлена в инвентарь.", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        coll.delete_one({"message_id": data[0]["message_id"]})
                    elif str(emoji) == "❌":
                        e = discord.Embed(title="Магазин Паймон", description=f"Покупка отменена.", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        coll.delete_one({"message_id": data[0]["message_id"]})
            elif data[0]["type"] == "marry":
                if user.id == int(data[0]["for_id"]):
                    #message = await reaction.message.channel.fetch_message(int(reaction.message.id))
                    member = message.guild.get_member(int(data[0]["for_id"]))
                    member2 = message.guild.get_member(int(data[0]["author"]))
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        marry_role = message.guild.get_role(772569219555917834)
                        coll_user = db.prof_ec_users
                        author_m = coll_user.find_one({"disid": data[0]["author"], "guild": f"{member2.guild.id}"})
                        if author_m["money"] < config.marry:
                            e = discord.Embed(title="", description=f"Невозможно завершить брак, недостаточно примогемов у отправителя.", color=discord.Color(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await message.clear_reactions()
                            return await message.edit(embed=e)
                        photo = ["https://cdn.discordapp.com/attachments/677839189991096350/746411914224992377/1Fhe.gif",
                                "https://cdn.discordapp.com/attachments/677839189991096350/746411918436335731/1fd892054b61087f06c3fd111e233124.gif",
                                "https://cdn.discordapp.com/attachments/677839189991096350/746411917794344990/270deadfc183b447aa36c38d92e00e19.gif",
                                "https://cdn.discordapp.com/attachments/677839189991096350/746411920508321832/NVDz.gif",
                                "https://cdn.discordapp.com/attachments/677839189991096350/746411920470441994/1405163520_lovestage-episode1-omake-6.gif"
                                ]
                        e = discord.Embed(title="Свадьба", description=f"<@!{data[0]['for_id']}> и <@!{data[0]['author']}> стали парой!", color=discord.Color(0x2F3136))
                        e.set_image(url=random.choice(photo))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member2.display_name}", icon_url=member2.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        coll.delete_one({"message_id": data[0]["message_id"]})
                        await member.add_roles(marry_role)
                        await member2.add_roles(marry_role)
                        love_room_category = message.guild.get_channel(876594464502743110)
                        #voice = await message.guild.create_voice_channel(f"{member.name} 💞 {member2.name}", category=love_room_category, user_limit=2)
                        tx = int(time.time())
                        ms = author_m["moneystats"]
                        ms["1d"] -= config.marry
                        ms["7d"] -= config.marry
                        ms["14d"] -= config.marry
                        ms["all"] -= config.marry
                        if ms["history_1d"]["marriage"]["view"] == 0:
                            ms["history_1d"]["marriage"]["view"] = 1
                        ms["history_1d"]["marriage"]["count"] -= config.marry
                        if ms["history"]["marriage"]["view"] == 0:
                            ms["history"]["marriage"]["view"] = 1
                        ms["history"]["marriage"]["count"] -= config.marry
                        coll_user.update_one({"disid": f"{member.id}", "guild": f"{member.guild.id}"}, { "$set": { "partner": f"{member2.id}", "marry_time": tx, "love_room": "", "love_room_created": 0 } })
                        coll_user.update_one({"disid": f"{member2.id}", "guild": f"{member.guild.id}"}, { "$set": { "partner": f"{member.id}", "marry_time": tx, "money": author_m["money"] - config.marry, "love_room": "", "love_room_created": 0, "moneystats": ms } })
                        #await voice.set_permissions(member2, manage_channels=True,
                        #                                     connect=True,
                        #                                     speak=True)
                        #await voice.set_permissions(member, manage_channels=True,
                        #                                    connect=True,
                        #                                    speak=True)
                        #rooms = db.love_rooms
                        #rooms.insert_one({ "id": f"{voice.id}", "owner1": f"{member.id}", "owner2": f"{member2.id}", "ctime": int(time.time()), "ptime": int(time.time()) + 2592000, "notify": "false", "payment": "false" })
                    elif str(emoji) == "❌":
                        e = discord.Embed(title="Свадьба: отказ", description=f"<@{str(member.id)}> тебе отказал(-а) :(", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member2.display_name}", icon_url=member2.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        coll.delete_one({"message_id": data[0]["message_id"]})
            elif data[0]["type"] == "reaction":
                if user.id != int(data[0]["mention_id"]):
                    return None
                else:
                    member = message.guild.get_member(int(data[0]["id"]))
                    member2 = message.guild.get_member(int(data[0]["mention_id"]))
                    money_emoji = client.get_emoji(775362271085461565)
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        if data[0]["react"] == 1:
                            photo = config.kiss
                            if data[0]["lang"] == "ru":
                                e = discord.Embed(title="Реакция: поцелуй", description=f"<@{str(member.id)}> поцеловал(-а) <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} примогемов", icon_url=member.avatar_url)
                            elif data[0]["lang"] == "en":
                                e = discord.Embed(title="Reaction: kiss", description=f"<@{str(member.id)}> kissed <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} stars", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_image(url=random.choice(photo))
                            #message = await reaction.message.channel.fetch_message(int(reaction.message.id))
                            await message.clear_reactions()
                            await message.edit(embed=e)
                            coll.delete_one({"message_id": data[0]["message_id"]})
                        elif data[0]["react"] == 2:
                            photo = config.cheek
                            e = discord.Embed(title="Реакция: поцелуй в щёку", description=f"<@{str(member.id)}> поцеловал(-а) **в щёку** <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                            e.set_footer(text=f"{member.display_name} • {config.reaction_two} примогемов", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_image(url=random.choice(photo))
                            #message = await reaction.message.channel.fetch_message(int(reaction.message.id))
                            await message.clear_reactions()
                            await message.edit(embed=e)
                            coll.delete_one({"message_id": data[0]["message_id"]})
                        elif data[0]["react"] == 3:
                            photo = config.virt
                            if data[0]["lang"] == "ru":
                                e = discord.Embed(title="Реакция: вирт", description=f"<@{str(member.id)}> и <@{str(member2.id)}> **виртят**!", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} примогемов", icon_url=member.avatar_url)
                            elif data[0]["lang"] == "en":
                                e = discord.Embed(title="Reaction: virt", description=f"<@{str(member.id)}> and <@{str(member2.id)}> are **flirting** with each other!", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} stars", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_image(url=random.choice(photo))
                            #message = await reaction.message.channel.fetch_message(int(reaction.message.id))
                            await message.clear_reactions()
                            await message.edit(embed=e)
                            coll.delete_one({"message_id": data[0]["message_id"]})
                        elif data[0]["react"] == 5:
                            photo = config.dance
                            if data[0]["lang"] == "ru":
                                e = discord.Embed(title="Реакция: танец", description=f"<@{str(member.id)}> танцует с <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} примогемов", icon_url=member.avatar_url)
                            elif data[0]["lang"] == "en":
                                e = discord.Embed(title="Reaction: dance", description=f"<@{str(member.id)}> dancing with <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} stars", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_image(url=random.choice(photo))
                            await message.clear_reactions()
                            await message.edit(embed=e)
                            coll.delete_one({"message_id": data[0]["message_id"]})

                        elif data[0]["react"] == 6: 
                            photo = config.hand
                            if data[0]["lang"] == "ru":
                                e = discord.Embed(title="Реакция: взять за руку", description=f"<@{str(member.id)}> взял за руку <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} примогемов", icon_url=member.avatar_url)
                            elif data[0]["lang"] == "en":
                                e = discord.Embed(title="Реакция: взять за руку", description=f"<@{str(member.id)}> взял за руку <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} примогемов", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_image(url=random.choice(photo))
                            await message.clear_reactions()
                            await message.edit(embed=e)
                            coll.delete_one({"message_id": data[0]["message_id"]})
                        elif data[0]["react"] == 7: 
                            photo = config.onhands
                            if data[0]["lang"] == "ru":
                                e = discord.Embed(title="Реакция: взять на ручки", description=f"<@{str(member.id)}> взял на ручки <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_one} примогемов", icon_url=member.avatar_url)
                            elif data[0]["lang"] == "en":
                                e = discord.Embed(title="Реакция: взять на ручки", description=f"<@{str(member.id)}> взял на ручки <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_one} примогемов", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_image(url=random.choice(photo))
                            await message.clear_reactions()
                            await message.edit(embed=e)
                            coll.delete_one({"message_id": data[0]["message_id"]})
                        elif data[0]["react"] == 8:
                            photo = config.sleep
                            if data[0]["lang"] == "ru":
                                e = discord.Embed(title="Реакция: спать", description=f"<@{str(member.id)}> спит с <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} примогемов", icon_url=member.avatar_url)
                            elif data[0]["lang"] == "en":
                                e = discord.Embed(title="Реакция: спать", description=f"<@{str(member.id)}> спит с <@{str(member2.id)}>", color=discord.Color(0x2F3136))
                                e.set_footer(text=f"{member.display_name} • {config.reaction_two} примогемов", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_image(url=random.choice(photo))
                            await message.clear_reactions()
                            await message.edit(embed=e)
                            coll.delete_one({"message_id": data[0]["message_id"]})
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        if data[0]["lang"] == "ru":
                            e = discord.Embed(title="Реакция: отказ", description=f"<@{str(member2.id)}> тебе отказал(-а) :(", color=discord.Color(0x2F3136))
                        elif data[0]["lang"] == "en":
                            e = discord.Embed(title="Reaction: rejection", description=f"<@{str(member2.id)}> turned you down :(", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
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
                        await message.clear_reactions()
                        await message.edit(embed=e)
                        coll.delete_one({"message_id": data[0]["message_id"]})
            elif data[0]["type"] == "invite_clan":
                if user.id == int(data[0]["invited"]):
                    await message.clear_reactions()
                    users = db.prof_ec_users
                    clans = db.clans
                    member = message.guild.get_member(int(data[0]["inviter"]))
                    member2 = message.guild.get_member(int(data[0]["invited"]))
                    userdb = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                    if not userdb["clan"]:
                        e = discord.Embed(title=f"", description=f"Пользотель, приглашающий в группировку не находится в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    userdb2 = users.find_one({ "disid": f"{member2.id}", "guild": f"{member2.guild.id}" })
                    if userdb2["clan"]:
                        e = discord.Embed(title=f"", description=f"Пользователь, которого вы собирались пригласить в группировку уже находится в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member2.display_name}", icon_url=member2.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        users.update_one({ "disid": str(member2.id), "guild": str(member2.guild.id)}, { "$set": { "clan": data[0]["clan"] } })
                        clans.update_one({ "id": int(data[0]["clan"]) }, { "$push": { "members": str(member2.id) } })
                        clan_info = clans.find_one({ "id": int(data[0]["clan"]) })
                        perks = clan_info["perks"]
                        if perks["role"]["id"] != "":
                            clan_role = message.guild.get_role(int(perks["role"]["id"]))
                            await member2.add_roles(clan_role)
                        e = discord.Embed(title="Приглашение в группировку", description=f"<@{str(member2.id)}> вступил в группировку.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        e = discord.Embed(title="Приглашение в группировку", description=f"<@{str(member2.id)}> отказался от вступления в группировку.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })

            elif data[0]["type"] == "create_clan":
                if user.id == int(data[0]["owner_clan"]):
                    await message.clear_reactions()
                    users = db.prof_ec_users
                    clans = db.clans
                    member = message.guild.get_member(int(data[0]["owner_clan"]))
                    userdb = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                    if userdb["clan"]:
                        e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    if str(emoji) == "✅":
                        if userdb["money"] < config.clancostup: 
                            e = discord.Embed(title=f"", description=f"Недостаточно примогемов.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                            return await message.edit(embed=e)
                        await message.clear_reactions()
                        idnew = clans.find({}).sort("id", -1)[0]["id"] + 1
                        users.update_one({ "disid": str(member.id), "guild": f"{member.guild.id}"}, { "$set": { "clan": f"{idnew}" } })
                        users.update_one({ "disid": str(member.id), "guild": f"{member.guild.id}"}, { "$inc": { "money": -(config.clancostup) } })
                        clans.insert_one({ 'id': idnew, 'title': f'{data[0]["name_clan"]}', 'description': '', 'exp': 0, 'nexp': 100000, 'lvl': 1, 'nlvl': 25000, 'balance': 0, 'color': '', 'image': '', 'time': int(time.time()), 'owner': f"{member.id}", "coowner": "", 'members': [f'{member.id}'], 'limitmembers': 15, 'officers': [], "perks": { "interface": { "access": 0, "cooldown_image": 0, "cooldown_color": 0 }, "role": { "access": 0, "buy": 0, "id": "", "cooldown": 0 }, "room": { "access": 0, "buy": 0, "id": "" }, "chat": { "access": 0, "buy": 0, "id": "", "captcha": { "status": 1, "text": "", "time": 0, "life_time": 120, "gift": 2500, "used": 0, "expire": 0, "message_id": "", "count": 0, "members": [] } }, "boost24h": { "access": 0, "buy": 0, "time": 0 }, "spots": { "access": 0, "spots": 0 } }, "booster": 1, "war_status": 0, "temp_chat": "" })
                        e = discord.Embed(title="Создание группировки", description=f"Была создана группировка {data[0]['name_clan']}.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        e = discord.Embed(title="Создание группировки", description=f"Создание отменено.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })

            elif data[0]["type"] == "transfer_clan":
                if user.id == int(data[0]["author"]):
                    await message.clear_reactions()
                    users = db.prof_ec_users
                    clans = db.clans
                    member = message.guild.get_member(int(data[0]["author"]))
                    member2 = message.guild.get_member(int(data[0]["transfer"]))
                    userdb = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                    if not userdb["clan"]:
                        e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    userdb2 = users.find_one({ "disid": f"{member2.id}", "guild": f"{member2.guild.id}" })
                    if not userdb2["clan"]:
                        e = discord.Embed(title=f"", description=f"Пользователь, которому вы собирались передать права уже не находится в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                        officers = [message.guild.get_member(int(x)) for x in clan_info["officers"]]
                        if member2 in officers:
                            clans.update_one({ "id": int(data[0]["clan"]) }, { "$pull": { "officers": str(member2.id) } })
                        clans.update_one({ "id": int(data[0]["clan"]) }, { "$set": { "owner": str(member2.id) } })
                        e = discord.Embed(title="Передача прав группировки", description=f"Успех! Права владельца группировки **\"{data[0]['title']}\"** были переданы <@!{member2.id}>.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        e = discord.Embed(title="Передача прав группировки", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })

            elif data[0]["type"] == "delete_clan":
                if user.id == int(data[0]["author"]):
                    await message.clear_reactions()
                    users = db.prof_ec_users
                    clans = db.clans
                    member = message.guild.get_member(int(data[0]["author"]))
                    userdb = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                    if not userdb["clan"]:
                        e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                        perks = clan_info["perks"]
                        if perks["role"]["id"] != "":
                            loadingem = client.get_emoji(794502101853798400)
                            e = discord.Embed(title="Удаление группировки", description=f"{loadingem} Обработка...", color=discord.Color(0x2F3136))
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            await message.edit(embed=e)
                            clan_role = message.guild.get_role(int(perks["role"]["id"]))
                            await clan_role.delete()
                        users.update_many({ "clan": str(data[0]["clan"]) }, { "$set": { "clan": "" } })
                        clans.delete_one({ "id": int(data[0]["clan"]) })
                        e = discord.Embed(title="Удаление группировки", description=f"Успех! Группировка **\"{clan_info['title']}\"** была удалена.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        e = discord.Embed(title="Удаление группировки", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
            
            elif data[0]["type"] == "leave_clan":
                if user.id == int(data[0]["author"]):
                    await message.clear_reactions()
                    users = db.prof_ec_users
                    clans = db.clans
                    member = message.guild.get_member(int(data[0]["author"]))
                    userdb = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                    if not userdb["clan"]:
                        e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                        officers = [message.guild.get_member(int(x)) for x in clan_info["officers"]]
                        if member in officers:
                            clans.update_one({ "id": int(data[0]["clan"]) }, { "$pull": { "officers": str(member.id) } })
                        clans.update_one({ "id": int(data[0]["clan"]) }, { "$pull": { "members": str(member.id) } })
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$set": { "clan": "", "depositInClan": 0 } } )
                        perks = clan_info["perks"]
                        if perks["role"]["id"] != "":
                            clan_role = message.guild.get_role(int(perks["role"]["id"]))
                            await member.remove_roles(clan_role)
                        e = discord.Embed(title="Выход из группировки", description=f"Вы успешно покинули группировку.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        e = discord.Embed(title="Выход из группировки", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })

            elif data[0]["type"] == "rename_clan":
                if user.id == int(data[0]["author"]):
                    await message.clear_reactions()
                    users = db.prof_ec_users
                    clans = db.clans
                    member = message.guild.get_member(int(data[0]["author"]))
                    userdb = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                    if not userdb["clan"]:
                        e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    newtitle = data[0]["newtitle"]
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                        perks = clan_info["perks"]
                        if clan_info["balance"] < 100000:
                            e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                            return await message.edit(embed=e)
                        
                        if perks["role"]["id"] != "":
                            loadingem = client.get_emoji(794502101853798400)
                            e = discord.Embed(title="Изменение названия группировки", description=f"{loadingem} Обработка...", color=discord.Color(0x2F3136))
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            await message.edit(embed=e)
                            namerole = (38 - len(newtitle)) // 3
                            clan_role = message.guild.get_role(int(perks["role"]["id"]))
                            await clan_role.edit(name=f"{'⠀'*namerole}{newtitle}{'⠀'*namerole}")
                        clans.update_one({ "id": int(data[0]["clan"]) }, { "$set": { "title": newtitle } })
                        clans.update_one({ "id": int(data[0]["clan"]) }, { "$inc": { "balance": -100000 } })
                        e = discord.Embed(title="Изменение названия группировки", description=f"Успех! Название изменено на **\"{newtitle}\"**.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        e = discord.Embed(title="Изменение названия группировки", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })

            elif data[0]["type"] == "spots_clan":
                if user.id == int(data[0]["author"]):
                    await message.clear_reactions()
                    users = db.prof_ec_users
                    clans = db.clans
                    member = message.guild.get_member(int(data[0]["author"]))
                    userdb = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                    if not userdb["clan"]:
                        e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    spots = data[0]["spots"]
                    cost = data[0]["cost"]
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                        perks = clan_info["perks"]
                        if clan_info["balance"] < cost:
                            e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_author(name="Покупка дополнительных мест")
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                            return await message.edit(embed=e)
                        
                        perks["spots"]["spots"] += spots
                        clans.update_one({ "id": int(data[0]["clan"]) }, { "$inc": { "balance": -cost, "limitmembers": spots } })
                        clans.update_one({ "id": int(data[0]["clan"]) }, { "$set": { "perks": perks } })
                        e = discord.Embed(title="", description=f"Успех! {'Добавлен' if spots == 1 else 'Добавлено'} {spots} {funcb.declension([ 'слот', 'слота', 'слотов' ], spots)}.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.set_author(name="Покупка дополнительных мест")
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        e = discord.Embed(title="", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        e.set_author(name="Покупка дополнительных мест")
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        coll.delete_one({ "message_id": data[0]["message_id"] })

            elif data[0]["type"] == "war_clan":
                clans = db.clans
                clan_id_opponent = data[0]["clan_id_opponent"]
                clan_id = data[0]["clan_id"]
                costwar = data[0]["costwar"]
                atclan = clans.find_one({ "war.id": int(clan_id) })
                opponent = clans.find_one({ "war.id": int(clan_id_opponent) })
                if user.id == int(atclan["owner"]):
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        if int(costwar) > int(atclan["balance"]):
                            e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_author(name="Война группировок")
                            e.set_footer(text=f"{user.display_name}", icon_url=user.avatar_url)
                            clans.update_one({ "id": clan_id }, { "$set": { "war_status": 0 } })
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                            await message.edit(embed=e)
                        elif int(costwar) > int(opponent["balance"]):
                            e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки противника.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_author(name="Война группировок")
                            e.set_footer(text=f"{user.display_name}", icon_url=user.avatar_url)
                            clans.update_one({ "id": clan_id }, { "$set": { "war_status": 0 } })
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                            await message.edit(embed=e)
                        else:
                            e = discord.Embed(title="Война группировок", description=f"Ожидание ответа противника.", color=discord.Color(0x2F3136))
                            e.set_footer(text=f"{user.display_name}", icon_url=user.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            await message.edit(embed=e)
                            money_emoji = client.get_emoji(config.MONEY_EMOJI)
                            clans.update_one({ "id": opponent["id"] }, { "$set": { "war_status": 2 } })
                            reactions = db.reactions
                            e = discord.Embed(title=f"", description=f"Вам объявили войну \"**{atclan['title']}**\" на {costwar}{money_emoji}, что ответите?", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_author(name=f"Война группировок")
                            e.set_footer(text=f"{user.display_name}", icon_url=user.avatar_url)
                            channel = message.guild.get_channel(int(data[0]["channels_id"][1]))
                            message_s = await channel.send(content=f"<@!{opponent['owner']}> <@&{opponent['perks']['role']['id']}>", embed=e)
                            await message_s.add_reaction("✅")
                            await message_s.add_reaction("❌")
                            reactions.insert_one({"message_id": str(message_s.id), "message_id2": str(message.id), "member": str(atclan['owner']), "member2": str(opponent['owner']), "costwar": costwar, "clan_id": clan_id, "clan_id_opponent": clan_id_opponent, "time": int(time.time()) + 300, "guild_id": str(message.guild.id), "channels_id": data[0]["channels_id"], "type": "war_clan_opponent" })
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        e = discord.Embed(title="Война группировок", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{user.display_name}", icon_url=user.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(embed=e)
                        clans.update_one({ "id": clan_id }, { "$set": { "war_status": 0 } })
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        try:
                            temp1 = client.get_channel(atclan["temp_chat"])
                            if temp1:
                                await temp1.delete()
                            clans.update_one({ "id": atclan["id"] }, { "$set": { "temp_chat": "" } })
                        except:
                            pass
                        try:
                            temp2 = client.get_channel(opponent["temp_chat"])
                            if temp1:
                                await temp2.delete()
                            clans.update_one({ "id": opponent["id"] }, { "$set": { "temp_chat": "" } })
                        except:
                            pass

            elif data[0]["type"] == "war_clan_opponent":
                clans = db.clans
                clan_id_opponent = data[0]["clan_id_opponent"]
                clan_id = data[0]["clan_id"]
                costwar = data[0]["costwar"]
                atclan = clans.find_one({ "war.id": int(clan_id) })
                opponent = clans.find_one({ "war.id": int(clan_id_opponent) })
                try:
                    channelt = int(atclan["perks"]["chat"]["id"])
                except:
                    channelt = int(atclan["temp_chat"])
                message2 = await message.guild.get_channel(channelt).fetch_message(int(data[0]["message_id2"]))
                if user.id == int(opponent["owner"]):
                    if str(emoji) == "✅":
                        await message.clear_reactions()
                        if int(costwar) > int(opponent["balance"]):
                            e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_author(name="Война группировок")
                            e.set_footer(text=f"{user.display_name}", icon_url=user.avatar_url)
                            clans.update_one({ "id": clan_id }, { "$set": { "war_status": 0 } })
                            clans.update_one({ "id": clan_id_opponent }, { "$set": { "war_status": 0 } })
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                            await message.edit(content="", embed=e)
                        elif int(costwar) > int(atclan["balance"]):
                            e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки противника.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_author(name="Война группировок")
                            e.set_footer(text=f"{user.display_name}", icon_url=user.avatar_url)
                            clans.update_one({ "id": clan_id }, { "$set": { "war_status": 0 } })
                            clans.update_one({ "id": clan_id_opponent }, { "$set": { "war_status": 0 } })
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                            await message.edit(content="", embed=e)
                        else:
                            war1 = atclan["war"]
                            war2 = opponent["war"]
                            war1["game"] = {
                                "bet": int(costwar),
                                "captcha": {
                                    "posted": 0,
                                    "time": 0,
                                    "life_time": 480,
                                    "count_captcha": 6,
                                    "message_id": "",
                                    "used": 0,
                                    "text": ""
                                },
                                "turn": "attack",
                                "opponent": clan_id_opponent,
                                "datetime": int(time.time()),
                                "members": [],
                                "result": "none",
                                "captches": 0
                            }
                            war2["game"] = {
                                "bet": int(costwar),
                                "captcha": {
                                    "posted": 0,
                                    "time": 0,
                                    "life_time": 480,
                                    "count_captcha": 6,
                                    "message_id": "",
                                    "used": 0,
                                    "text": ""
                                },
                                "turn": "defense",
                                "opponent": clan_id,
                                "datetime": int(time.time()),
                                "members": [],
                                "result": "none",
                                "captches": 0
                            }
                            #captcha1 = atclan["perks"]
                            #captcha1["chat"]["captcha"]["status"] = 0
                            #captcha2 = opponent["perks"]
                            #captcha2["chat"]["captcha"]["status"] = 0
                            
                            clans.update_one({ "id": clan_id }, { "$set": { "war_status": 1, "war": war1} }) #, "perks": captcha1 } })
                            clans.update_one({ "id": clan_id_opponent }, { "$set": { "war_status": 1, "war": war2} }) #, "perks": captcha2 } })
                            clans.update_one({ "id": clan_id }, { "$inc": { "balance": -costwar } })
                            clans.update_one({ "id": clan_id_opponent }, { "$inc": { "balance": -costwar } })
                            e = discord.Embed(title="Война группировок", description=f"Да начнётся война!", color=discord.Color(0x2F3136))
                            e.set_footer(text=f"{user.display_name}", icon_url=user.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            await message.edit(content="", embed=e)
                            await message2.edit(embed=e)
                            await message2.channel.send(f"<@&{atclan['perks']['role']['id']}>", delete_after=2.0)
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif str(emoji) == "❌":
                        await message.clear_reactions()
                        e = discord.Embed(title="Война группировок", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{user.display_name}", icon_url=user.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        await message.edit(content="", embed=e)
                        await message2.edit(embed=e)
                        clans.update_one({ "id": clan_id }, { "$set": { "war_status": 0 } })
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        try:
                            temp1 = client.get_channel(atclan["temp_chat"])
                            if temp1:
                                await temp1.delete()
                            clans.update_one({ "id": atclan["id"] }, { "$set": { "temp_chat": "" } })
                        except:
                            pass
                        try:
                            temp2 = client.get_channel(opponent["temp_chat"])
                            if temp1:
                                await temp2.delete()
                            clans.update_one({ "id": opponent["id"] }, { "$set": { "temp_chat": "" } })
                        except:
                            pass

            elif data[0]["type"] == "shop_clan":
                if user.id == int(data[0]["author"]):
                    await message.clear_reactions()
                    users = db.prof_ec_users
                    clans = db.clans
                    member = message.guild.get_member(int(data[0]["author"]))
                    userdb = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                    if not userdb["clan"]:
                        e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        coll.delete_one({ "message_id": data[0]["message_id"] })
                        return await message.edit(embed=e)
                    if data[0]["item"] == "role":
                        if str(emoji) == "✅":
                            await message.clear_reactions()
                            clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                            title = clan_info["title"]
                            if clan_info["balance"] < 500000:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            perks = clan_info["perks"]
                            if perks["role"]["access"] == 0:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, доступ запрещен.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            elif perks["role"]["buy"] == 1:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, роль группировки уже куплена.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            else:
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                loadingem = client.get_emoji(794502101853798400)
                                e = discord.Embed(title="", description=f"{loadingem} Обработка...", color=discord.Color(0x2F3136))
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                e.timestamp = datetime.datetime.utcnow()
                                await message.edit(embed=e)
                                namerole = (38 - len(title)) // 3
                                clan_role = await message.guild.create_role(name=f"{'⠀'*namerole}{title}{'⠀'*namerole}")
                                drole = int(message.guild.get_role(838723403706793998).position) + 1
                                while clan_role.position != drole:
                                    await clan_role.edit(position=drole)
                                for x in clan_info["members"]:
                                    user = message.guild.get_member(int(x))
                                    if user:
                                        while clan_role not in user.roles:
                                            await user.add_roles(clan_role)
                                perks["role"]["buy"] = 1
                                perks["role"]["id"] = f"{clan_role.id}"
                                clans.update_one({ "id": clan_info["id"] }, { "$set": { "perks": perks } })
                                clans.update_one({ "id": clan_info["id"] }, { "$inc": { "balance": -500000 } })
                                e = discord.Embed(title="", description=f"Успех! Куплена роль группировки, чтобы воспользоваться: `.g role [цвет]`.", color=discord.Color(0x2F3136))
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                e.timestamp = datetime.datetime.utcnow()
                                await message.edit(embed=e)
                        elif str(emoji) == "❌":
                            await message.clear_reactions()
                            clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                            title = clan_info["title"]
                            e = discord.Embed(title="", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                            e.set_author(name=f"Магазин группировки {title}")
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            await message.edit(embed=e)
                            coll.delete_one({ "message_id": data[0]["message_id"] })

                    elif data[0]["item"] == "voice_room":
                        if str(emoji) == "✅":
                            await message.clear_reactions()
                            clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                            title = clan_info["title"]
                            if clan_info["balance"] < 500000:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            perks = clan_info["perks"]
                            if perks["role"]["buy"] == 0:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, доступ запрещен.\nДля покупки нужно купить роль группировки.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e) 
                            elif perks["room"]["access"] == 0:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, доступ запрещен.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            elif perks["room"]["buy"] == 1:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, войс канал группировки уже куплен.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            else:
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                loadingem = client.get_emoji(794502101853798400)
                                e = discord.Embed(title="", description=f"{loadingem} Обработка...", color=discord.Color(0x2F3136))
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                e.timestamp = datetime.datetime.utcnow()
                                await message.edit(embed=e)
                                role = message.guild.get_role(int(perks["role"]["id"]))
                                categoryclans = client.get_channel(841440615770095616)
                                room = await message.guild.create_voice_channel(name=title, category=categoryclans)
                                await room.set_permissions(role, connect=True,
                                                                 view_channel=True,
                                                                 stream=True,
                                                                 use_voice_activation=True)
                                perks["room"]["buy"] = 1
                                perks["room"]["id"] = f"{room.id}"
                                clans.update_one({ "id": clan_info["id"] }, { "$set": { "perks": perks } })
                                clans.update_one({ "id": clan_info["id"] }, { "$inc": { "balance": -500000 } })
                                e = discord.Embed(title="", description=f"Успех! Куплена и создана войс комната группировки.", color=discord.Color(0x2F3136))
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                e.timestamp = datetime.datetime.utcnow()
                                await message.edit(embed=e)
                        elif str(emoji) == "❌":
                            await message.clear_reactions()
                            clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                            title = clan_info["title"]
                            e = discord.Embed(title="", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                            e.set_author(name=f"Магазин группировки {title}")
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            await message.edit(embed=e)
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif data[0]["item"] == "boost24h":
                        if str(emoji) == "✅":
                            await message.clear_reactions()
                            clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                            title = clan_info["title"]
                            members = clan_info["members"]
                            if clan_info["balance"] < 250000:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            perks = clan_info["perks"]
                            if perks["boost24h"]["access"] == 0:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, доступ запрещен.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            else:
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                loadingem = client.get_emoji(794502101853798400)
                                e = discord.Embed(title="", description=f"{loadingem} Обработка...", color=discord.Color(0x2F3136))
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                e.timestamp = datetime.datetime.utcnow()
                                await message.edit(embed=e)
                                givem = 10000
                                susers = db.prof_ec_users
                                primo = client.get_emoji(config.MONEY_EMOJI)
                                a1 = 0 
                                for x in members:
                                    user = message.guild.get_member(int(x))
                                    if user is None:
                                        continue
                                    if user.status != discord.Status.offline:
                                        a1 += 1
                                        susers.update_one({ "disid": f"{user.id}", "guild": f"{user.guild.id}" }, { "$inc": { "money": givem } })
                                        try:
                                            e = discord.Embed(title="", description=f"Вам было выдано {givem}{primo}", color=discord.Colour(0x2F3136))
                                            e.timestamp = datetime.datetime.utcnow()
                                            e.set_author(name=f"Магазин группировки {title}")
                                            e.set_footer(text=f"{user.guild.name}", icon_url=user.guild.icon_url)
                                            await user.send(embed=e)
                                        except:
                                            pass
                                perks["boost24h"]["time"] = int(time.time()) + 864000
                                clans.update_one({ "id": clan_info["id"] }, { "$set": { "perks": perks } })
                                clans.update_one({ "id": clan_info["id"] }, { "$inc": { "balance": -250000 } })
                                e = discord.Embed(title="", description=f"Успех! Куплены и выданы дополнительные примогемы {a1} {funcb.declension(['участнику', 'участникам', 'участникам'], a1)} группировки в сети.", color=discord.Color(0x2F3136))
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                e.timestamp = datetime.datetime.utcnow()
                                await message.edit(embed=e)
                        elif str(emoji) == "❌":
                            await message.clear_reactions()
                            clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                            title = clan_info["title"]
                            e = discord.Embed(title="", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                            e.set_author(name=f"Магазин группировки {title}")
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            await message.edit(embed=e)
                            coll.delete_one({ "message_id": data[0]["message_id"] })
                    elif data[0]["item"] == "chat":
                        if str(emoji) == "✅":
                            await message.clear_reactions()
                            clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                            title = clan_info["title"]
                            if clan_info["balance"] < 500000:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, недостаточно примогемов на балансе группировки.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            perks = clan_info["perks"]
                            if perks["role"]["buy"] == 0:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, доступ запрещен.\nДля покупки нужно купить роль группировки.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e) 
                            elif perks["chat"]["access"] == 0:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, доступ запрещен.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            elif perks["chat"]["buy"] == 1:
                                e = discord.Embed(title=f"", description=f"Невозможно завершить действие, чат канал с капчей для группировки уже куплен.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                return await message.edit(embed=e)
                            else:
                                coll.delete_one({ "message_id": data[0]["message_id"] })
                                loadingem = client.get_emoji(794502101853798400)
                                e = discord.Embed(title="", description=f"{loadingem} Обработка...", color=discord.Color(0x2F3136))
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                e.timestamp = datetime.datetime.utcnow()
                                await message.edit(embed=e)
                                role = message.guild.get_role(int(perks["role"]["id"]))
                                categoryclans = client.get_channel(841440615770095616)
                                room = await message.guild.create_text_channel(name=title, category=categoryclans)
                                await room.set_permissions(role, send_messages=True,
                                                                 view_channel=True,
                                                                 add_reactions=True,
                                                                 attach_files=True,
                                                                 read_messages=True,
                                                                 external_emojis=True,
                                                                 read_message_history=True)
                                perks["chat"]["buy"] = 1
                                perks["chat"]["id"] = f"{room.id}"
                                perks["chat"]["captcha"]["time"] = int(time.time())
                                clans.update_one({ "id": clan_info["id"] }, { "$set": { "perks": perks } })
                                clans.update_one({ "id": clan_info["id"] }, { "$inc": { "balance": -500000 } })
                                e = discord.Embed(title="", description=f"Успех! Куплен и создан чат канал с капчей для группировки.", color=discord.Color(0x2F3136))
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                                e.timestamp = datetime.datetime.utcnow()
                                await message.edit(embed=e)
                        elif str(emoji) == "❌":
                            await message.clear_reactions()
                            clan_info = clans.find_one({"id": int(data[0]["clan"]) })
                            title = clan_info["title"]
                            e = discord.Embed(title="", description=f"Действие отменено.", color=discord.Color(0x2F3136))
                            e.set_author(name=f"Магазин группировки {title}")
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            await message.edit(embed=e)
                            coll.delete_one({ "message_id": data[0]["message_id"] })
