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

def init():
    return [
                  ["marry", love().marry, "flood", "all", "help", "предложить брак"],
                  ["marryinfo|minfo", love().minfo, "flood", "all"],
                  ["divorce", love().divorce, "flood", "all", "help", "развод"],
                  ["love_room|lv", love().love_room, "flood", "all"]
                   ]

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}дн. {h:02d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"    

class love:

    def __init__(self):
        pass

    async def minfo(self, client, message, command, messageArray, lang_u):
        #if str(message.author.id) not in config.ADMINS:
        #        return message.channel.send("Access denied. This part of the command is incomplete.")
        coll = db.prof_ec_users
        rooms = db.love_rooms
        user = coll.find_one({"disid": str(message.author.id), "guild": f"{message.guild.id}" })
        marry_time = int(time.time())-user["marry_time"]
        if user["partner"] != "":
            e = discord.Embed(title="Брачные узы: информация", description=f"", color=discord.Color(0x2F3136))
            partner = message.guild.get_member(int(user['partner']))
            if partner is None:
                partner = "«Не найдено»"
            else:
                partner = str(partner)
            e.add_field(name="```Партнёр```", value=f"```diff\n- {partner}\n```", inline=True)
            e.add_field(name="```Дата свадьбы```", value=f"```fix\n{datetime.datetime.utcfromtimestamp(user['marry_time'] + 10800).strftime('%d.%m.%Y %H:%M:%S')}\n```", inline=True)
            e.add_field(name="```Длительность```", value=f"```glsl\n{seconds_to_hh_mm_ss(marry_time)}\n```", inline=True)
            if user["love_room"]:
                room = rooms.find_one({ "id": user["love_room"] })
                love_room = message.guild.get_channel(int(room["id"]))
                e.add_field(name="```Любовная комната```", value=f"```glsl\n{love_room}\n```", inline=True)
                e.add_field(name="```Дата оплаты```", value=f"```fix\n{datetime.datetime.utcfromtimestamp(room['ptime'] + 10800).strftime('%d.%m.%Y %H:%M:%S')}\n```", inline=True)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        else:
            e = discord.Embed(title="", description=f"Ты не состоишь в брачных узах.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)

    async def marry(self, client, message, command, messageArray, lang_u):
        #if str(message.author.id) not in config.ADMINS:
        #        return message.channel.send("Access denied. This part of the command is incomplete.")
        coll = db.prof_ec_users
        money_emoji = client.get_emoji(config.MONEY_EMOJI)
        user = coll.find({"disid": str(message.author.id), "guild": f"{message.guild.id}" })[0]
        if user["partner"] != "":
            if len(messageArray) == 0:
                e = discord.Embed(title="Брачные узы: Ошибка", description=f"Ты разве уже не имеешь партнёра?", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            else:
                e = discord.Embed(title="Брачные узы: Ошибка", description=f"Ты разве уже не имеешь партнёра?", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
        else:
            if len(messageArray) == 0 or len(message.mentions) == 0:
                e = discord.Embed(title="Брачные узы: Ошибка", description=f"Укажи пользователя.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            elif message.mentions[0].id == message.author.id:
                e = discord.Embed(title="Брачные узы: Ошибка", description=f"Попробуй указать не себя :)", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            elif message.mentions[0].bot:
                e = discord.Embed(title="Брачные узы: Ошибка", description=f"Не трожь ботов!", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            else:
                muser = coll.find({"disid": str(message.mentions[0].id), "guild": f"{message.guild.id}"})[0]
                if muser["partner"] != "":
                    e = discord.Embed(title="Брачные узы: Ошибка", description=f"Данный пользователь имеет партнёра!", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                else:
                    coll = db.prof_ec_users
                    data = coll.find_one({"disid": str(message.author.id), "guild": str(message.guild.id)})
                    if data["money"] < config.marry:
                        if lang_u == "ru":
                            e = discord.Embed(title="", description=f"Недостаточно примогемов. Цена: {config.marry}{money_emoji}", color=discord.Color(0x2F3136))
                        else:
                            e = discord.Embed(title="", description=f"Not enough stars. Price: {config.marry}{money_emoji}", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        return await message.channel.send(embed = e)
                    else:
                        if db.reactions.count_documents({"author": str(message.author.id), "guild_id": str(message.guild.id), "type": "marry"}) != 0:
                            e = discord.Embed(title="Брачные узы: Ошибка", description=f"Вы уже отправили запрос на свадьбу!", color=discord.Color(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                            return await message.channel.send(embed = e)
                        elif db.reactions.count_documents({"for_id": str(message.mentions[0].id), "guild_id": str(message.guild.id), "type": "marry"}) != 0:
                            e = discord.Embed(title="Брачные узы: Ошибка", description=f"Данному пользователю уже отправили запрос на свадьбу!", color=discord.Color(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                            return await message.channel.send(embed = e)

                        e = discord.Embed(title="Брачные узы", description=f"<@!{message.mentions[0].id}>, тебе <@!{message.author.id}> предложил(а) стать парой. Что ответишь?", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        message_s = await message.channel.send(embed = e)
                        await message_s.add_reaction("✅")
                        await message_s.add_reaction("❌")
                        coll = db.reactions
                        coll.insert_one({"message_id": str(message_s.id), "author": str(message.author.id), "for_id": str(message.mentions[0].id), "time": int(time.time()) + 120, "guild_id": str(message.guild.id), "channel_id": str(message.channel.id), "lang": str(lang_u), "type": "marry"})
            
    
    async def divorce(self, client, message, command, messageArray, lang_u):
        #if str(message.author.id) not in config.ADMINS:
        #        return message.channel.send("Access denied. This part of the command is incomplete.")
        coll = db.prof_ec_users
        user = coll.find({"disid": str(message.author.id), "guild": f"{message.guild.id}" })[0]
        if user["partner"] == "":
            e = discord.Embed(title="Развод: Ошибка", description=f"У тебя и так нет партнёра.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        else:
            marry_role = message.guild.get_role(772569219555917834)
            e = discord.Embed(title="Развод", description=f"<@!{message.author.id}> и <@!{user['partner']}> развелись.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            user1 = message.guild.get_member(int(user["partner"]))
            await message.channel.send(embed=e)
            if user["love_room"]:
                rooms = db.love_rooms
                rooms.delete_one({"id": user["love_room"]})
                try:
                    await message.guild.get_channel(int(user["love_room"])).delete()
                except:
                    pass
            try:
                await message.author.remove_roles(marry_role)
            except:
                pass
            try:
                await user1.remove_roles(marry_role)
            except:
                pass
            
            coll.update_one({"disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { 'partner': "", 'love_room': "", 'marry_time': 0, 'love_room_created': 0 } })
            coll.update_one({"disid": user["partner"], "guild": f"{message.guild.id}" }, { "$set": { 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0 } })

    async def love_room(self, client, message, command, messageArray, lang_u):
        users = db.prof_ec_users
        user = users.find_one({"disid": str(message.author.id), "guild": f"{message.guild.id}" })
        if user["money"] < 10000:
            primo = client.get_emoji(config.MONEY_EMOJI)
            e = discord.Embed(title="", description=f"Стоимость создания/восстановления любовной комнаты: 10.000{primo}", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        elif user["partner"] == "":
            e = discord.Embed(title="", description=f"У тебя нет партнёра для создания/восстановлени любовной комнаты.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        elif user["love_room"] != "":
            e = discord.Embed(title="", description=f"У тебя и так есть любовная комната.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        else:
            love_room_category = message.guild.get_channel(876594464502743110)
            member = message.author
            member2 = message.guild.get_member(int(user["partner"]))
            voice = await message.guild.create_voice_channel(f"{member.name} 💞 {member2.name}", category=love_room_category, user_limit=2)
            await voice.set_permissions(member2, manage_channels=True,
                                                 connect=True,
                                                 speak=True,
                                                 view_channel=True)
            await voice.set_permissions(member, manage_channels=True,
                                                connect=True,
                                                speak=True,
                                                view_channel=True)
            tx = int(time.time())
            users.update_one({"disid": str(member.id), "guild": f"{message.guild.id}" }, { "$set": { "love_room": str(voice.id), 'love_room_created': tx, "money": user["money"] - config.marry } })
            users.update_one({"disid": str(member2.id), "guild": f"{message.guild.id}" }, { "$set": { "love_room": str(voice.id), 'love_room_created': tx } })
            rooms = db.love_rooms
            rooms.insert_one({ "id": f"{voice.id}", "owner1": f"{member.id}", "owner2": f"{member2.id}", "ctime": int(time.time()), "ptime": int(time.time()) + 2592000, "notify": "false", "payment": "false" })
            e = discord.Embed(title="", description="Любовная комната была куплена и создана.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)