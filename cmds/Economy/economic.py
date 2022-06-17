import datetime
import pymongo
import os
import discord
import time
import random
import numpy
import sys
from PIL import Image, ImageFont, ImageSequence, ImageDraw, ImageOps
sys.path.append("../../")
from libs import Builders
from libs import cmdlib
cooldown = cmdlib.cooldown()
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

sdb = db.u_settings

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
    items = list(filter(lambda x: x["type"] == "card", items))
    items = list(map(lambda x: list(x.items())[1][1], items))
    if custom in items:
        if lang == "ru":
            return "Куплено!"
        else:
            return "Purchased!"
    else:
        return f"{cost}{money_emoji}"

async def check_member(guild, text):
    try:
        member = guild.get_member(int(text[0]))
        return member
    except:
        return None

def declension(forms, val):
    cases = [ 2, 0, 1, 1, 1, 2 ]
    if val % 100 > 4 and val % 100 < 20:
        return forms[2]
    else:
        if val % 10 < 5:
            return forms[cases[val % 10]]
        else:
            return forms[cases[5]]

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

def seconds_to_hh_mm_ss_t(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    st = declension([ 'секунда', 'секунды', 'секунд' ], s)
    mt = declension([ 'минута', 'минуты', 'минут' ], m)
    ht = declension([ 'час', 'часа', 'часов' ], h)
    dt = declension([ 'день', 'дня', 'дней' ], d)

    if seconds >= 86400:
        return f"{d:d} {dt} {h:d} {ht} {m:d} {mt} {s:d} {st}"
    elif seconds >= 3600:
        return f"{h:d} {ht} {m:d} {mt}"
    elif seconds >= 60:
        return f"{m:d} {mt} {s:d} {st}"
    else:
        return f"{s:d} {st}"


def seconds_to_hh_mm_ss_tt(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    st = declension([ 'секунду', 'секунды', 'секунд' ], s)
    mt = declension([ 'минуту', 'минуты', 'минут' ], m)
    ht = declension([ 'час', 'часа', 'часов' ], h)
    dt = declension([ 'день', 'дня', 'дней' ], d)

    if seconds >= 86400:
        return f"{d:d} {dt} {h:d} {ht} {m:d} {mt} {s:d} {st}"
    elif seconds >= 3600:
        return f"{h:d} {ht} {m:d} {mt}"
    elif seconds >= 60:
        return f"{m:d} {mt} {s:d} {st}"
    else:
        return f"{s:d} {st}"

def checkcount(count):
    if count <= 9:
        return (4 + count) * 10
    else:
        return 150

def bcheckcount(count):
    if count <= 9:
        return count * 100
    else:
        return 1000

def toFixed(numObj, digits=0):
    return float(f"{numObj:.{digits}f}")

def init():
    return [
                ["timely|daily", economic().timely, "flood", "all", "help", "ежедневная награда"],
                ["boost", economic().boost, "flood", "boost", "help"],
                ["transfer", economic().transfer, "flood", "all", "help", "перевод определенной суммы другому человеку"],
                ["give", economic().give, "all", "owner"],
                ["take", economic().take, "all", "owner"]
            ]

class economic:
    def __init__(self):
        pass    
    
    async def transfer(self, client, message, command, messageArray, lang_u):
        money_emoji = client.get_emoji(775362271085461565)
        users = db.prof_ec_users
        user = users.find_one({"disid": str(message.author.id), "guild": f"{message.guild.id}"})
        check = await check_member(message.guild, messageArray)
        if len(messageArray) == 0 or (len(message.mentions) == 0 and check == None):
            e = discord.Embed(title="Ошибка", description="Укажите пользователя, которому хотите перевести звёздочки.\n\nПример команды: `.transfer @night. 1`")
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        else:
            member = None
            try:
                member = int(messageArray[0])
            except:
                pass
            if len(message.mentions) != 0:
                if message.mentions[0].id == 665667955220021250:
                    return
                try:
                    amount = int(messageArray[1])
                except:
                    e = discord.Embed(title="Ошибка", description="Укажите сумму, которую хотите перевести.\n\nПример команды: `.transfer @night. 1`", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                if message.mentions[0].id == message.author.id:
                    e = discord.Embed(title="Ошибка", description="Попробуйте указать не себя, а кого нибудь другого.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                if len(messageArray) <= 1:
                    e = discord.Embed(title="Ошибка", description="Укажите сумму, которую вы хотите перевести.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                if amount < 5:
                    e = discord.Embed(title="Ошибка", description="Укажите сумму более 5 примогемов.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                if user["money"] < amount:
                    e = discord.Embed(title="Ошибка", description="Недостаточно примогемов.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                res = cooldown.checkcd(message.author, "transfer")
                if res["result"]:
                    e = discord.Embed(title="", description=f"Подождите перед применением данной команды еще {seconds_to_hh_mm_ss_tt(res['time'] - int(time.time()))}.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                muser = users.find_one({"disid": str(message.mentions[0].id), "guild": f"{message.guild.id}"})
                #if muser is None:
                #    users.insert_one({ "disid": str(message.mentions[0].id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{message.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
                damount = amount
                oamount = amount - int(amount / 100 * 20)
                ms = muser["moneystats"]
                ms2 = user["moneystats"]
                ms["1d"] += oamount
                ms["7d"] += oamount
                ms["14d"] += oamount
                ms["all"] += oamount
                if ms["history_1d"]["transfer"]["view"] == 0:
                    ms["history_1d"]["transfer"]["view"] = 1
                ms["history_1d"]["transfer"]["count"] += oamount
                if ms["history"]["transfer"]["view"] == 0:
                    ms["history"]["transfer"]["view"] = 1
                ms["history"]["transfer"]["count"] += oamount
                ms2["1d"] -= damount
                ms2["7d"] -= damount
                ms2["14d"] -= damount
                ms2["all"] -= damount
                if ms2["history_1d"]["transfer"]["view"] == 0:
                    ms2["history_1d"]["transfer"]["view"] = 1
                ms2["history_1d"]["transfer"]["count"] -= damount
                if ms2["history"]["transfer"]["view"] == 0:
                    ms2["history"]["transfer"]["view"] = 1
                ms2["history"]["transfer"]["count"] -= damount
                users.update_one({ "disid": str(message.mentions[0].id), "guild": f"{message.guild.id}" }, { "$set": { "money": muser["money"] + oamount, "moneystats": ms } })
                users.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "money": user["money"] - damount, "moneystats": ms2 } })
                cooldown.setcd(message.author, "transfer", 10)
                e = discord.Embed(title="Переводы", description=f"Пользователю <@!{str(message.mentions[0].id)}> было переведено {oamount}{money_emoji} c 20% комиссией.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed = e)
                e = discord.Embed(title="Переводы", description=f"Вам было переведено {oamount}{money_emoji} от <@!{message.author.id}>.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                if sdb.count_documents({ "id": str(message.mentions[0].id), "guild": str(message.guild.id) }) == 0:
                    sdb.insert_one({ "id": str(message.mentions[0].id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

                user_m_s = sdb.find_one({ "id": str(message.mentions[0].id), "guild": str(message.guild.id) })
                try:
                    if user_m_s["notify_transfer"] == 1:
                        return await message.mentions[0].send(embed = e)
                    else:
                        return
                except:
                    sdb.update_one({ "id": str(message.mentions[0].id), "guild": str(message.guild.id) }, { "$set": { "notify_transfer": 0 } })
                    return
            else:
                if check.id == 665667955220021250:
                    return
                try:
                    amount = int(messageArray[1])
                except:
                    e = discord.Embed(title="Ошибка", description="Укажите сумму, которую хотите перевести.\n\nПример команды: `.transfer @night. 1`", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                if check.id == message.author.id:
                    e = discord.Embed(title="Ошибка", description="Попробуйте указать не себя, а кого нибудь другого.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                if len(messageArray) <= 1:
                    e = discord.Embed(title="Ошибка", description="Укажите сумму, которую вы хотите перевести.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                if user["money"] < int(messageArray[1]):
                    e = discord.Embed(title="Ошибка", description="Недостаточно примогемов.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                res = cooldown.checkcd(message.author, "transfer")
                if res["result"]:
                    e = discord.Embed(title="", description=f"Подождите перед применением данной команды еще {seconds_to_hh_mm_ss_tt(res['time'] - int(time.time()))}.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    return await message.channel.send(embed = e)
                muser = users.find({"disid": str(check.id), "guild": f"{message.guild.id}" })[0]
                #if muser is None:
                #    users.insert_one({}) # write insert
                damount = amount
                oamount = amount - int(amount / 100 * 20)
                ms = muser["moneystats"]
                ms2 = user["moneystats"]
                ms["1d"] += oamount
                ms["7d"] += oamount
                ms["14d"] += oamount
                ms["all"] += oamount
                if ms["history_1d"]["transfer"]["view"] == 0:
                    ms["history_1d"]["transfer"]["view"] = 1
                ms["history_1d"]["transfer"]["count"] += oamount
                if ms["history"]["transfer"]["view"] == 0:
                    ms["history"]["transfer"]["view"] = 1
                ms["history"]["transfer"]["count"] += oamount
                ms2["1d"] -= damount
                ms2["7d"] -= damount
                ms2["14d"] -= damount
                ms2["all"] -= damount
                if ms2["history_1d"]["transfer"]["view"] == 0:
                    ms2["history_1d"]["transfer"]["view"] = 1
                ms2["history_1d"]["transfer"]["count"] -= damount
                if ms2["history"]["transfer"]["view"] == 0:
                    ms2["history"]["transfer"]["view"] = 1
                ms2["history"]["transfer"]["count"] -= damount
                users.update_one({ "disid": str(check.id), "guild": f"{message.guild.id}" }, { "$set": { "money": muser["money"] + oamount, "moneystats": ms } })
                users.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "money": user["money"] - damount, "moneystats": ms2 } })
                cooldown.setcd(message.author, "transfer", 10)
                e = discord.Embed(title="Переводы", description=f"Пользователю <@!{str(check.id)}> было переведено {oamount}{money_emoji} с 20% комиссией.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed = e)
                e = discord.Embed(title="Переводы", description=f"Вам было переведено {oamount}{money_emoji} от <@!{message.author.id}>.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                if sdb.count_documents({ "id": str(check.id), "guild": str(message.guild.id) }) == 0:
                    sdb.insert_one({ "id": str(check.id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

                user_m_s = sdb.find_one({ "id": str(check.id), "guild": str(message.guild.id) })
                try:
                    if user_m_s["notify_transfer"] == 1:
                        return await check.send(embed = e)
                    else:
                        return
                except:
                    sdb.update_one({ "id": str(check.id), "guild": str(message.guild.id) }, { "$set": { "notify_transfer": 0 } })
                    return


    async def timely(self, client, message, command, messageArray, lang_u):
        money_emoji = client.get_emoji(775362271085461565)
        users = db.prof_ec_users
        user = users.find({"disid": str(message.author.id), "guild": f"{message.guild.id}" })[0]
        timely_count = user["timely_count"]
        #if int(time.time()) - user["timely"] >= 86400:
        #    timely_count = 1
        #    users.update_one({"disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "timely_count": 1 } })
        if user["timely_used"] == 0:
            timely_money = checkcount(timely_count)
            bonus = ""
            if int(timely_count) >= 100:
                timely_money += 400
                bonus = f" (150{money_emoji} + 400{money_emoji}(бонус))"
            elif int(timely_count) >= 75:
                timely_money += 300
                bonus = f" (150{money_emoji} + 300{money_emoji}(бонус))"
            elif int(timely_count) >= 50:
                timely_money += 200
                bonus = f" (150{money_emoji} + 200{money_emoji}(бонус))"
            elif int(timely_count) >= 25:
                timely_money += 100
                bonus = f" (150{money_emoji} + 100{money_emoji}(бонус))"
            ms = user["moneystats"]
            ms["1d"] += timely_money
            ms["7d"] += timely_money
            ms["14d"] += timely_money
            ms["all"] += timely_money
            if ms["history_1d"]["daily"]["view"] == 0:
                ms["history_1d"]["daily"]["view"] = 1
            ms["history_1d"]["daily"]["count"] += timely_money
            if ms["history"]["daily"]["view"] == 0:
                ms["history"]["daily"]["view"] = 1
            ms["history"]["daily"]["count"] += timely_money
            users.update_one({"disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "money": user["money"] + timely_money, "timely_count": timely_count + 1, "timely_used": 1, "moneystats": ms } })
            e = discord.Embed(title="Ежедневная награда", description=f"Твоя награда {timely_money}{money_emoji}{bonus} за использование команды {timely_count} раз(а) подряд.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        else:
            servers = db.server
            server = servers.find_one({ "server": "604083589570625555" })
            timely = server["timely_time"]
            x = int(time.time())
            time_timely = timely + 86400 - x
            e = discord.Embed(title="Ежедневная награда", description=f"Следующая награда в 8 часов утра по Москве.\n\nОсталось {seconds_to_hh_mm_ss_t(time_timely)}.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
    
    async def boost(self, client, message, command, messageArray, lang_u):
        money_emoji = client.get_emoji(775362271085461565)
        users = db.prof_ec_users
        user = users.find({"disid": str(message.author.id), "guild": f"{message.guild.id}" })[0]
        timely_count = user["btimely_count"]
        #if int(time.time()) - user["timely"] >= 86400:
        #    timely_count = 1
        #    users.update_one({"disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "timely_count": 1 } })
        if user["btimely_used"] == 0:
            timely_money = bcheckcount(timely_count)
            ms = user["moneystats"]
            ms["1d"] += timely_money
            ms["7d"] += timely_money
            ms["14d"] += timely_money
            ms["all"] += timely_money
            if ms["history_1d"]["bdaily"]["view"] == 0:
                ms["history_1d"]["bdaily"]["view"] = 1
            ms["history_1d"]["bdaily"]["count"] += timely_money
            if ms["history"]["bdaily"]["view"] == 0:
                ms["history"]["bdaily"]["view"] = 1
            ms["history"]["bdaily"]["count"] += timely_money
            users.update_one({"disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "money": user["money"] + timely_money, "btimely_count": timely_count + 1, "btimely_used": 1, "moneystats": ms } })
            e = discord.Embed(title="", description=f"Твоя награда {timely_money}{money_emoji} за использование команды {timely_count} раз(а) подряд.", color=discord.Color(0x2F3136))
            e.set_author(name="Буст награда", icon_url="https://cdn.discordapp.com/attachments/767015636354203659/833345983466307584/814411997637771265.gif")
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        else:
            servers = db.server
            server = servers.find_one({ "server": "604083589570625555" })
            timely = server["timely_time"]
            x = int(time.time())
            time_timely = timely + 86400 - x
            e = discord.Embed(title="", description=f"Следующая награда в 8 часов утра по Москве.\n\nОсталось {seconds_to_hh_mm_ss_t(time_timely)}.", color=discord.Color(0x2F3136))
            e.set_author(name="Буст награда", icon_url="https://cdn.discordapp.com/attachments/767015636354203659/833345983466307584/814411997637771265.gif")
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        
    async def give(self, client, message, command, messageArray, lang_u):
        if str(message.author.id) not in config.ADMINS and message.author.guild_permissions.administrator == False: #rewrite to permissions "administrator"
            return None
        time_start = int(time.time())
        e = discord.Embed(title="", description=f"Происходит выдача, пожалуйста, ожидайте...\nРасчётное время: вычисление...", color=discord.Color(0x8B0000))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        message_give = await message.channel.send(embed = e)
        try:
            money_emoji = client.get_emoji(775362271085461565)
            users = db.prof_ec_users
            list_give = []
            list_give_txt= ""
            add = int(messageArray[0])
            if len(message.mentions) == 0 and len(message.role_mentions) == 0:
                return
            reason = "Не указана."
            if (len(message.mentions) != 0 and messageArray[1] != f"<@!{message.mentions[0].id}>") or (len(message.role_mentions) != 0 and messageArray[1] != f"<@&{message.role_mentions[0].id}>"):
                reason = ""
                for i in range(1, len(messageArray)):
                    if (len(message.mentions) != 0 and messageArray[i] == f"<@!{message.mentions[0].id}>") or (len(message.role_mentions) != 0 and messageArray[i] == f"<@&{message.role_mentions[0].id}>"):
                        break
                    reason += f" {messageArray[i]}"
            reason = " ".join(reason.split())
            if reason.strip() == "":
                reason = "Не указана."
            time_x = len(message.role_mentions) + len(message.mentions)
            time_end = int(time.time()) + len(message.role_mentions) + len(message.mentions) + 10800
            e = discord.Embed(title="", description=f"Происходит выдача, пожалуйста, ожидайте...\nРасчётное время: {datetime.datetime.utcfromtimestamp(time_end).strftime('%d.%m.%Y %H:%M:%S')}({time_x} {declension([ 'секунда', 'секунды', 'секунд' ], time_x)})", color=discord.Color(0x8B0000))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message_give.edit(embed=e)
            list_count = 1
            for role in message.role_mentions:
                users_with_role = list(filter(lambda a: role in a.roles, message.guild.members))
                for user_r in users_with_role:
                    user = users.find_one({"disid": str(user_r.id), "guild": f"{message.guild.id}" })
                    if user is None:
                        x = int(time.time())
                        # MONEYSTATS EDIT JOPA
                        users.insert_one({ "disid": str(user_r.id), "warns": [], "money": add, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{message.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": { "1d": 0, "7d": 0, "14d": 0, "all": 0, "history_1d": { "reactions": { "count": 0, "view": 0 }, "marriage": { "count": 0, "view": 0 }, "casino": { "count": 0, "view": 0 }, "transfer": { "count": 0, "view": 0 }, "shop": { "count": 0, "view": 0 }, "admin": { "count": 0, "view": 0 }, "captcha": { "count": 0, "view": 0 }, "chat": { "count": 0, "view": 0 }, "voice": { "count": 0, "view": 0 }, "daily": { "count": 0, "view": 0 } }, "history": { "reactions": { "count": 0, "view": 0 }, "marriage": { "count": 0, "view": 0 }, "casino": { "count": 0, "view": 0 }, "transfer": { "count": 0, "view": 0 }, "shop": { "count": 0, "view": 0 }, "admin": { "count": 0, "view": 0 }, "captcha": { "count": 0, "view": 0 }, "chat": { "count": 0, "view": 0 }, "voice": { "count": 0, "view": 0 }, "daily": { "count": 0, "view": 0 } } }, "status": "", "background": 0, "timely_used": 1 })
                    else:
                        ms = user["moneystats"]
                        ms["1d"] += add
                        ms["7d"] += add
                        ms["14d"] += add
                        ms["all"] += add
                        if ms["history_1d"]["admin"]["view"] == 0:
                            ms["history_1d"]["admin"]["view"] = 1
                        ms["history_1d"]["admin"]["count"] += add
                        if ms["history"]["admin"]["view"] == 0:
                            ms["history"]["admin"]["view"] = 1
                        ms["history"]["admin"]["count"] += add
                        new_balance = user["money"] + add
                        users.update_one({"disid": str(user_r.id), "guild": f"{message.guild.id}" }, { "$set": { "money": new_balance, "moneystats": ms } })
                    e = discord.Embed(title="Выдача баланса", description=f"Вам было выдано {add}{money_emoji} по причине \"{reason}\".", color=discord.Color(0x00ff00))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    #try:
                    #    await user_r.send(embed=e)
                    #except:
                    #    pass
                list_give_txt += f"{list_count}. Выдано {len(users_with_role)} {declension([ 'пользователю', 'пользователям', 'пользователям' ], len(users_with_role))} c ролью <@&{role.id}>\n\n"
                list_count += 1
                
            for mention in message.mentions:
                user = users.find_one({"disid": str(mention.id), "guild": f"{message.guild.id}" })
                if user is None:
                    x = int(time.time())
                    users.insert_one({ "disid": str(mention.id), "warns": [], "money": add, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{message.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
                else:
                    ms = user["moneystats"]
                    ms["1d"] += add
                    ms["7d"] += add
                    ms["14d"] += add
                    ms["all"] += add
                    if ms["history_1d"]["admin"]["view"] == 0:
                        ms["history_1d"]["admin"]["view"] = 1
                    ms["history_1d"]["admin"]["count"] += add
                    if ms["history"]["admin"]["view"] == 0:
                        ms["history"]["admin"]["view"] = 1
                    ms["history"]["admin"]["count"] += add
                    new_balance = user["money"] + add
                    users.update_one({"disid": str(mention.id), "guild": f"{message.guild.id}" }, { "$set": { "money": new_balance, "moneystats": ms } })
                e = discord.Embed(title="Выдача баланса", description=f"Вам было выдано {add}{money_emoji} по причине \"{reason}\".", color=discord.Color(0x00ff00))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                try:
                    await mention.send(embed=e)
                except:
                    pass
                list_give.append(f"<@!{mention.id}>")
            if len(list_give) != 0: 
                list_give_txt += f"{list_count}. Выдано пользователям:\n"
                list_give_txt += "\n".join(list_give)
            time_end2 = int(time.time())
            e = discord.Embed(title="", description=f"Выдача завершена\n\n**Информация**\n\nНачало: {datetime.datetime.utcfromtimestamp(time_start + 10800).strftime('%d.%m.%Y %H:%M:%S')}\nКонец: {datetime.datetime.utcfromtimestamp(time_end2 + 10800).strftime('%d.%m.%Y %H:%M:%S')}\nЗаняло: {seconds_to_hh_mm_ss_t(time_end2 - time_start)} ({time_end2 - time_start} {declension([ 'секунда', 'секунды', 'секунд' ], time_end2 - time_start)})\n\n**Выдача**\n\nПо причине \"{reason}\" было выдано {messageArray[0]}{money_emoji} списку: \n{list_give_txt}", color=discord.Color(0x8B0000))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            #await message.channel.send(embed = e)
            return await message_give.edit(embed = e)
        except BaseException as e:
            e = discord.Embed(title="Error", description=f"{e}.", color=discord.Color(0x8B0000))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message_give.edit(embed = e)

    async def take(self, client, message, command, messageArray, lang_u):
        if message.author.guild_permissions.administrator == False: #rewrite to permissions "administrator"
            return None
        try:
            money_emoji = client.get_emoji(775362271085461565)
            users = db.prof_ec_users
            user = users.find({"disid": str(message.mentions[0].id), "guild": f"{message.guild.id}"})[0]
            if user["money"] < int(messageArray[0]):
                e = discord.Embed(title="Ошибка", description=f"У данного пользователя недостаточно примогемов.", color=discord.Color(0x8B0000))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            ms = user["moneystats"]
            ms["1d"] -= int(messageArray[0])
            ms["7d"] -= int(messageArray[0])
            ms["14d"] -= int(messageArray[0])
            ms["all"] -= int(messageArray[0])
            if ms["history_1d"]["admin"]["view"] == 0:
                ms["history_1d"]["admin"]["view"] = 1
            ms["history_1d"]["admin"]["count"] -= int(messageArray[0])
            if ms["history"]["admin"]["view"] == 0:
                ms["history"]["admin"]["view"] = 1
            ms["history"]["admin"]["count"] -= int(messageArray[0])
            new_balance = user["money"] - int(messageArray[0])
            users.update_one({"disid": str(message.mentions[0].id), "guild": f"{message.guild.id}"}, { "$set": { "money": new_balance, "moneystats": ms } })
            e = discord.Embed(title="Изменение баланса", description=f"Уничтожено {messageArray[0]}{money_emoji} у пользователю <@!{str(message.mentions[0].id)}>.", color=discord.Color(0x8B0000))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        except BaseException as e:
            e = discord.Embed(title="Error", description=f"{e}.", color=discord.Color(0x8B0000))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)