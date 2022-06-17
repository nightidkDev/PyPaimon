import discord
import time
import datetime
import sys
import time
import pymongo
sys.path.append("../../")
import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

users = db.prof_ec_users
sdb = db.u_settings

def voice_members(voice_channels):
    members = []
    for channel in voice_channels:
        if len(channel.members) == 0: continue
        for member in channel.members:
            if member.bot: continue
            members.append(member)

    return members


def voice_member_no_mute(voice_members):
    members = []
    for member in voice_members:
        if member.bot: continue
        if member.voice.mute or member.voice.deaf or member.voice.self_mute or member.voice.self_deaf: continue
        members.append(member)
    return members

async def voice_money(client: discord.Client):
    
    guild = client.get_guild(604083589570625555)
    x = int(time.time())
    start = time.time()
    a = voice_members(guild.voice_channels)
    end = time.time()
    print(end - start, len(a))
    
    start = time.time()
    for member in a:
        if not member:
            continue
        week_stats = db.week_stats
        if week_stats.count_documents({ "id": f"{member.id}" }) == 0:
            week_stats.insert_one({ "id": f"{member.id}", "chat": 0, "voice": 0 })
        uws = week_stats.find_one({ "id": f"{member.id}" })
        if users.count_documents({ "disid": str(member.id), "guild": f"{guild.id}" }) == 0:
            users.insert_one({ "disid": str(member.id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "100", "lvl": 1, "nlvl": "55", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{member.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "rob": 1, "view": "true", "clan": "", "donate_money": 0, "ignore_list": [], "moneystats": config.cmoneystats, "status": "", "background": 0, "timely_used": 1, "btimely_count": 1, "btimely_used": 0, "cooldown": [], "depositInClan": 0, "history_warns": [], "warns_counter_system": 0, "wishes": config.wishes_db_user, "wishesCount": config.wishesCount })
        user = users.find_one({ "disid": str(member.id), "guild": f"{guild.id}" })
        if sdb.count_documents({ "id": str(member.id), "guild": str(guild.id) }) == 0:
            sdb.insert_one({ "id": str(member.id), "guild": str(guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })
        user_s = sdb.find_one({ "id": str(member.id), "guild": f"{guild.id}" })
        if user["view"] == "false":
            continue
        if user["voice_state"] == "0":
            if (member.voice.mute == False and member.voice.mute == False) and (member.voice.self_mute == False and member.voice.self_mute == False):
                users.update_one({ "disid": str(member.id), "guild": f"{guild.id}" }, { "$set": { "voice_state": "1", "last_time": str(x) } })

        if int(user["exp"]) >= int(user["nexp"]):
            exp_ins = int(user["exp"]) - int(user["nexp"])
            nexp_ins = int(user["nexp"]) + int(user["nlvl"])
            nlvl_ins = int(user["nlvl"]) + 10
            lvl_ins = int(user["lvl"]) + 1
            moneyu = user["money"]
            bonusm = 0
            ranks = config.ranks
            last_role = None
            for rank in ranks:
                if lvl_ins == rank[0]:
                    bonusm = rank[2]
                else:
                    bonusm = 0
                if lvl_ins >= rank[0]:
                    role_lvl = guild.get_role(int(rank[1]))
                    index_role = ranks.index([rank[0], rank[1], rank[2]])
                    if index_role != len(ranks) - 1:
                        last_role = guild.get_role(int(ranks[index_role + 1][1]))
                    if user_s["role_lvl"] == 1:
                        if role_lvl not in member.roles:
                            await member.add_roles(role_lvl)
                        if last_role != None:
                            if last_role in member.roles:
                                await member.remove_roles(last_role)
                    break
            moneyu += bonusm
            users.update_one({ "disid": str(member.id), "guild": f"{guild.id}" }, { "$set": { "exp": exp_ins, "nexp": str(nexp_ins), "lvl": lvl_ins, "nlvl": str(nlvl_ins), "money": moneyu } })
            lvlMessage = "Ты получил(-а) {level} уровень на сервере {server}!"
            lvlMessage = lvlMessage.replace("{server}", guild.name)
            lvlMessage = lvlMessage.replace("{level}", str(lvl_ins))
            e = discord.Embed(title="", description=f"{lvlMessage}", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            try:
                if user_s["notify_lvl"] == 1:
                    await member.send(embed=e)
            except:
                sdb.update_one({ "id": str(member.id), "guild": str(guild.id) }, { "$set": { "notify_lvl": 0 } })
        else:
            member_voice = member.voice
            if member_voice == None:
                continue
            last = int(user["last_time"])
            mo_time = x - last
            if int(mo_time / 60) >= 1:
                vcm = voice_member_no_mute(member_voice.channel.members)
                
                if member.voice.channel.id == 788024928036847616:
                    continue
                if member.voice.channel.category:
                    if member.voice.channel.category.id == 865613264296869908:
                        continue

                if member.voice.mute or member.voice.deaf or member.voice.self_mute or member.voice.self_deaf:
                    continue

                count_members = len(vcm)

                #if member.id == 518427777523908608 or member.id == 252378040024301570:
                #    print(f"{member} ({int(mo_time / 60)}) - {member.voice.channel} - {count_members} ({[x.name for x in vcm]})")

                if count_members == 1 and member_voice.channel.id not in [809797697997242420, 914905633952780288, 931653817840304258]:
                    continue
                if count_members > 10:
                    count_members = 10
                if member_voice.channel.id in [809797697997242420, 914905633952780288, 931653817840304258]:
                    count_members = 10

                multiplier = 1
                multiplier_money = 1
                boost_role = member.guild.get_role(612661327101558796)
                if boost_role in member.roles:
                    multiplier = 1.5
                    multiplier_money = 2
                #if member_voice.channel.id == 860615065283198996:
                #    multiplier_money = 2
                clans_db = db.clans
                boosterclan = 1
                if user["clan"] != "":
                    clan = clans_db.find_one({ "id": int(user["clan"]) })
                    boosterclan = clan["booster"]
                exp = int(3 * count_members * multiplier * boosterclan)
                exp_now = int(user["exp"])
                exp_ins = exp + exp_now
                #if member.id == 518427777523908608:
                #    exp_ins = int(exp_ins / 3)
                ms = user["moneystats"]
                ms["1d"] += 2
                ms["7d"] += 2
                ms["14d"] += 2
                ms["all"] += 2
                if ms["history_1d"]["voice"]["view"] == 0:
                    ms["history_1d"]["voice"]["view"] = 1
                ms["history_1d"]["voice"]["count"] += 2
                if ms["history"]["voice"]["view"] == 0:
                    ms["history"]["voice"]["view"] = 1
                ms["history"]["voice"]["count"] += 2
                if user["clan"] != "":
                    expn = int(exp / 2)
                    if clan["exp"] + expn < clan["nexp"] * 2:
                        clans_db.update_one({ "id": int(user["clan"]) }, { "$inc": { "exp": expn } })
                users.update_one({ "disid": user["disid"], "guild": f"{guild.id}" }, { "$set": { "last_time": str(x), "exp": exp_ins, "moneystats": ms }, "$inc": { "money": int(2 * multiplier_money * boosterclan), "voice_time": mo_time } })
        member_voice = member.voice
        last = int(user["last_time"])
        mo_time = x - last
        if int(mo_time / 60) >= 1:
            week_stats.update_one({ "id": user["disid"] }, { "$inc": { "voice": mo_time } })
            foundChannel = False
            time_n = 0
            for elem in user["v_channels"]:
                for channel, time_c in list(elem.items()):
                    if channel == str(member_voice.channel.id):
                        foundChannel = True
                        time_n = time_c
                        break
            if foundChannel == False:
                users.update_one({"disid": user["disid"], "guild": str(guild.id)}, { "$push": { "v_channels": { str(member_voice.channel.id): 0 } } })
            else:
                users.update_one({ "disid": user["disid"], "guild": f"{guild.id}" }, { "$set": { f"v_channels.$[element].{member_voice.channel.id}": time_n + mo_time, "s_voice": user["s_voice"] + mo_time } }, array_filters=[ { f"element.{member_voice.channel.id}": time_n } ])

    end = time.time()
    print(end - start)
