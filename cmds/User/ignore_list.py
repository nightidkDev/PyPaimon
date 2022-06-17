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

users = db.prof_ec_users

def init():
    return [["ignore", ignore, "flood", "all"]]

async def ignore(client, message, command, messageArray, lang_u):
    user = users.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
    if len(messageArray) == 0 or messageArray[0] == "":
        ignore_list = user["ignore_list"]
        ignore_str = "\n".join(f"{i + 1}. <@!{ignore_list[i]}> ({client.get_user(int(ignore_list[i]))})" for i in range(len(ignore_list)))
        if ignore_str == "":
            ignore_str = "Пусто."
        e = discord.Embed(title="Игнор-лист", description="", color=discord.Color(0x2F3136))
        e.description = ignore_str
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        await message.channel.send(embed=e)
    else:
        if messageArray[0] == "add":
            e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
            ignore_list = user["ignore_list"]
            if len(message.mentions) != 0:
                if message.mentions[0].bot:
                    return None
                if message.mentions[0] == message.author:
                    e.description = "Себя в чс? Серьезно?"
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed=e)
                if str(message.mentions[0].id) in ignore_list:
                    e.description = "Данный пользователь уже находится в вашем игнор-листе."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed=e)
                else:
                    users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$push": { "ignore_list": f"{message.mentions[0].id}" } })
                    e.description = "Пользователь был добавлен в ваш игнор-лист."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed=e)
            else:
                user_id = None
                try:
                    user_id = int(messageArray[1])
                except:
                    pass
                if message.guild.get_member(user_id) != None:
                    check = message.guild.get_member(user_id)
                    if check.bot:
                        return None
                    if check == message.author:
                        e.description = "Себя в чс? Серьезно?"
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        return await message.channel.send(embed=e)
                    if str(check.id) in ignore_list:
                        e.description = "Данный пользователь уже находится в вашем игнор-листе."
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        return await message.channel.send(embed=e)
                    else:
                        users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$push": { "ignore_list": f"{check.id}" } })
                        e.description = "Пользователь был добавлен в ваш игнор-лист."
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        return await message.channel.send(embed=e)
                else:
                    e.description = "Укажите пользователя."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed=e)
        elif messageArray[0] == "remove":
            e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
            ignore_list = user["ignore_list"]
            if len(message.mentions) != 0:
                if message.mentions[0].bot:
                    return None
                if message.mentions[0] == message.author:
                    return None
                if str(message.mentions[0].id) not in ignore_list:
                    e.description = "Данный пользователь уже не находится в вашем игнор-листе."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed=e)
                else:
                    users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$pull": { "ignore_list": f"{message.mentions[0].id}" } })
                    e.description = "Пользователь был удален из вашего игнор-листа."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed=e)
            else:
                user_id = None
                try:
                    user_id = int(messageArray[1])
                except:
                    pass
                if message.guild.get_member(user_id) != None:
                    check = message.guild.get_member(user_id)
                    if check.bot:
                        return None
                    if check == message.author:
                        return None
                    if str(check.id) not in ignore_list:
                        e.description = "Данный пользователь уже не находится в вашем игнор-листе."
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        return await message.channel.send(embed=e)
                    else:
                        users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$pull": { "ignore_list": f"{check.id}" } })
                        e.description = "Пользователь был удален из вашего игнор-листа."
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        return await message.channel.send(embed=e)
                else:
                    e.description = "Укажите пользователя."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed=e)
        


            
