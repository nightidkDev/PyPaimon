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

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}дн. {h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{h:02d}:{m:02d}:{s:02d}"

def mandp(value):
    if value < 0:
        value = abs(value)
        return f"-{value}"
    elif value == 0:
        return f"{value}"
    else:
        return f"+{value}"

def lenfix(text, value):
    len_text = len(text)
    k = value - len_text
    return f"{text}{'⠀' * k}"

def param_check(value):
    if value == "reactions":
        return "Реакции"
    elif value == "marriage":
        return "Бракосочетания"
    elif value == "casino":
        return "Казино"
    elif value == "transfer":
        return "Переводы"
    elif value == "shop":
        return "Покупки"
    elif value == "admin":
        return "Прочее"
    elif value == "captcha":
        return "Коды в чате"
    elif value == "chat":
        return "Чат"
    elif value == "voice":
        return "Войс"
    elif value == "daily":
        return "Ежедневная награда"
    elif value == "bdaily":
        return "Буст награда"
    elif value == "lroom":
        return "Налог на любовную комнату"

def init():
    return [
                ["s|stats", stats().stats, "flood", "all"]
            ]

class stats():

    def __init__(self):
        pass

    async def stats(self, client, message, command, messageArray, lang_u):
        stats = db.prof_ec_users

        uid = None

        if len(messageArray) != 0:
            try:
                uid = message.guild.get_member(int(messageArray[0]))
            except:
                pass

        mm = list(filter(lambda x: x.bot is False, message.mentions))
        if uid == None and len(mm) == 0:
            user = stats.find_one({ "disid": str(message.author.id), "guild": str(message.guild.id) })
            s_chat = user["s_chat"]
            s_voice = user["s_voice"]
            v_channels = user["v_channels"]
            c_channels = user["c_channels"]

            ms = user["moneystats"]

            h1 = ms["history_1d"]
            h1v = []
            ha = ms["history"]
            hav = []

            e = discord.Embed(title=f"", description="", color=discord.Color(0x2F3136))
            
            for a in enumerate(h1):
                if h1[a[1]]["view"] == 1:
                    h1v.append([h1[a[1]]["count"], param_check(a[1])])

            for b in enumerate(h1):
                if ha[b[1]]["view"] == 1:
                    hav.append([ha[b[1]]["count"], param_check(b[1])])

            h1v.sort(key = lambda x: x[0], reverse=True)
            hav.sort(key = lambda x: x[0], reverse=True)

            h1vr = "\n".join(f'{lenfix(mandp(a[0]), 10)}——⠀⠀⠀⠀⠀⠀⠀⠀{a[1]}' for a in h1v)
            if h1vr == "":
                h1vr = "Неизвестно."
            havr = "\n".join(f'{lenfix(mandp(a[0]), 10)}——⠀⠀⠀⠀⠀⠀⠀⠀{a[1]}' for a in hav)
            if havr == "":
                havr = "Неизвестно."

            list_c = []
            top_c = ""
            count_c = 5

            for elem in c_channels:
                for channel, el in list(elem.items()):
                    list_c.append([channel, el])

            if len(list_c) < 5:
                count_c = len(list_c)

            list_c.sort(key = lambda x: x[1], reverse=True)

            for i in range(count_c):
                channel = message.guild.get_channel(int(list_c[i][0]))
                if channel is None:
                    channel_name = "удаленный-канал"
                else:
                    channel_name = channel.name.replace("`", "")
                top_c += f"{i + 1}. #{channel_name}: {list_c[i][1]}\n"

            if top_c == "":
                top_c = "Не активил(-а) в последнее время..."

            


            list_v = []
            top_v = ""
            count_v = 5

            for elem in v_channels:
                for channel, el in list(elem.items()):
                    list_v.append([channel, el])

            if len(list_v) < 5:
                count_v = len(list_v)

            if message.author.voice:
                x = int(time.time())
                lastt = int(user["last_time"])
                voicen = x - lastt
                s_voice += voicen
                for i in range(count_v):
                    if message.author.voice.channel.id == int(list_v[i][0]):
                        list_v[i][1] += voicen

            list_v.sort(key = lambda x: x[1], reverse=True)

            for i in range(count_v):
                channel = message.guild.get_channel(int(list_v[i][0]))
                if channel is None:
                    channel_name = "удаленный-канал"
                else:
                    channel_name = channel.name.replace("`", "")
                top_v += f"{i + 1}. #{channel_name}: {seconds_to_hh_mm_ss(list_v[i][1])}\n"

            if top_v == "":
                top_v = "Не активил(-а) в последнее время..."

            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀Баланс⠀⠀⠀⠀⠀⠀⠀```", value=f"```diff\n{mandp(ms['1d'])} (1 день)\n{mandp(ms['7d'])} (7 дней)\n{mandp(ms['14d'])} (14 дней)\n{mandp(ms['all'])} (все время)\n```")
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀Войс(7*)⠀⠀⠀⠀⠀⠀```", value=f"```css\n{seconds_to_hh_mm_ss(s_voice)}\n```")
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀Чат(7*)⠀⠀⠀⠀⠀⠀```", value=f"```css\n{s_chat}\n```")
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Полная статистика ⠀ (за 1 день)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```diff\n{h1vr}\n```", inline=False)
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Полная статистика ⠀(за всё время)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```diff\n{havr}\n```", inline=False)
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Топ(5*)-чат статистика (недельная)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```css\n\n{top_c}\n```", inline=False)
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Топ(5*)-войс статистика (недельная)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```css\n{top_v}\n```", inline=False)

            e.set_author(name=f"Статистика {message.author}", icon_url=message.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()

            e.set_footer(text="(7*) - статистика за 7 дней.\n(5*) - топ 5 самых активных каналов.\n\n(✿❛◡❛)")

            await message.channel.send(embed=e)
        elif len(mm) != 0:
            user = stats.find_one({ "disid": str(mm[0].id), "guild": str(message.guild.id) })
            s_chat = user["s_chat"]
            s_voice = user["s_voice"]
            v_channels = user["v_channels"]
            c_channels = user["c_channels"]

            ms = user["moneystats"]

            h1 = ms["history_1d"]
            h1v = []
            ha = ms["history"]
            hav = []

            e = discord.Embed(title=f"", description="", color=discord.Color(0x2F3136))
            
            for a in enumerate(h1):
                if h1[a[1]]["view"] == 1:
                    h1v.append([h1[a[1]]["count"], param_check(a[1])])

            for b in enumerate(h1):
                if ha[b[1]]["view"] == 1:
                    hav.append([ha[b[1]]["count"], param_check(b[1])])

            h1v.sort(key = lambda x: x[0], reverse=True)
            hav.sort(key = lambda x: x[0], reverse=True)

            h1vr = "\n".join(f'{lenfix(mandp(a[0]), 10)}——⠀⠀⠀⠀⠀⠀⠀⠀{a[1]}' for a in h1v)
            if h1vr == "":
                h1vr = "Неизвестно."
            havr = "\n".join(f'{lenfix(mandp(a[0]), 10)}——⠀⠀⠀⠀⠀⠀⠀⠀{a[1]}' for a in hav)
            if havr == "":
                havr = "Неизвестно."


            list_c = []
            top_c = ""
            count_c = 5

            for elem in c_channels:
                for channel, el in list(elem.items()):
                    list_c.append([channel, el])

            if len(list_c) < 5:
                count_c = len(list_c)

            list_c.sort(key = lambda x: x[1], reverse=True)

            for i in range(count_c):
                channel = message.guild.get_channel(int(list_c[i][0]))
                if channel == None:
                    channel = "удаленный-канал"
                top_c += f"{i + 1}. #{channel}: {list_c[i][1]}\n"

            if top_c == "":
                top_c = "Не активил(-а) в последнее время..."

            


            list_v = []
            top_v = ""
            count_v = 5

            for elem in v_channels:
                for channel, el in list(elem.items()):
                    list_v.append([channel, el])

            if len(list_v) < 5:
                count_v = len(list_v)

            if mm[0].voice:
                x = int(time.time())
                lastt = int(user["last_time"])
                voicen = x - lastt
                s_voice += voicen
                for i in range(count_v):
                    if mm[0].voice.channel.id == int(list_v[i][0]):
                        list_v[i][1] += voicen

            list_v.sort(key = lambda x: x[1], reverse=True)

            for i in range(count_v):
                channel = message.guild.get_channel(int(list_v[i][0]))
                if channel == None:
                    channel = "удаленный-канал"
                top_v += f"{i + 1}. #{channel}: {seconds_to_hh_mm_ss(list_v[i][1])}\n"

            if top_v == "":
                top_v = "Не активил(-а) в последнее время..."

            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀Баланс⠀⠀⠀⠀⠀⠀⠀```", value=f"```diff\n{mandp(ms['1d'])} (1 день)\n{mandp(ms['7d'])} (7 дней)\n{mandp(ms['14d'])} (14 дней)\n{mandp(ms['all'])} (все время)\n```")
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀Войс(7*)⠀⠀⠀⠀⠀⠀```", value=f"```css\n{seconds_to_hh_mm_ss(s_voice)}\n```")
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀Чат(7*)⠀⠀⠀⠀⠀⠀```", value=f"```css\n{s_chat}\n```")
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Полная статистика ⠀ (за 1 день)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```diff\n{h1vr}\n```", inline=False)
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Полная статистика ⠀(за всё время)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```diff\n{havr}\n```", inline=False)
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Топ(5*)-чат статистика (недельная)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```css\n{top_c}\n```", inline=False)
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Топ(5*)-войс статистика (недельная)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```css\n{top_v}\n```", inline=False)

            e.set_author(name=f"Статистика {mm[0]}", icon_url=mm[0].avatar_url)
            e.timestamp = datetime.datetime.utcnow()

            e.set_footer(text="(7*) - статистика за 7 дней.\n(5*) - топ 5 самых активных каналов.\n\n(✿❛◡❛)")

            await message.channel.send(embed=e)
        else:
            user = stats.find_one({ "disid": str(uid.id), "guild": str(message.guild.id) })
            s_chat = user["s_chat"]
            s_voice = user["s_voice"]
            v_channels = user["v_channels"]
            c_channels = user["c_channels"]

            ms = user["moneystats"]

            h1 = ms["history_1d"]
            h1v = []
            ha = ms["history"]
            hav = []

            e = discord.Embed(title=f"", description="", color=discord.Color(0x2F3136))
            
            for a in enumerate(h1):
                if h1[a[1]]["view"] == 1:
                    h1v.append([h1[a[1]]["count"], param_check(a[1])])

            for b in enumerate(h1):
                if ha[b[1]]["view"] == 1:
                    hav.append([ha[b[1]]["count"], param_check(b[1])])

            h1v.sort(key = lambda x: x[0], reverse=True)
            hav.sort(key = lambda x: x[0], reverse=True)

            h1vr = "\n".join(f'{lenfix(mandp(a[0]), 10)}——⠀⠀⠀⠀⠀⠀⠀⠀{a[1]}' for a in h1v)
            if h1vr == "":
                h1vr = "Неизвестно."
            havr = "\n".join(f'{lenfix(mandp(a[0]), 10)}——⠀⠀⠀⠀⠀⠀⠀⠀{a[1]}' for a in hav)
            if havr == "":
                havr = "Неизвестно."


            list_c = []
            top_c = ""
            count_c = 5

            for elem in c_channels:
                for channel, el in list(elem.items()):
                    list_c.append([channel, el])

            if len(list_c) < 5:
                count_c = len(list_c)

            list_c.sort(key = lambda x: x[1], reverse=True)

            for i in range(count_c):
                channel = message.guild.get_channel(int(list_c[i][0]))
                if channel == None:
                    channel = "удаленный-канал"
                top_c += f"{i + 1}. #{channel}: {list_c[i][1]}\n"

            if top_c == "":
                top_c = "Не активил(-а) в последнее время..."

            


            list_v = []
            top_v = ""
            count_v = 5

            for elem in v_channels:
                for channel, el in list(elem.items()):
                    list_v.append([channel, el])

            if len(list_v) < 5:
                count_v = len(list_v)

            if uid.voice:
                x = int(time.time())
                lastt = int(user["last_time"])
                voicen = x - lastt
                s_voice += voicen
                for i in range(count_v):
                    if uid.voice.channel.id == int(list_v[i][0]):
                        list_v[i][1] += voicen

            list_v.sort(key = lambda x: x[1], reverse=True)

            for i in range(count_v):
                channel = message.guild.get_channel(int(list_v[i][0]))
                if channel == None:
                    channel = "удаленный-канал"
                top_v += f"{i + 1}. #{channel}: {seconds_to_hh_mm_ss(list_v[i][1])}\n"

            if top_v == "":
                top_v = "Не активил(-а) в последнее время..."

            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀Баланс⠀⠀⠀⠀⠀⠀⠀```", value=f"```diff\n{mandp(ms['1d'])} (1 день)\n{mandp(ms['7d'])} (7 дней)\n{mandp(ms['14d'])} (14 дней)\n{mandp(ms['all'])} (все время)\n```")
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀Войс(7*)⠀⠀⠀⠀⠀⠀```", value=f"```css\n{seconds_to_hh_mm_ss(s_voice)}\n```")
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀Чат(7*)⠀⠀⠀⠀⠀⠀```", value=f"```css\n{s_chat}\n```")
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Полная статистика ⠀ (за 1 день)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```diff\n{h1vr}\n```", inline=False)
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Полная статистика ⠀(за всё время)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```diff\n{havr}\n```", inline=False)
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Топ(5*)-чат статистика (недельная)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```css\n{top_c}\n```", inline=False)
            e.add_field(name="```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Топ(5*)-войс статистика (недельная)⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```", value=f"```css\n{top_v}\n```", inline=False)

            e.set_author(name=f"Статистика {uid}", icon_url=uid.avatar_url)
            e.timestamp = datetime.datetime.utcnow()

            e.set_footer(text="(7*) - статистика за 7 дней.\n(5*) - топ 5 самых активных каналов.\n\n(✿❛◡❛)")

            await message.channel.send(embed=e)
        
        
