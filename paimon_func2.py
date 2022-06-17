import asyncio
import datetime
import json
import os
import random
import re
import time
import io
import psutil
import string
import glob
import numpy
from PIL import Image, ImageDraw, ImageFont

import discord
import discord.ext
from discord import utils
import pymongo
import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

from libs import Builders
from libs import Profile
from libs import DataBase
from libs import ReactionsOnMessage
from plugins import voice_money
from plugins import checkreact
from plugins import funcb

print("Loading...")

intents = discord.Intents().all() 
client = discord.Client(intents=intents)

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}д. {h:02d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{h:02d}:{m:02d}:{s:02d}"

def image_to_byte_array(image:Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

async def check_invite_ban():
    await client.wait_until_ready()
    while True:
        coll = db.invite_ban
        for user in coll.find({}):
            member = client.get_guild(604083589570625555).get_member(int(user["id"]))
            channel = client.get_channel(792455728178135060)
            try:
                if not member.guild_permissions.administrator:
                    e = discord.Embed(title="", description="Попытался устроить рассылку ссылок на другой сервер и был забанен.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_author(name=f"{member.display_name}", icon_url=f"{member.avatar_url}")
                    await channel.send(embed=e)
                    try:
                        await member.ban(reason="AutoMod: ad dm.")
                    except:
                        pass
                    coll.delete_one({ "id": user["id"] })
                else:
                    e = discord.Embed(title="", description="Попытался устроить рассылку ссылок на другой сервер и был забанен.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_author(name=f"{member.display_name}", icon_url=f"{member.avatar_url}")
                    await channel.send(embed=e)
                    coll.delete_one({ "id": user["id"] })
            except:
                coll.delete_one({ "id": user["id"] })
        await asyncio.sleep(60)

async def checkdate():
    await client.wait_until_ready()
    while True:
        date_s1 = db.server.find_one({"server": "604083589570625555"})["date_s"]
        if int(time.time()) - date_s1 >= 604800:
            db.server.update_one({"server": "604083589570625555"}, { "$set": { "date_s": date_s1 + 604800 } })
            db.prof_ec_users.update_many({"guild": "604083589570625555"}, { "$set": { "c_channels": [], "s_chat": 0, "s_voice": 0, "v_channels": [] } })
        await asyncio.sleep(30)

async def check_pay():
    await client.wait_until_ready()
    while True:
        rooms = db.love_rooms
        users = db.prof_ec_users
        x = int(time.time())
        for love in rooms.find({}):
            guild = client.get_guild(604083589570625555)
            if love["ptime"] - x <= 43200 and love["notify"] == "false":
                member = guild.get_member(int(love["owner1"]))
                member2 = guild.get_member(int(love["owner2"]))
                # if member is None or member2 is None:
                #     try:
                #         channel = guild.get_channel(int(love["id"]))
                #         await channel.delete()
                #     except:
                #         pass
                #     rooms.delete_one({ "id": love["id"] })
                #     users.update_many({ "love_room": love["id"] }, { "$set": { "partner": "", "marry_time": 0, "love_room": "", "love_room_created": 0 } })
                #     continue
                if guild.get_channel(int(love["id"])) is None:
                    rooms.delete_one({ "id": love["id"] })
                    users.update_many({ "love_room": love["id"] }, { "$set": { "love_room": "", "love_room_created": 0 } })
                    continue
                primo = client.get_emoji(config.MONEY_EMOJI)
                e = discord.Embed(title="", description=f"Привет! Через 12 часов будет снята плата за любовную комнату в размере 1.250{primo} с каждого из пары.", color=discord.Color(0x2F3136))
                rooms.update_one({ "id": love["id"] }, { "$set": { "payment_time": int(time.time()) + 43200, "notify": "true" } })
                e.set_author(name="Ежемесячная оплата")
                e.set_footer(text=f"{guild.name}", icon_url=guild.icon_url)
                try:
                    await member.send(embed=e)
                except: 
                    pass
                try:
                    await member2.send(embed=e)
                except:
                    pass
            elif love["notify"] == "true":
                if love["payment_time"] - x <= 0:
                    member = guild.get_member(int(love["owner1"]))
                    member2 = guild.get_member(int(love["owner2"]))
                    # if member is None or member2 is None:
                    #     try:
                    #         channel = guild.get_channel(int(love["id"]))
                    #         await channel.delete()
                    #     except:
                    #         pass
                    #     rooms.delete_one({ "id": love["id"] })
                    #     users.update_many({ "love_room": love["id"] }, { "$set": { "partner": "", "marry_time": 0, "love_room": "", "love_room_created": 0 } })
                    #     continue
                    if guild.get_channel(int(love["id"])) is None:
                        rooms.delete_one({ "id": love["id"] })
                        users.update_many({ "love_room": love["id"] }, { "$set": { "love_room": "", "love_room_created": 0 } })
                        continue
                    user1 = users.find_one({ "disid": f"{member.id}", "guild": f"{guild.id}" })
                    user2 = users.find_one({ "disid": f"{member2.id}", "guild": f"{guild.id}" })
                    primo = client.get_emoji(config.MONEY_EMOJI)
                    if user1["money"] < 1250 and user2["money"] < 1250:
                        e = discord.Embed(title="", description=f"У каждого партнера недостаточно примогемов для оплаты любовной комнаты, поэтому ваша комната была удалена.", color=discord.Color(0x2F3136))
                        e.set_author(name="Ежемесячная оплата")
                        e.set_footer(text=f"{guild.name}", icon_url=guild.icon_url)
                        try:
                            await member.send(embed=e)
                        except: 
                            pass
                        try:
                            await member2.send(embed=e)
                        except:
                            pass
                        try:
                            channel = guild.get_channel(int(love["id"]))
                            await channel.delete()
                        except:
                            pass
                        rooms.delete_one({ "id": love["id"] })
                        users.update_many({ "love_room": love["id"] }, { "$set": { "love_room": "", "love_room_created": 0 } })
                    else:
                        if user1["money"] < 1250:
                            if user2["money"] < 2500:
                                e = discord.Embed(title="", description=f"У каждого партнера недостаточно примогемов для оплаты любовной комнаты, поэтому ваша комната была удалена.", color=discord.Color(0x2F3136))
                                e.set_author(name="Ежемесячная оплата")
                                e.set_footer(text=f"{guild.name}", icon_url=guild.icon_url)
                                try:
                                    await member.send(embed=e)
                                except: 
                                    pass
                                try:
                                    await member2.send(embed=e)
                                except:
                                    pass
                                try:
                                    channel = guild.get_channel(int(love["id"]))
                                    await channel.delete()
                                except:
                                    pass
                                rooms.delete_one({ "id": love["id"] })
                                users.update_many({ "love_room": love["id"] }, { "$set": { "love_room": "", "love_room_created": 0 } })
                            else:
                                e = discord.Embed(title="", description=f"Оплата была произведена, следующая оплата через 30 дней.", color=discord.Color(0x2F3136))
                                e.set_author(name="Ежемесячная оплата")
                                e.set_footer(text=f"{guild.name}", icon_url=guild.icon_url)
                                try:
                                    await member.send(embed=e)
                                except: 
                                    pass
                                try:
                                    await member2.send(embed=e)
                                except:
                                    pass
                                rooms.update_one({ "id": love["id"] }, { "$set": { "ptime": love["ptime"] + 2592000, "notify": "false" } })
                                rooms.update_one({ "id": love["id"] }, { "$unset": { "payment_time": "" } })
                                users.update_many({ "disid": f"{member2.id}", "guild": f"{guild.id}" }, { "$inc": { "money": -2500 } })
                        elif user2["money"] < 1250:
                            if user1["money"] < 2500:
                                e = discord.Embed(title="", description=f"У каждого партнера недостаточно примогемов для оплаты любовной комнаты, поэтому ваша комната была удалена.", color=discord.Color(0x2F3136))
                                e.set_author(name="Ежемесячная оплата")
                                e.set_footer(text=f"{guild.name}", icon_url=guild.icon_url)
                                try:
                                    await member.send(embed=e)
                                except: 
                                    pass
                                try:
                                    await member2.send(embed=e)
                                except:
                                    pass
                                try:
                                    channel = guild.get_channel(int(love["id"]))
                                    await channel.delete()
                                except:
                                    pass
                                rooms.delete_one({ "id": love["id"] })
                                users.update_many({ "love_room": love["id"] }, { "$set": { "love_room": "", "love_room_created": 0 } })
                            else:
                                e = discord.Embed(title="", description=f"Оплата была произведена, следующая оплата через 30 дней.", color=discord.Color(0x2F3136))
                                e.set_author(name="Ежемесячная оплата")
                                e.set_footer(text=f"{guild.name}", icon_url=guild.icon_url)
                                try:
                                    await member.send(embed=e)
                                except: 
                                    pass
                                try:
                                    await member2.send(embed=e)
                                except:
                                    pass
                                rooms.update_one({ "id": love["id"] }, { "$set": { "ptime": love["ptime"] + 2592000, "notify": "false" } })
                                rooms.update_one({ "id": love["id"] }, { "$unset": { "payment_time": "" } })
                                users.update_many({ "disid": f"{member.id}", "guild": f"{guild.id}" }, { "$inc": { "money": -2500 } })
                        else:
                            e = discord.Embed(title="", description=f"Оплата была произведена, следующая оплата через 30 дней.", color=discord.Color(0x2F3136))
                            e.set_author(name="Ежемесячная оплата")
                            e.set_footer(text=f"{guild.name}", icon_url=guild.icon_url)
                            try:
                                await member.send(embed=e)
                            except: 
                                pass
                            try:
                                await member2.send(embed=e)
                            except:
                                pass
                            rooms.update_one({ "id": love["id"] }, { "$set": { "ptime": love["ptime"] + 2592000, "notify": "false" } })
                            rooms.update_one({ "id": love["id"] }, { "$unset": { "payment_time": "" } })
                            users.update_many({ "disid": f"{member.id}", "guild": f"{guild.id}" }, { "$inc": { "money": -1250 } })
                            users.update_many({ "disid": f"{member2.id}", "guild": f"{guild.id}" }, { "$inc": { "money": -1250 } })




                    
        await asyncio.sleep(10)

async def checkmute():
    await client.wait_until_ready()
    while True:
        coll = db.mutes
        for value in coll.find():
            guild = client.get_guild(int(value['guild']))
            if not guild:
                coll.delete_one({ "disid": value["disid"], "guild": f"{guild.id}"})
                continue
            x = int(time.time())
            if x >= int(value["time_mute"]):
                member = guild.get_member(int(value["disid"]))
                if not member:
                    continue
                role = guild.get_role(int(value["roleid"]))
                if not role:
                    continue
                await member.remove_roles(role)
                coll.delete_one({ "disid": value["disid"], "guild": f"{guild.id}"})
        await asyncio.sleep(10)

async def fvoice_money():
    await client.wait_until_ready()
    guild = client.get_guild(604083589570625555)
    while not guild:
        guild = client.get_guild(604083589570625555)
        await asyncio.sleep(1)
    else:
        while True:
            await voice_money.voice_money(client)
            await asyncio.sleep(1)

@client.event
async def on_ready():
    print(f"[{datetime.datetime.utcfromtimestamp(int(time.time()) + 10800).strftime('%H:%M:%S')}] Запустилась второстепенная (функции 2) Paimon.exe <3")

client.loop.create_task(checkmute())
client.loop.create_task(fvoice_money())
client.loop.create_task(check_invite_ban())
client.loop.create_task(checkdate())
client.loop.create_task(check_pay())
token = config.TOKEN
client.run(str(token))