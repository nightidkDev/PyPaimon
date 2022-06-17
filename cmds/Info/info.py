import datetime
import pymongo
import os
import discord
import time
import random
import sys
import psutil
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [
            ["info", info, "all", "all"]
            ]

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}d {h:02d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{h:02d}:{m:02d}:{s:02d}"

async def info(client, message, command, messageArray, lang_u):
    server_coll = db.server
    if server_coll.count_documents({"server": f"{message.guild.id}"}) == 0:
            server_coll.insert_one({"server": str(message.guild.id), "roleid_mute": "0", "prefix": "." })
    prefix = server_coll.find_one({"server": f"{message.guild.id}" })["prefix"]
    owner = client.get_user(252378040024301570)
    memused = f"{psutil.virtual_memory().percent}%"
    p = psutil.Process(os.getpid())
    uptime = int(time.time()) - int(p.create_time())
    guilds = [g for g in client.guilds]
    channels = []
    users = 0
    avatar = discord.File("./imgs/avatar.png", filename="avatar.png")
    #image = discord.File("./imgs/genshin.gif", filename="genshin.gif")
    #dfiles = []
    #dfiles.append(avatar)
    #dfiles.append(image)
    for g in guilds:
        for c in g.channels:
            channels.append(c)
        users += g.member_count
    e = discord.Embed()
    e.title = "Information"
    e.color = discord.Color(0x2F3136)
    e.description = "**The bot is in development, so it often reloads**"
    e.timestamp = datetime.datetime.utcnow()
    e.set_thumbnail(url="attachment://avatar.png")
    #e.set_image(url="attachment://genshin.gif")
    e.set_footer(text=f"{message.author.name}", icon_url=f"{message.author.avatar_url}")
    e.add_field(name="Author", value=f"`{owner}`", inline=True)
    e.add_field(name="Prefix", value=f"`{prefix}`", inline=True)
    e.add_field(name="RAM usage", value=f"{memused}", inline=True)
    e.add_field(name="Platform", value=f"{os.uname().sysname}", inline=True)
    e.add_field(name="Ping", value=f"{int(round(client.latency * 100, 2))}", inline=True)
    e.add_field(name="Uptime", value=f"{seconds_to_hh_mm_ss(uptime)}", inline=True)
    #e.add_field(name="Total servers", value=f"{len(guilds)}", inline=True)
    #e.add_field(name="Total channels", value=f"{len(channels)}", inline=True)
    #e.add_field(name="Total users", value=f"{users}", inline=True)
    #e.add_field(name="⠀", value="[**BOT INVITE**](https://discord.com/api/oauth2/authorize?client_id=665667955220021250&permissions=8&scope=bot)", inline=True)
    #e.add_field(name="⠀", value="[**SUPPORT SERVER**](https://discord.gg/R4YxBaX)", inline=True)
    await message.channel.send(embed=e, file=avatar)