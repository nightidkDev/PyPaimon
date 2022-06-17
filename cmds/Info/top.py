import datetime
import pymongo
import os
import discord
import time
import re
import sys
sys.path.append("../../")
import config 
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def toFixed(numObj, digits=0):
    return float(f"{numObj:.{digits}f}")

def money_kkk(number):

    str_m = "{:,}".format(int(number))
    return str_m.replace(",", " ")

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}дн. {h:02d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{h:02d}:{m:02d}:{s:02d}"

def init():
    return [
                ["top", top().top, "flood", "all", "help", "топ по уровню"],
                ["topvc", top().topvc, "flood", "all", "help", "топ по войс активу"],
                ["topm", top().topm, "flood", "all", "help", "топ по балансу"],
                ["topch", top().topch, "flood", "all", "help", "топ по чат активу"],
                ["topc", top().topc, "flood", "all", "help", "топ по бракам"]
            ]

class top:
    def __init__(self):
        pass

    async def top(self, client, message, command, messageArray, lang_u):
        start_time = time.time()
        end_time = time.time()
        # print(toFixed(end_time-start_time, 3))
        coll = db.prof_ec_users
        end_time = time.time()
        #print(toFixed(end_time-start_time, 3))
        top = list(coll.find({"guild": f"{message.guild.id}", "view": "true"}).sort([("lvl", -1), ("exp", -1)]).limit(8))
        #topid = [x["disid"] for x in top]
        #end_time = time.time()
        # print(toFixed(end_time-start_time, 3))
        e = discord.Embed(title="Топ по уровню", description="", color=discord.Color(0x2F3136))
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        count = len(top)
        #end_time = time.time()
        # print(toFixed(end_time-start_time, 3))
        #nottop = False
        #try:
        #    if topid.index(f"{message.author.id}") <= 7:
        #        nottop = True
        #        if count > 7:
        #            count = 8
        #    else:
        #        if count > 7:
        #            count = 7
        #except:
        #    if count > 7:
        #        count = 7
        #end_time = time.time()
        # print(toFixed(end_time-start_time, 3))
        #addspace = ""
        #if count == 7 and nottop is False:
        #    place = None
            #try:
            #    indexm = topid.index(f"{message.author.id}")
            #    user = str(client.get_user(int(top[indexm]["disid"])))
            #    lvl = top[indexm]["lvl"]
            #    place = indexm + 1
            #except:
            #    us = coll.find_one({"disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
            #    user = str(client.get_user(int(us["disid"])))
            #    lvl = us["lvl"]
            #    place = "100+"
            # if len(str(place)) == 2:
            #     addspace = "⠀"
            # elif len(str(place)) == 3:
            #     addspace = "⠀⠀"
            # elif len(str(place)) == 4:
            #     addspace = "⠀⠀⠀"
        #end_time = time.time()
        # print(toFixed(end_time-start_time, 3))
        for x in range(0, count):
            user = str(client.get_user(int(top[x]["disid"])))
            lvl = top[x]["lvl"]
            color = ""
            if x == 0:
                color = "fix"
            elif x == 1:
                color = "yaml"
            e.add_field(name=f"`#.⠀`", value=f"```{color}\n{x + 1}.\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Ник⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{user}\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀Уровень⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{lvl}\n```", inline=True)
        end_time = time.time()
        # print(toFixed(end_time-start_time, 3))
        # if count == 7 and nottop is False:
        #     place = None
        #     try:
        #         indexm = topid.index(f"{message.author.id}")
        #         user = str(client.get_user(int(top[indexm]["disid"])))
        #         lvl = top[indexm]["lvl"]
        #         place = indexm + 1
        #     except:
        #         us = coll.find_one({"disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
        #         user = str(client.get_user(int(us["disid"])))
        #         lvl = us["lvl"]
        #         place = "100+"
        #     if len(str(place)) == 2:
        #         addspace = "⠀"
        #     elif len(str(place)) == 3:
        #         addspace = "⠀⠀"
        #     elif len(str(place)) == 4:
        #         addspace = "⠀⠀⠀"
        #     color = ""
        #     e.add_field(name=f"`#.⠀{addspace}`", value=f"```{color}\n{place}.\n```", inline=True)
        #     e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Ник⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{user}\n```", inline=True)
        #     e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀Уровень⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{lvl}\n```", inline=True)
        #end_time = time.time()
        # print(toFixed(end_time-start_time, 3))
        await message.channel.send(embed=e)
        #end_time = time.time()
        # print(toFixed(end_time-start_time, 3))

    async def topch(self, client, message, command, messageArray, lang_u):
        coll = db.prof_ec_users
        top = list(coll.find({"guild": f"{message.guild.id}", "view": "true"}).sort("msg", -1).limit(8))
        #topid = [x["disid"] for x in top]
        e = discord.Embed(title="Топ по сообщениям", description="", color=discord.Color(0x2F3136))
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        count = len(top)
        #nottop = False
        # try:
        #     if topid.index(f"{message.author.id}") <= 7:
        #         nottop = True
        #         if count > 7:
        #             count = 8
        #     else:
        #         if count > 7:
        #             count = 7
        # except:
        #     if count > 7:
        #         count = 7
        # addspace = ""
        # if count == 7 and nottop is False:
        #     place = None
        #     try:
        #         indexm = topid.index(f"{message.author.id}")
        #         user = str(client.get_user(int(top[indexm]["disid"])))
        #         messages = top[indexm]["msg"]
        #         place = indexm + 1
        #     except:
        #         us = coll.find_one({"disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
        #         user = str(client.get_user(int(us["disid"])))
        #         messages = us["msg"]
        #         place = "100+"
        #     if len(str(place)) == 2:
        #         addspace = "⠀"
        #     elif len(str(place)) == 3:
        #         addspace = "⠀⠀"
        #     elif len(str(place)) == 4:
        #         addspace = "⠀⠀⠀"
        for x in range(0, count):
            user = str(client.get_user(int(top[x]["disid"])))
            messages = top[x]["msg"]
            color = ""
            if x == 0:
                color = "fix"
            elif x == 1:
                color = "yaml"
            e.add_field(name=f"`#.⠀`", value=f"```{color}\n{x + 1}.\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Ник⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{user}\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀Кол-во сообщений⠀⠀⠀⠀⠀`", value=f"```{color}\n{money_kkk(messages)}\n```", inline=True)
        # if count == 7 and nottop is False:
        #     place = None
        #     try:
        #         indexm = topid.index(f"{message.author.id}")
        #         user = str(client.get_user(int(top[indexm]["disid"])))
        #         messages = top[indexm]["msg"]
        #         place = indexm + 1
        #     except:
        #         us = coll.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
        #         user = str(client.get_user(int(us["disid"])))
        #         messages = us["msg"]
        #         place = "100+"
        #     if len(str(place)) == 2:
        #         addspace = "⠀"
        #     elif len(str(place)) == 3:
        #         addspace = "⠀⠀"
        #     elif len(str(place)) == 4:
        #         addspace = "⠀⠀⠀"
        #     color = ""
        #     e.add_field(name=f"`#.⠀{addspace}`", value=f"```{color}\n{place}.\n```", inline=True)
        #     e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Ник⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{user}\n```", inline=True)
        #     e.add_field(name=f"`⠀⠀⠀⠀⠀Кол-во сообщений⠀⠀⠀⠀⠀`", value=f"```{color}\n{money_kkk(messages)}\n```", inline=True)
        await message.channel.send(embed=e)

    async def topm(self, client, message, command, messageArray, lang_u):
        coll = db.prof_ec_users
        top = list(coll.find({"guild": f"{message.guild.id}", "view": "true"}).sort("money", -1).limit(8))
        #topid = [x["disid"] for x in top]
        e = discord.Embed(title="Топ по балансу", description="", color=discord.Color(0x2F3136))
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        count = len(top)
        #nottop = False
        # try:
        #     if topid.index(f"{message.author.id}") <= 7:
        #         nottop = True
        #         if count > 7:
        #             count = 8
        #     else:
        #         if count > 7:
        #             count = 7
        # except:
        #     if count > 7:
        #         count = 7
        # addspace = ""
        # if count == 7 and nottop is False:
        #     place = None
        #     try:
        #         indexm = topid.index(f"{message.author.id}")
        #         user = str(client.get_user(int(top[indexm]["disid"])))
        #         balance = top[indexm]["money"]
        #         place = indexm + 1
        #     except:
        #         us = coll.find_one({"disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
        #         user = str(client.get_user(int(us["disid"])))
        #         balance = us["money"]
        #         place = "100+"
        #     if len(str(place)) == 2:
        #         addspace = "⠀"
        #     elif len(str(place)) == 3:
        #         addspace = "⠀⠀"
        #     elif len(str(place)) == 4:
        #         addspace = "⠀⠀⠀"
        for x in range(0, count):
            user = str(client.get_user(int(top[x]["disid"])))
            balance = int(top[x]["money"])
            color = ""
            if x == 0:
                color = "fix"
            elif x == 1:
                color = "yaml"
            e.add_field(name=f"`#.⠀`", value=f"```{color}\n{x + 1}.\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Ник⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{user}\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀Баланс⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{money_kkk(balance)}\n```", inline=True)
        # if count == 7 and nottop is False:
        #     place = None
        #     try:
        #         indexm = topid.index(f"{message.author.id}")
        #         user = str(client.get_user(int(top[indexm]["disid"])))
        #         balance = top[indexm]["money"]
        #         place = indexm + 1
        #     except:
        #         us = coll.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
        #         user = str(client.get_user(int(us["disid"])))
        #         balance = us["money"]
        #         place = "100+"
        #     if len(str(place)) == 2:
        #         addspace = "⠀"
        #     elif len(str(place)) == 3:
        #         addspace = "⠀⠀"
        #     elif len(str(place)) == 4:
        #         addspace = "⠀⠀⠀"
        #     color = ""
        #     e.add_field(name=f"`#.⠀{addspace}`", value=f"```{color}\n{place}.\n```", inline=True)
        #     e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Ник⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{user}\n```", inline=True)
        #     e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀Баланс⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{money_kkk(balance)}\n```", inline=True)
        await message.channel.send(embed=e)
        #text = "\n".join([str(x + 1) + ". <@" + array_top[x].split(" ")[0] + "> - " + array_top[x].split(" ")[1] + f"{money_emoji}" for x in range(0, 10)])
        #await message.channel.send(embed = discord.Embed.from_dict({'title': 'Money Top', 'description': text, 'color': 3092790}))

    async def topvc(self, client, message, command, messageArray, lang_u):
        coll = db.prof_ec_users
        top1 = [coll.find_one({ "disid": "252378040024301570", "guild": "604083589570625555" })]
        top2 = list(coll.find({"guild": f"{message.guild.id}", "view": "true"}).sort("voice_time", -1).limit(7))
        top = top1 + top2
        #topid = [x["disid"] for x in top]
        e = discord.Embed(title="Топ по войсу", description="", color=discord.Color(0x2F3136))
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        count = len(top)
        # nottop = False
        # try:
        #     if topid.index(f"{message.author.id}") <= 7:
        #         nottop = True
        #         if count > 7:
        #             count = 8
        #     else:
        #         if count > 7:
        #             count = 7
        # except:
        #     if count > 7:
        #         count = 7
        # addspace = ""
        # if count == 7 and nottop is False:
        #     place = None
        #     try:
        #         indexm = topid.index(f"{message.author.id}")
        #         user = str(client.get_user(int(top[indexm]["disid"])))
        #         time = seconds_to_hh_mm_ss(int(top[indexm]["voice_time"]))
        #         place = indexm + 1
        #     except:
        #         us = coll.find_one({"disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
        #         user = str(client.get_user(int(us["disid"])))
        #         time = seconds_to_hh_mm_ss(int(us["voice_time"]))
        #         place = "100+"
        #     if len(str(place)) == 2:
        #         addspace = "⠀"
        #     elif len(str(place)) == 3:
        #         addspace = "⠀⠀"
        #     elif len(str(place)) == 4:
        #         addspace = "⠀⠀⠀"
        for x in range(0, count):
            user = str(client.get_user(int(top[x]["disid"])))
            time = seconds_to_hh_mm_ss(int(top[x]["voice_time"]))
            color = ""
            if x == 0:
                color = "fix"
            elif x == 1:
                color = "yaml"
            e.add_field(name=f"`#.⠀`", value=f"```{color}\n{x + 1}.\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Ник⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{user}\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀Время⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{time}\n```", inline=True)
        # if count == 7 and nottop is False:
        #     place = None
        #     try:
        #         indexm = topid.index(f"{message.author.id}")
        #         user = str(client.get_user(int(top[indexm]["disid"])))
        #         time = seconds_to_hh_mm_ss(int(top[indexm]["voice_time"]))
        #         place = indexm + 1
        #     except:
        #         us = coll.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
        #         user = str(client.get_user(int(us["disid"])))
        #         time = seconds_to_hh_mm_ss(int(us["voice_time"]))
        #         place = "100+"
        #     if len(str(place)) == 2:
        #         addspace = "⠀"
        #     elif len(str(place)) == 3:
        #         addspace = "⠀⠀"
        #     elif len(str(place)) == 4:
        #         addspace = "⠀⠀⠀"
        #     color = ""
        #     e.add_field(name=f"`#.⠀{addspace}`", value=f"```{color}\n{place}.\n```", inline=True)
        #     e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Ник⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{user}\n```", inline=True)
        #     e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀Время⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{time}\n```", inline=True)
        await message.channel.send(embed=e)
        #text = "\n".join([str(x + 1) + ". <@" + array_top[x].split(" ")[0] + "> - " + seconds_to_hh_mm_ss(int(array_top[x].split(" ")[1])) for x in range(0, 10)])
        #await message.channel.send(embed = discord.Embed.from_dict({'title': 'Voice Top', 'description': text, 'color': 3092790}))

    async def topc(self, client, message, command, messageArray, lang_u):
        coll = db.prof_ec_users
        top = list(coll.find({"guild": f"{message.guild.id}", "marry_time": { "$gte": 1 }, "view": "true" }).sort("marry_time", 1).limit(16))
        e = discord.Embed(title="Топ браков", description="", color=discord.Color(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        count = len(top)
        a = 0
        i = 1
        for x in range(0, count):
            if a == 1:
                a = 0
                continue
            user1, user2 = client.get_user(int(top[x]["disid"])), client.get_user(int(top[x]["partner"]))
            
            time_m = seconds_to_hh_mm_ss(int(int(time.time()) - int(top[x]["marry_time"])))
            color = ""
            if i == 1:
                color = "fix"
            elif i == 2:
                color = "yaml"
            e.add_field(name=f"`#.⠀`", value=f"```{color}\n{i}.\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Пара⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{user1} ❤ {user2}\n```", inline=True)
            e.add_field(name=f"`⠀⠀⠀⠀⠀⠀⠀Время⠀⠀⠀⠀⠀⠀⠀`", value=f"```{color}\n{time_m}\n```", inline=True)
            a += 1
            i += 1
        await message.channel.send(embed=e)