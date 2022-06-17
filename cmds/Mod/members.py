import datetime
import os
import discord
import time
import re

def init():
    return [["members", members, "all", "admins"]]

async def members(client, message, command, messageArray, lang_u):
    if len(messageArray) >= 1:
        if messageArray[0] != None and len(message.role_mentions) >= 1:
            count1 = 0
            io = 1
            specsch = 0
            pps = 0
            if lang_u == "ru":
                msg = "С ролью " + str(message.role_mentions[0].name) + " %s человек"
            elif lang_u == "en":
                msg = "With the role "+ str(message.role_mentions[0].name) + " %s person"
            listmsg = ""
            for member in message.guild.members:
                for role in member.roles:
                    if role.id == message.role_mentions[0].id:
                        count1 += 1
            title = msg % count1
            for member in message.guild.members:
                for role in member.roles:
                    if role.id == message.role_mentions[0].id:
                        listmsg += str(io) + ". <@!" + str(member.id) + ">\n"
                        io += 1
                        specsch += 1
                        if specsch == 50:
                            pps += 1
                            e = discord.Embed(color=discord.Color(0x2F3136))
                            if pps == 1:
                                e.title = title
                            e.description = listmsg
                            if lang_u == "ru":
                                e.set_footer(text="Запросил: " + message.author.display_name, icon_url=message.author.avatar_url)
                            elif lang_u == "en":
                                e.set_footer(text="Asked: " + message.author.display_name, icon_url=message.author.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            await message.channel.send(embed=e)
                            specsch = 0
                            listmsg = ""
            if count1 - io < 50 and pps >= 2:
                e = discord.Embed(color=discord.Color(0x2F3136))
                e.description = listmsg
                if lang_u == "ru":
                    e.set_footer(text="Запросил: " + message.author.display_name, icon_url=message.author.avatar_url)
                elif lang_u == "en":
                    e.set_footer(text="Asked: " + message.author.display_name, icon_url=message.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                await message.channel.send(embed=e)
            if count1 <= 50:
                e = discord.Embed(color=discord.Color(0x2F3136))
                e.title = msg % count1
                e.description = listmsg
                if lang_u == "ru":
                    e.set_footer(text="Запросил: " + message.author.display_name, icon_url=message.author.avatar_url)
                elif lang_u == "en":
                    e.set_footer(text="Asked: " + message.author.display_name, icon_url=message.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                await message.channel.send(embed=e)