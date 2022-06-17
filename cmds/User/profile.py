import datetime
import pymongo
import os
import discord
import time
import re
import sys
import json
sys.path.append("../../")
import config 
from libs import Profile
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

items_db = db.items

def toFixed(numObj, digits=0):
    return float(f"{numObj:.{digits}f}")
        
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

def money_kkk(number):

    str_m = "{:,}".format(int(number))
    return str_m.replace(",", " ")

def check_items(client, user):
    no_item_e = client.get_emoji(798326118201032724)

    items_from_db = items_db.find({ "type": "bonus_item" })

    item_exp = user["item_exp"].split(":")[1]
    item_money = user["item_money"].split(":")[1]

    rie = None
    rim = None

    if item_exp == "none":
        rie = f"{no_item_e}"
    else:
        for item in items_from_db:
            if item["name"].split(":")[1] == item_exp:
                rie = client.get_emoji(int(item["id"]))
                break

    if item_money == "none":
        rim = f"{no_item_e}"
    else:
        for item in items_from_db:
            if item["name"].split(":")[1] == item_money:
                rim = client.get_emoji(int(item["id"]))
                break

    return [rie, rim]

        
def init():
    return [["profile2|p2|prof2", profile().profile, "flood", "owner"]]
        

class profile:
    def __init__(self):
        pass

    async def profile(self, client, message, command, messageArray, lang_u):
        deny_channels = []
        no_item_e = client.get_emoji(798326118201032724)
        #if str(message.author.id) not in config.ADMINS:
        #    return await message.channel.send("Access denied. This command is currently disabled.") # убрать
        #time_start = time.time()
        coll = db.prof_ec_users
        check = await Profile.Profile().check_member(message.guild, messageArray)
        check_name = await Profile.Profile().check_member_name(message, messageArray)
        if len(messageArray) == 0 or (len(message.mentions) == 0 and (check == None and check_name == None)):
            
            prof = coll.find_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" })
            voice = prof["voice_time"]
            m = message.author
            if m.voice is not None:
                vcm = m.voice.channel.members
                vcm = list(filter(lambda x: x.bot is False, vcm))
                vcm = list(filter(lambda x: x.voice.mute is False and x.voice.deaf is False and x.voice.self_mute is False and x.voice.self_deaf is False, vcm))
                if (m.voice.channel.id) not in deny_channels and len(vcm) != 1 and m.voice.mute is False and m.voice.deaf is False and m.voice.self_mute is False and m.voice.self_deaf is False:
                    x = int(time.time())
                    lastt = int(prof["last_time"])
                    voice = int(prof["voice_time"])
                    voicen = x - lastt
                    voice += voicen
            lvl_line = await Profile.Profile().bar(client, prof["theme"], prof["exp"], prof["nexp"])
            money_l = int(prof["money"])
            money_l = money_kkk(money_l)
            if message.author.id == 252378040024301570:
                d = None
                with open('cmds/Dev/info.json', "r") as f:
                    d = json.load(f)
                if d["dev"]["state"] == 1:
                    money_l = "@Unlimited"
            money_emoji = client.get_emoji(775362271085461565)
            e = discord.Embed(title=f"Профиль • {message.author.name}", description="", color=discord.Color(0x2F3136))
            
            e.timestamp = datetime.datetime.utcnow()
            voice_emoji = client.get_emoji(754286926172913685)
            level_emoji = client.get_emoji(754287020922241125)
            msg_emoji = client.get_emoji(754286963112280124)
            voice_top = client.get_emoji(754286997626945588)
            wedding_rings = client.get_emoji(782944827947614228)
            clock = client.get_emoji(782943569568727080)
            partner = None
            if prof["partner"] == "":
                partner = "Нет"
            else:
                partner = str(client.get_user(int(prof["partner"])))
            marry_time = 0
            if prof["marry_time"] != 0:
                marry_time = int(time.time())-prof["marry_time"]
            else:
                marry_time = 0
            e.add_field(name=f"{money_emoji} Звёздочки", value=f"```css\n{money_l}\n```", inline=True)
            e.add_field(name=f"{msg_emoji} Чат актив", value="```css\n" + money_kkk(str(prof["msg"])) + "\n```", inline=True)
            e.add_field(name=f"{voice_emoji} Войс актив", value="```glsl\n" + seconds_to_hh_mm_ss(voice) + "\n```", inline=True)
            #if message.author.id == 252378040024301570: 
            #    items_user = check_items(client, prof)
            #    e.add_field(name=f"Предметы:", value=f"⠀Опыт: {items_user[0]}\n⠀Звездочки: {items_user[1]}", inline=True)
            #e.add_field(name=f"{exp_emoji} Experience {exp_emoji}", value="" + prof["exp"] + "/" + prof["nexp"] + " " + toFixed(float(int(prof["exp"]) / int(prof["nexp"]) * 100), 2) + "%", inline=True)
            e.add_field(name=f"{level_emoji} Уровень", value=f"{lvl_line} `" + str(int(int(prof["exp"]) / int(prof["nexp"]) * 100)) + "%` `(" + str(prof['exp']) + "/" + str(prof['nexp']) + ")`\n`[" + str(prof["lvl"]) + "] " + await Profile.Profile().rank(prof["lvl"]) + "`", inline=False)
            e.add_field(name=f"{wedding_rings} Брак", value="```diff\n- " + partner + "\n```", inline=True)
            e.add_field(name=f"{clock} Длительность брака", value="```glsl\n" + seconds_to_hh_mm_ss(marry_time) + "\n```", inline=True)
            e.set_thumbnail(url=message.author.avatar_url)
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        else:
            if len(message.mentions) != 0:
                if coll.count_documents({ "disid": str(message.mentions[0].id), "guild": f"{message.guild.id}" }) == 0:
                    x = int(time.time())
                    # nexp: 100, nlvl: 55
                    coll.insert_one({ "disid": str(message.mentions[0].id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{message.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
                    voice_test = False
                prof = coll.find_one({ "disid": str(message.mentions[0].id), "guild": f"{message.guild.id}" })
                voice = prof["voice_time"]
                m = message.mentions[0]
                if m.voice is not None:
                    vcm = m.voice.channel.members
                    vcm = list(filter(lambda x: x.bot is False, vcm))
                    vcm = list(filter(lambda x: x.voice.mute is False and x.voice.deaf is False and x.voice.self_mute is False and x.voice.self_deaf is False, vcm))
                    if (m.voice.channel.id) not in deny_channels and len(vcm) != 1 and m.voice.mute is False and m.voice.deaf is False and m.voice.self_mute is False and m.voice.self_deaf is False:
                        x = int(time.time())
                        lastt = int(prof["last_time"])
                        voice = int(prof["voice_time"])
                        voicen = x - lastt
                        voice += voicen
                lvl_line = await Profile.Profile().bar(client, prof["theme"], prof["exp"], prof["nexp"])
                money_l = int(prof["money"])
                money_l = money_kkk(money_l)
                if message.mentions[0].id == 252378040024301570:
                    d = None
                    with open('cmds/Dev/info.json', "r") as f:
                        d = json.load(f)
                    if d["dev"]["state"] == 1:
                        money_l = "@Unlimited"
                money_emoji = client.get_emoji(775362271085461565)
                e = discord.Embed(title=f"Профиль • {message.mentions[0].name}", description="", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()

                voice_emoji = client.get_emoji(754286926172913685)
                level_emoji = client.get_emoji(754287020922241125)
                msg_emoji = client.get_emoji(754286963112280124)
                voice_top = client.get_emoji(754286997626945588)
                wedding_rings = client.get_emoji(782944827947614228)
                clock = client.get_emoji(782943569568727080)
                partner = None
                if prof["partner"] == "":
                    partner = "Нет"
                else:
                    partner = str(client.get_user(int(prof["partner"])))
                marry_time = 0
                if prof["marry_time"] != 0:
                    marry_time = int(time.time())-prof["marry_time"]
                else:
                    marry_time = 0
                e.add_field(name=f"{money_emoji} Звёздочки", value=f"```css\n{money_l}\n```", inline=True)
                e.add_field(name=f"{msg_emoji} Чат актив", value="```css\n" + money_kkk(str(prof["msg"])) + "\n```", inline=True)
                e.add_field(name=f"{voice_emoji} Войс актив", value="```glsl\n" + seconds_to_hh_mm_ss(voice) + "\n```", inline=True)
                #e.add_field(name=f"{exp_emoji} Experience {exp_emoji}", value="" + prof["exp"] + "/" + prof["nexp"] + " " + toFixed(float(int(prof["exp"]) / int(prof["nexp"]) * 100), 2) + "%", inline=True)
                e.add_field(name=f"{level_emoji} Уровень", value=f"{lvl_line} `" + str(int(int(prof["exp"]) / int(prof["nexp"]) * 100)) + "%` `(" + str(prof['exp']) + "/" + str(prof['nexp']) + ")`\n`[" + str(prof["lvl"]) + "] " + await Profile.Profile().rank(prof["lvl"]) + "`", inline=False)
                e.add_field(name=f"{wedding_rings} Брак", value="```diff\n- " + partner + "\n```", inline=True)
                e.add_field(name=f"{clock} Длительность брака", value="```glsl\n" + seconds_to_hh_mm_ss(marry_time) + "\n```", inline=True)
                e.set_thumbnail(url=message.mentions[0].avatar_url)
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=e)
            elif check != None:
                if coll.count_documents({ "disid": str(message.guild.get_member(int(messageArray[0])).id), "guild": f"{message.guild.id}" }) == 0:
                    x = int(time.time())
                    # nexp: 100, nlvl: 55
                    coll.insert_one({ "disid": str(message.guild.get_member(int(messageArray[0])).id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{message.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
                prof = coll.find_one({ "disid": str(message.guild.get_member(int(messageArray[0])).id), "guild": f"{message.guild.id}" })
                voice = prof["voice_time"]
                m = message.guild.get_member(int(messageArray[0]))
                if m.voice is not None:
                    vcm = m.voice.channel.members
                    vcm = list(filter(lambda x: x.bot is False, vcm))
                    vcm = list(filter(lambda x: x.voice.mute is False and x.voice.deaf is False and x.voice.self_mute is False and x.voice.self_deaf is False, vcm))
                    if (m.voice.channel.id) not in deny_channels and len(vcm) != 1 and m.voice.mute is False and m.voice.deaf is False and m.voice.self_mute is False and m.voice.self_deaf is False:
                        x = int(time.time())
                        lastt = int(prof["last_time"])
                        voice = int(prof["voice_time"])
                        voicen = x - lastt
                        voice += voicen
                lvl_line = await Profile.Profile().bar(client, prof["theme"], prof["exp"], prof["nexp"])
                money_l = int(prof["money"])
                money_l = money_kkk(money_l)
                if message.guild.get_member(int(messageArray[0])).id == 252378040024301570:
                    d = None
                    with open('cmds/Dev/info.json', "r") as f:
                        d = json.load(f)
                    if d["dev"]["state"] == 1:
                        money_l = "@Unlimited"
                money_emoji = client.get_emoji(775362271085461565)
                e = discord.Embed(title=f"Профиль • {message.guild.get_member(int(messageArray[0])).name}", description="", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()

                #exp_emoji = client.get_emoji(714750046134075404)
                voice_emoji = client.get_emoji(754286926172913685)
                level_emoji = client.get_emoji(754287020922241125)
                msg_emoji = client.get_emoji(754286963112280124)
                voice_top = client.get_emoji(754286997626945588)
                wedding_rings = client.get_emoji(782944827947614228)
                clock = client.get_emoji(782943569568727080)
                partner = None
                if prof["partner"] == "":
                    partner = "Нет"
                else:
                    partner = str(client.get_user(int(prof["partner"])))
                marry_time = 0
                if prof["marry_time"] != 0:
                    marry_time = int(time.time())-prof["marry_time"]
                else:
                    marry_time = 0
                e.add_field(name=f"{money_emoji} Звёздочки", value=f"```css\n{money_l}\n```", inline=True)
                e.add_field(name=f"{msg_emoji} Чат актив", value="```css\n" + money_kkk(str(prof["msg"])) + "\n```", inline=True)
                e.add_field(name=f"{voice_emoji} Войс актив", value="```glsl\n" + seconds_to_hh_mm_ss(voice) + "\n```", inline=True)
                #e.add_field(name=f"{exp_emoji} Experience {exp_emoji}", value="" + prof["exp"] + "/" + prof["nexp"] + " " + toFixed(float(int(prof["exp"]) / int(prof["nexp"]) * 100), 2) + "%", inline=True)
                e.add_field(name=f"{level_emoji} Уровень", value=f"{lvl_line} `" + str(int(int(prof["exp"]) / int(prof["nexp"]) * 100)) + "%` `(" + str(prof['exp']) + "/" + str(prof['nexp']) + ")`\n`[" + str(prof["lvl"]) + "] " + await Profile.Profile().rank(prof["lvl"]) + "`", inline=False)
                e.add_field(name=f"{wedding_rings} Брак", value="```diff\n- " + partner + "\n```", inline=True)
                e.add_field(name=f"{clock} Длительность брака", value="```glsl\n" + seconds_to_hh_mm_ss(marry_time) + "\n```", inline=True)
                e.set_thumbnail(url=message.guild.get_member(int(messageArray[0])).avatar_url)
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=e)
            elif check_name != None:
                if coll.count_documents({ "disid": str(check_name.id), "guild": f"{message.guild.id}" }) == 0:
                    x = int(time.time())
                    # nexp: 100, nlvl: 55
                    coll.insert_one({ "disid": str(check_name.id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{message.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
                prof = coll.find_one({ "disid": str(check_name.id), "guild": f"{message.guild.id}" })
                voice = prof["voice_time"]
                m = check_name
                if m.voice is not None:
                    vcm = m.voice.channel.members
                    vcm = list(filter(lambda x: x.bot is False, vcm))
                    vcm = list(filter(lambda x: x.voice.mute is False and x.voice.deaf is False and x.voice.self_mute is False and x.voice.self_deaf is False, vcm))
                    if (m.voice.channel.id) not in deny_channels and len(vcm) != 1 and m.voice.mute is False and m.voice.deaf is False and m.voice.self_mute is False and m.voice.self_deaf is False:
                        x = int(time.time())
                        lastt = int(prof["last_time"])
                        voice = int(prof["voice_time"])
                        voicen = x - lastt
                        voice += voicen
                lvl_line = await Profile.Profile().bar(client, prof["theme"], prof["exp"], prof["nexp"])
                money_l = int(prof["money"])
                money_l = money_kkk(money_l)
                if check_name.id == 252378040024301570:
                    d = None
                    with open('cmds/Dev/info.json', "r") as f:
                        d = json.load(f)
                    if d["dev"]["state"] == 1:
                        money_l = "@Unlimited"
                money_emoji = client.get_emoji(775362271085461565)
                e = discord.Embed(title=f"Профиль • {check_name.name}", description="", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()

                #exp_emoji = client.get_emoji(714750046134075404)
                voice_emoji = client.get_emoji(754286926172913685)
                level_emoji = client.get_emoji(754287020922241125)
                msg_emoji = client.get_emoji(754286963112280124)
                voice_top = client.get_emoji(754286997626945588)
                wedding_rings = client.get_emoji(782944827947614228)
                clock = client.get_emoji(782943569568727080)
                partner = None
                if prof["partner"] == "":
                    partner = "Нет"
                else:
                    partner = str(client.get_user(int(prof["partner"])))
                marry_time = 0
                if prof["marry_time"] != 0:
                    marry_time = int(time.time())-prof["marry_time"]
                else:
                    marry_time = 0
                e.add_field(name=f"{money_emoji} Звёздочки", value=f"```css\n{money_l}\n```", inline=True)
                e.add_field(name=f"{msg_emoji} Чат актив", value="```css\n" + money_kkk(str(prof["msg"])) + "\n```", inline=True)
                e.add_field(name=f"{voice_emoji} Войс актив", value="```glsl\n" + seconds_to_hh_mm_ss(prof["voice_time"]) + "\n```", inline=True)
                #e.add_field(name=f"{exp_emoji} Experience {exp_emoji}", value="" + prof["exp"] + "/" + prof["nexp"] + " " + toFixed(float(int(prof["exp"]) / int(prof["nexp"]) * 100), 2) + "%", inline=True)
                e.add_field(name=f"{level_emoji} Уровень", value=f"{lvl_line} `" + str(int(int(prof["exp"]) / int(prof["nexp"]) * 100)) + "%` `(" + str(prof['exp']) + "/" + str(prof['nexp']) + ")`\n`[" + str(prof["lvl"]) + "] " + await Profile.Profile().rank(prof["lvl"]) + "`", inline=False)
                e.add_field(name=f"{wedding_rings} Брак", value="```diff\n- " + partner + "\n```", inline=True)
                e.add_field(name=f"{clock} Длительность брака", value="```glsl\n" + seconds_to_hh_mm_ss(marry_time) + "\n```", inline=True)
                e.set_thumbnail(url=check_name.avatar_url)
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=e)
        #time_end = time.time()
        #await message.channel.send(f"Time: {time_end - time_start}")