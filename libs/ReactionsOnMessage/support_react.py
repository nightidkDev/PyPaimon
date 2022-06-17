import datetime
import random
import time
import asyncio
import sys
import pymongo
import numpy
sys.path.append("../../")
from libs import DataBase
import os
import config
uri = config.uri
import sqlite3
#mongoclient = pymongo.MongoClient(uri)
#db = mongoclient.aimi

async def sleeptime(time):
    await asyncio.sleep(int(time))

async def support_react(client, discord, user, message, emoji, config):
    if message.author.id == client.user.id:
        con = sqlite3.connect('support.db', check_same_thread=False)
        cur = con.cursor()
        #support = db.support
        info = cur.execute(f"SELECT * FROM support WHERE message_id='{message.id}'").fetchall()
        if not info:
            return
        data = info[0]
        #print(data)
        #data = support.find_one({"message_id": f"{message.id}" })
        support_role = message.guild.get_role(823234604550062102)
        prime_role = message.guild.get_role(827278746205683802)
        if support_role not in user.roles and prime_role not in user.roles:
            return 
        # message = client.get_guild(604083589570625555).get_channel(int(data[2])).fetch_message(data["message_id"])
        if str(emoji.id) == "824729100572819537":
            # print(data[4])
            if data[4] and data[4] != str(user.id):
                return
            if data[5] == 1:
                if data[3]:
                    voice = message.guild.get_channel(int(data[3]))
                    await voice.delete(reason=f"Вопрос закрыт: {user}.")
                text = message.guild.get_channel(int(data[2]))
                await text.delete(reason=f"Вопрос закрыт: {user}.")
                cur.execute(f"DELETE FROM support WHERE message_id='{message.id}'")
                con.commit()
                con.close()
                #support.delete_one({ "message_id": str(message.id) })
            else:
                cancel = client.get_emoji(824737872035708968)
                qcancel = client.get_emoji(824729100572819537)
                suser = message.guild.get_member(int(data[0]))
                e = discord.Embed(title="", description=f"Привет, {f'<@!{suser.id}>' if suser is not None else '@leaved-user'}. Тут ты можешь задавать вопросы по игре, тебе ответят:\n<@&827278746205683802>\n<@&823234604550062102>\n\nДля помощника: Ты точно хочешь закрыть? Если нет, то поставь {cancel}.\nЕсли же ты хочешь закрыть, то повторно нажми на реакцию.", color=discord.Color(0x2F3136))
                await message.edit(embed=e)
                await message.add_reaction(cancel)
                await message.remove_reaction(qcancel, user)
                cur.execute(f"UPDATE support SET check_close = 1 WHERE message_id='{message.id}'")
                con.commit()
                con.close()
                #support.update_one({ "message_id": str(message.id) }, { "$set": { "check_close": 1 } })
        elif str(emoji.id) == "824737872035708968":
            if data[5] == 1:
                cancel = client.get_emoji(824737872035708968)
                suser = message.guild.get_member(int(data[0]))
                e = discord.Embed(title="", description=f"Привет, {f'<@!{suser.id}>' if suser is not None else '@leaved-user'}. Тут ты можешь задавать вопросы по игре, тебе ответят:\n<@&827278746205683802>\n<@&823234604550062102>", color=discord.Color(0x2F3136))
                await message.edit(embed=e)
                await message.clear_reaction(cancel)
                cur.execute(f"UPDATE support SET check_close = 0 WHERE message_id='{message.id}'")
                con.commit()
                con.close()
                #support.update_one({ "message_id": str(message.id) }, { "$set": { "check_close": 0 } })
        elif str(emoji.id) == "824729799900659753":
            info2 = cur.execute(f"SELECT * FROM support WHERE mod_id='{user.id}'").fetchall()
            if info2:
                return
            check_mark = client.get_emoji(824729799900659753)
            voice_open = client.get_emoji(824729110809935902)
            if data[5] == 1:
                await message.remove_reaction(check_mark, user)
                return
            if not data[4]:
                cur.execute(f"UPDATE support SET mod_id = '{user.id}' WHERE message_id='{message.id}'")
                con.commit()
                con.close()
                #support.update_one({ "message_id": str(message.id) }, { "$set": { "mod_id": f"{user.id}" } })
                e = discord.Embed(title="", description=f"Помощник найден!\nТебе будет отвечать: <@!{user.id}>.", color=discord.Color(0x2F3136))
                await message.channel.send(embed=e)
                await message.clear_reaction(check_mark)
                await message.add_reaction(voice_open)
                await message.channel.set_permissions(user, send_messages=True)
            else:
                return
        elif str(emoji.id) == "824729110809935902":
            voice_open = client.get_emoji(824729110809935902)
            if data[5] == 1:
                await message.remove_reaction(voice_open, user)
                return
            if data[4] == str(user.id) and not data[3]:
                suser = message.guild.get_member(int(data[0]))
                e = discord.Embed(title="", description=f"Войс канал был создан.", color=discord.Color(0x2F3136))
                await message.channel.send(embed=e)
                await message.clear_reaction(voice_open)
                voice = await message.guild.create_voice_channel(f"{suser.name}", category=message.channel.category)
                await voice.set_permissions(user, view_channel=True,
                                                  connect=True,
                                                  speak=True,
                                                  stream=True,
                                                  use_voice_activation=True)
                await voice.set_permissions(suser, view_channel=True,
                                                   connect=True,
                                                   speak=True,
                                                   stream=True,
                                                   use_voice_activation=True)
                cur.execute(f"UPDATE support SET vchannel_id = '{voice.id}' WHERE message_id='{message.id}'")
                con.commit()
                con.close()
                #support.update_one({ "message_id": str(message.id) }, { "$set": { "vchannel_id": f"{voice.id}" } })
            else:
                return
        #elif str(emoji.id) == ""
        #if data[4] == "":

        #else:
