import datetime
import pymongo
import os
import discord
import time
import re
import sys
import random
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
        return f"{d:d}d {h:d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:d}:{s:02d}"

def init():
    return [
                ["rob", rob().rob, "flood", "all"],
                #["defrob|dr", rob().dr, "flood", "all"],
                #["givedefrob|gdr", rob().gdr, "flood", "owner"],
                #["takedefrob|tdr", rob().tdr, "flood", "owner"]
           ]

class rob():
    def __init__(self):
        pass

    async def rob(self, client, message, command, messageArray, lang_u):
        if str(message.author.id) not in config.ADMINS:
            return None
        users = db.prof_ec_users
        if len(messageArray) == 0 or messageArray[0] == "":
            return await message.channel.send("uknown member")
        else:
            user = users.find_one({"disid": str(message.author.id), "guild": str(message.guild.id)})
            if users.count_documents({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}) == 0:
                x = int(time.time())
                users.insert_one({ "disid": str(message.mentions[0].id), "warns": [], "money": 0, "voice_time": 0, "last_time": str(x), "voice_state": "0", "exp": 0, "nexp": "155", "lvl": 1, "nlvl": "65", "msg": 0, "msg_m": "0", "inv": [], "roles": [], "customs": [], "timely": 0, "timely_count": 0, 'theme': 0, 'partner': '', 'love_room': '', 'marry_time': 0, 'love_room_created': 0, "guild": f"{message.guild.id}", "s_voice": 0, "s_chat": 0, "v_channels": [], "c_channels": [], "rob": 1, " rob_time": 0, "can_rob": 1, "can_rob_time": 0, "rob_result": 0 })
            muser = users.find_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)})
            if user["can_rob"] == 0:
                return await message.channel.send(f"TIME, rob_result: {user['rob_result']}")
            else:
                if muser["money"] < 50:
                    return await message.channel.send("not enough stars, find more rich user!")
                else:
                    if muser["rob"] == 0:
                        return await message.channel.send("cannot rob this user")
                    else:
                        rob_result = random.randint(0, 2)
                        if rob_result == 0:
                            users.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "can_rob": 0, "can_rob_time": int(time.time()) + 86400, "rob_result": 0 }})
                            return await message.channel.send("fail rob")
                        elif rob_result == 1:
                            users.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "can_rob": 0, "can_rob_time": int(time.time()) + 43200, "rob_result": 1 }})
                            return await message.channel.send("rob, but police")
                        else:
                            users.update_one({"disid": str(message.author.id), "guild": str(message.guild.id)}, { "$set": { "can_rob": 0, "can_rob_time": int(time.time()) + 21600, "rob_result": 2 }})
                            return await message.channel.send("rob, hide")
                        users.update_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}, { "$set": { "rob": 0, "rob_time": int(time.time()) + 86400 }})
                

