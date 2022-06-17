import discord
from discord.ext import commands
import pymongo
import config
import time
import asyncio
mc = pymongo.MongoClient(config.uri)
db = mc.aimi
server = db.server
staff = db.staff

async def check_stats_7d(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        server_info = server.find_one({ "server": "604083589570625555" })["7d_reset"]
        if int(time.time()) >= server_info:
            staff.update_many({}, { "$set": { "stats.7d": { "chat": 0, "voice": 0, "v_channels": {}, "c_channels": {} } } })
            server.update_one({ "server": "604083589570625555" }, { "$inc": { "7d_reset": 604800 } })
        await asyncio.sleep(10)

async def check_stats_14d(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        server_info = server.find_one({ "server": "604083589570625555" })["14d_reset"]
        if int(time.time()) >= server_info:
            staff.update_many({}, { "$set": { "stats.14d": { "chat": 0, "voice": 0, "v_channels": {}, "c_channels": {} } } })
            server.update_one({ "server": "604083589570625555" }, { "$inc": { "14d_reset": 1209600 } })
        await asyncio.sleep(10)

async def check_stats_30d(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        server_info = server.find_one({ "server": "604083589570625555" })["30d_reset"]
        if int(time.time()) >= server_info:
            staff.update_many({}, { "$set": { "stats.30d": { "chat": 0, "voice": 0, "v_channels": {}, "c_channels": {} } } })
            server.update_one({ "server": "604083589570625555" }, { "$inc": { "30d_reset": 2592000 } })
        await asyncio.sleep(10)

async def voicestat(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        guild = bot.get_guild(604083589570625555)
        while not guild:
            guild = bot.get_guild(604083589570625555)
            await asyncio.sleep(1)
        x = int(time.time())
        staff_role = guild.get_role(761771540181942273)
        a = list(filter(lambda a: a.voice is not None, guild.members))
        b = list(filter(lambda b: b.bot is False, a))
        c = list(filter(lambda c: staff_role in c.roles, b))
        for member in c:
            try:
                if staff.count_documents({ 'id': f"{member.id}" }) == 0:
                    return
                user = staff.find_one({ 'id': f'{member.id}' })
                if (len(member.voice.channel.members) > 1 or member.voice.channel.id in [809797697997242420, 914905633952780288, 931653817840304258, 933368883484692510]) and user['voice_start'] == 0:
                    user['voice_start'] = int(time.time())
                    continue
                if len(member.voice.channel.members) <= 1 and member.voice.channel.id not in [809797697997242420, 914905633952780288, 931653817840304258, 933368883484692510]:
                    continue
                
                if x - user['voice_start'] >= 60:
                    if not member.voice.mute and not member.voice.self_mute:
                        voice_channel = member.voice.channel
                        time_voice = int(time.time()) - user['voice_start']
                        staff.update_one({ "id": f"{member.id}" }, { "$set": { "voice_start": x }, "$inc": { "voice": time_voice, "stats.7d.voice": time_voice, "stats.14d.voice": time_voice, "stats.30d.voice": time_voice } })
                        if f"{voice_channel.id}" in user['stats']["7d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.7d.v_channels.{voice_channel.id}": time_voice } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.7d.v_channels.{voice_channel.id}": time_voice } })
                        if f"{voice_channel.id}" in user['stats']["14d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.4d.v_channels.{voice_channel.id}": time_voice } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.14d.v_channels.{voice_channel.id}": time_voice } })
                        if f"{voice_channel.id}" in user['stats']["30d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.30d.v_channels.{voice_channel.id}": time_voice } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.30d.v_channels.{voice_channel.id}": time_voice } })
            except BaseException as e:
                print(e)
        await asyncio.sleep(60)

class Activity(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        if message.author.bot:
            return
        if staff.count_documents({ 'id': f"{message.author.id}" }) == 0:
            return
        check_cmd = message.content.lower().split(" ")[0][len(config.PREFIX):]
        if not self.bot.get_command(check_cmd):
            staff.update_one({ "id": f"{message.author.id}" }, { "$inc": { 'chat': 1, "stats.7d.chat": 1, "stats.14d.chat": 1, "stats.30d.chat": 1 } })
            user = staff.find_one({ "id": f"{message.author.id}" })
            if f"{message.channel.id}" in user['stats']["7d"]["c_channels"]:
                staff.update_one({ "id": f"{message.author.id}" }, { "$inc": { f"stats.7d.c_channels.{message.channel.id}": 1 } })
            else:
                staff.update_one({ "id": f"{message.author.id}" }, { "$set": { f"stats.7d.c_channels.{message.channel.id}": 1 } })
            if f"{message.channel.id}" in user['stats']["14d"]["c_channels"]:
                staff.update_one({ "id": f"{message.author.id}" }, { "$inc": { f"stats.14d.c_channels.{message.channel.id}": 1 } })
            else:
                staff.update_one({ "id": f"{message.author.id}" }, { "$set": { f"stats.14d.c_channels.{message.channel.id}": 1 } })
            if f"{message.channel.id}" in user['stats']["30d"]["c_channels"]:
                staff.update_one({ "id": f"{message.author.id}" }, { "$inc": { f"stats.30d.c_channels.{message.channel.id}": 1 } })
            else:
                staff.update_one({ "id": f"{message.author.id}" }, { "$set": { f"stats.30d.c_channels.{message.channel.id}": 1 } })


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member is None:
            return
        if member.bot:
            return

        if staff.count_documents({ 'id': f"{member.id}" }) == 0:
            return
        if before is None:
            voice_b = None
        else:
            voice_b = before.channel
        if after is None:
            voice_a = None
        else:
            voice_a = after.channel

        if not voice_b and voice_a:
            members = list(filter(lambda x: member.id != x.id, voice_a.members))
            if len(members) == 0 and voice_a.id not in [809797697997242420, 914905633952780288, 931653817840304258, 933368883484692510]:
                return
            else:
                if len(members) == 1:
                    staff.update_one({ "id": f"{members[0].id}" }, { "$set": { "voice_start": int(time.time()) } })
                    staff.update_one({ "id": f"{member.id}" }, { "$set": { "voice_start": int(time.time()) } })
                else:
                    staff.update_one({ "id": f"{member.id}" }, { "$set": { "voice_start": int(time.time()) } })
        elif voice_b and not voice_a:
            members = list(filter(lambda x: member.id != x.id, voice_b.members))
            if len(members) == 0 and voice_b.id not in [809797697997242420, 914905633952780288, 931653817840304258, 933368883484692510]:
                return
            else:
                if len(members) == 1  and voice_b.id not in [809797697997242420, 914905633952780288, 931653817840304258, 933368883484692510]:
                    user_1 = staff.find_one({ "id": f"{members[0].id}" })["voice_start"]
                    user_2 = staff.find_one({ "id": f"{member.id}" })["voice_start"]
                    if user_1 != 0:
                        time_voice_1 = int(time.time()) - user_1
                        staff.update_one({ "id": f"{members[0].id}" }, { "$inc": { "voice": time_voice_1, "stats.7d.voice": time_voice_1, "stats.14d.voice": time_voice_1, "stats.30d.voice": time_voice_1 } })
                        user = staff.find_one({ "id": f"{members[0].id}" })
                        if f"{voice_b.id}" in user['stats']["7d"]["v_channels"]:
                            staff.update_one({ "id": f"{members[0].id}" }, { "$inc": { f"stats.7d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{members[0].id}" }, { "$set": { f"stats.7d.v_channels.{voice_b.id}": time_voice_1 } })
                        if f"{voice_b.id}" in user['stats']["14d"]["v_channels"]:
                            staff.update_one({ "id": f"{members[0].id}" }, { "$inc": { f"stats.14d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{members[0].id}" }, { "$set": { f"stats.14d.v_channels.{voice_b.id}": time_voice_1 } })
                        if f"{voice_b.id}" in user['stats']["30d"]["v_channels"]:
                            staff.update_one({ "id": f"{members[0].id}" }, { "$inc": { f"stats.30d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{members[0].id}" }, { "$set": { f"stats.30d.v_channels.{voice_b.id}": time_voice_1 } })
                    if user_2 != 0:
                        time_voice_2 = int(time.time()) - user_2
                        staff.update_one({ "id": f"{member.id}" }, { "$inc": { "voice": time_voice_2, "stats.7d.voice": time_voice_2, "stats.14d.voice": time_voice_2, "stats.30d.voice": time_voice_2 } })
                        user = staff.find_one({ "id": f"{member.id}" })
                        if f"{voice_b.id}" in user['stats']["7d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.7d.v_channels.{voice_b.id}": time_voice_2 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.7d.v_channels.{voice_b.id}": time_voice_2 } })
                        if f"{voice_b.id}" in user['stats']["14d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.14d.v_channels.{voice_b.id}": time_voice_2 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.14d.v_channels.{voice_b.id}": time_voice_2 } })
                        if f"{voice_b.id}" in user['stats']["30d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.30d.v_channels.{voice_b.id}": time_voice_2 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.30d.v_channels.{voice_b.id}": time_voice_2 } })
                else:
                    user_1 = staff.find_one({ "id": f"{member.id}" })["voice_start"]
                    if user_1 != 0:
                        time_voice_1 = int(time.time()) - user_1
                        staff.update_one({ "id": f"{member.id}" }, { "$inc": { "voice": time_voice_1, "stats.7d.voice": time_voice_1, "stats.14d.voice": time_voice_1, "stats.30d.voice": time_voice_1 } })
                        user = staff.find_one({ "id": f"{member.id}" })
                        if f"{voice_b.id}" in user['stats']["7d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.7d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.7d.v_channels.{voice_b.id}": time_voice_1 } })
                        if f"{voice_b.id}" in user['stats']["14d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.14d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.14d.v_channels.{voice_b.id}": time_voice_1 } })
                        if f"{voice_b.id}" in user['stats']["30d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.30d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.30d.v_channels.{voice_b.id}": time_voice_1 } })
        elif (voice_b and voice_a) and (voice_b != voice_a):
            members_1 = list(filter(lambda x: member.id != x.id, voice_b.members))
            members_2 = list(filter(lambda x: member.id != x.id, voice_a.members))
            if len(members_1) > 0 or voice_b.id in [809797697997242420, 914905633952780288, 931653817840304258, 933368883484692510]:
                if len(members_1) == 1 and voice_b.id not in [809797697997242420, 914905633952780288, 931653817840304258, 933368883484692510]:
                    user_1 = staff.find_one({ "id": f"{members_1[0].id}" })["voice_start"]
                    user_2 = staff.find_one({ "id": f"{member.id}" })["voice_start"]
                    if user_1 != 0:
                        time_voice_1 = int(time.time()) - user_1
                        staff.update_one({ "id": f"{members_1[0].id}" }, { "$inc": { "voice": time_voice_1, "stats.7d.voice": time_voice_1, "stats.14d.voice": time_voice_1, "stats.30d.voice": time_voice_1 } })
                        user_1_data = staff.find_one({ "id": f"{members_1[0].id}" })
                        if f"{voice_b.id}" in user_1_data['stats']["7d"]["v_channels"]:
                            staff.update_one({ "id": f"{members_1[0].id}" }, { "$inc": { f"stats.7d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{members_1[0].id}" }, { "$set": { f"stats.7d.v_channels.{voice_b.id}": time_voice_1 } })
                        if f"{voice_b.id}" in user_1_data['stats']["14d"]["v_channels"]:
                            staff.update_one({ "id": f"{members_1[0].id}" }, { "$inc": { f"stats.14d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{members_1[0].id}" }, { "$set": { f"stats.14d.v_channels.{voice_b.id}": time_voice_1 } })
                        if f"{voice_b.id}" in user_1_data['stats']["30d"]["v_channels"]:
                            staff.update_one({ "id": f"{members_1[0].id}" }, { "$inc": { f"stats.30d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{members_1[0].id}" }, { "$set": { f"stats.30d.v_channels.{voice_b.id}": time_voice_1 } })
                    if user_2 != 0:
                        time_voice_2 = int(time.time()) - user_2
                        staff.update_one({ "id": f"{member.id}" }, { "$inc": { "voice": time_voice_2, "stats.7d.voice": time_voice_2, "stats.14d.voice": time_voice_2, "stats.30d.voice": time_voice_2 } })
                        user_2_data = staff.find_one({ "id": f"{member.id}" })
                        if f"{voice_b.id}" in user_2_data['stats']["7d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.7d.v_channels.{voice_b.id}": time_voice_2 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.7d.v_channels.{voice_b.id}": time_voice_2 } })
                        if f"{voice_b.id}" in user_2_data['stats']["14d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.14d.v_channels.{voice_b.id}": time_voice_2 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.14d.v_channels.{voice_b.id}": time_voice_2 } })
                        if f"{voice_b.id}" in user_2_data['stats']["30d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.30d.v_channels.{voice_b.id}": time_voice_2 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.30d.v_channels.{voice_b.id}": time_voice_2 } })
                else:
                    user_1 = staff.find_one({ "id": f"{member.id}" })["voice_start"]
                    if user_1 != 0:
                        time_voice_1 = int(time.time()) - user_1
                        staff.update_one({ "id": f"{member.id}" }, { "$inc": { "voice": time_voice_1, "stats.7d.voice": time_voice_1, "stats.14d.voice": time_voice_1, "stats.30d.voice": time_voice_1 } })
                        user = staff.find_one({ "id": f"{member.id}" })
                        if f"{voice_b.id}" in user['stats']["7d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.7d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.7d.v_channels.{voice_b.id}": time_voice_1 } })
                        if f"{voice_b.id}" in user['stats']["14d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.14d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.14d.v_channels.{voice_b.id}": time_voice_1 } })
                        if f"{voice_b.id}" in user['stats']["30d"]["v_channels"]:
                            staff.update_one({ "id": f"{member.id}" }, { "$inc": { f"stats.30d.v_channels.{voice_b.id}": time_voice_1 } })
                        else:
                            staff.update_one({ "id": f"{member.id}" }, { "$set": { f"stats.30d.v_channels.{voice_b.id}": time_voice_1 } })

            if len(members_2) == 0 and voice_a.id not in [809797697997242420, 914905633952780288, 931653817840304258, 933368883484692510]:
                return
            else:
                if len(members_2) == 1 and voice_a.id not in [809797697997242420, 914905633952780288, 931653817840304258, 933368883484692510]:
                    staff.update_one({ "id": f"{members_2[0].id}" }, { "$set": { "voice_start": int(time.time()) } })
                    staff.update_one({ "id": f"{member.id}" }, { "$set": { "voice_start": int(time.time()) } })
                else:
                    staff.update_one({ "id": f"{member.id}" }, { "$set": { "voice_start": int(time.time()) } })

def setup(bot):
    bot.add_cog(Activity(bot))
    bot.loop.create_task(check_stats_7d(bot))
    bot.loop.create_task(check_stats_14d(bot))
    bot.loop.create_task(check_stats_30d(bot))
    bot.loop.create_task(voicestat(bot))  