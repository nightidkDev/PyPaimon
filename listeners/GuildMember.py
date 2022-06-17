import discord
from discord.ext import commands
import datetime
import asyncio
import time
import random
import os
import re
import sys
sys.path.append("../../")
import config

# DataBase
import pymongo
login_url = config.uri
mongoclient = pymongo.MongoClient(login_url)
db = mongoclient.aimi
login_url2 = config.uri2
mongoclient = pymongo.MongoClient(login_url2)
db2 = mongoclient.aimi
users = db.prof_ec_users
lb = db.lb
no13 = db.no13
mutes = db.mutes
extended_sub = db2.extended_sub
        
class GuildMemberLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild

        if guild.id != 604083589570625555:
            return

        if lb.count_documents({ "id": f"{member.id}" }) > 0:
            role_lb = member.guild.get_role(767626360965038080)
            await member.add_roles(role_lb)

        if no13.count_documents({ "id": f"{member.id}" }) > 0:
            role_no13 = member.guild.get_role(810459698721062943)
            await member.add_roles(role_no13)

        if mutes.count_documents({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }) > 0:
            role_mute = member.guild.get_role(767025328405086218)
            await member.add_roles(role_mute)
        if extended_sub.count_documents({ 'id': f"{member.id}" }) > 0:
            role_sub = member.guild.get_role(912064706414526544)
            await member.add_roles(role_sub)

        if lb.count_documents({ "id": f"{member.id}" }) > 0 or no13.count_documents({ "id": f"{member.id}" }) > 0 or mutes.count_documents({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }) > 0:
            return

        if users.count_documents({ "disid": f"{member.id}", "guild": f"{guild.id}" }) == 0:
            return
        user = users.find_one({ "disid": f"{member.id}", "guild": f"{guild.id}" })
        warn_roles = [876711190091423816, 876714788732952637, 876771661628731432]
        if user["warns_counter_system"] >= 9:
            warn3 = guild.get_role(warn_roles[2])
            await member.add_roles(warn3)
        elif user["warns_counter_system"] >= 6:
            warn2 = guild.get_role(warn_roles[1])
            await member.add_roles(warn2)
        elif user["warns_counter_system"] >= 3:
            warn1 = guild.get_role(warn_roles[0])
            await member.add_roles(warn1)
        users.update_one({"disid": str(member.id), "guild": str(member.guild.id)}, { "$set": { "view": "true" } })

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.bot:
            return

        if after == self.bot.user:
            return
        
        if before.roles == after.roles:
            return

        if after.guild.id == 604083589570625555:
            #staff_roles = [767084198816776262, 760218179447685142, 768141743942008882, 760873610528161812, 766390222979465237, 766390759095533610, 761771540181942273]
            after_r = set(after.roles)
            before_r = set(before.roles)
            if len(after.roles) > len(before.roles):
                diff = list(after_r-before_r)
                to_do = "add"
            else:
                diff = list(before_r-after_r)
                to_do = "remove"
            diff = diff[0]
            staff = db.staff
            users = db.prof_ec_users
            lb = db.lb
            no13 = db.no13
            if to_do == "add":
                if diff.id == 767012156557623356:
                    config.wusers.append(f"{after.id}")
                if diff.id == 761771540181942273:
                    if staff.count_documents({ "id": f"{after.id}" }) == 0:
                        staff.insert_one({"id": str(after.id), "time_staff": int(time.time()), "warns": 0, "mutes": 0, "bans": 0, "mwarns": [], 'chat': 0, 'voice': 0, 'voice_start': 0, "stats": { "7d": { "voice": 0, "chat": 0,"v_channels": {}, "c_channels": {} }, "14d": { "voice": 0, "chat": 0,"v_channels": {}, "c_channels": {}}, "30d": { "voice": 0, "chat": 0,"v_channels": {}, "c_channels": {} } } })
                if diff.id == 767626360965038080:
                    jail = self.bot.get_channel(794660897271578625)
                    e = discord.Embed(title='', description=f'{after.mention}, добро пожаловать за решётку мондштадтской темницы!', color=0x2F3136)
                    e.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await jail.send(embed=e)
                if diff.id == 767025328405086218:
                    jail = self.bot.get_channel(794660897271578625)
                    e = discord.Embed(title='', description=f'{after.mention}, добро пожаловать за решётку мондштадтской темницы!', color=0x2F3136)
                    e.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await jail.send(embed=e)
                if diff.id == 810459698721062943:
                    if no13.count_documents({"id": str(after.id) }) == 0:
                        no13.insert_one({"id": str(after.id) })
            if to_do == "remove":
                if diff.id == 810459698721062943:
                    no13.delete_one({"id": str(after.id) })

            

def setup(bot):
    bot.add_cog(GuildMemberLog(bot))