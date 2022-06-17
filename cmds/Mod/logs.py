import datetime
import pymongo
import os
import discord
import time
import random
import sys
sys.path.append("../../")
import config 
from libs import DataBase
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

logs_channel = 745584798558584922

def init():
    return []

class logs:

    def __init__(self):
        pass

    async def delete(self, message):
        channel = message.guild.get_channel(logs_channel)
        e = discord.Embed(title="Удалено сообщение", description=f"Удалённое сообщение: ```{message.content}```", color=discord.Color(0x8B0000))
        e.add_field(name="```Пользователь```", value=f"```{str(message.author)} • {message.author.id}```", inline=True)
        e.add_field(name="```Канал```", value=f"```{message.channel.name}```", inline=True)
        e.add_field(name="```Дата сообщения```", value=f"```{message.created_at.strftime('%H:%M:%S %d.%m.%Y')}```", inline=True)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.guild.name}", icon_url=message.guild.icon_url)
        #try:
        #    await channel.send(embed = e)
        #except:
        #    pass

    async def update_roles(self, before, after, client):
        if after.guild.id == 604083589570625555:
            staff_roles = [767084198816776262, 760218179447685142, 768141743942008882, 760873610528161812, 766390222979465237, 766390759095533610, 761771540181942273]
            black_staff = []
            after_r = set(after.roles)
            before_r = set(before.roles)
            to_do = ""
            if len(after.roles) > len(before.roles):
                diff = list(after_r-before_r)
                to_do = "add"
            else:
                diff = list(before_r-after_r)
                to_do = "remove"
            diff = diff[0]
            if after.id in black_staff:
                if to_do == "add":
                    if diff.id in staff_roles:
                        await after.remove_roles(diff)
            staff = db.staff
            users = db.prof_ec_users
            lb = db.lb
            no13 = db.no13
            if to_do == "add":
                if diff.id == 767012156557623356:
                    config.wusers.append(f"{after.id}")
                if diff.id == 761771540181942273:
                    staff.insert_one({"id": str(after.id), "time_staff": int(time.time()), "warns": 0, "mutes": 0, "bans": 0, "mwarns": [] })
                if diff.id == 767626360965038080:
                    if lb.count_documents({"id": str(after.id) }) == 0:
                        users.update_one({"disid": str(after.id), "guild": str(after.guild.id)}, { "$set": { "view": "false" } })
                        lb.insert_one({"id": str(after.id) })
                    jail = client.get_channel(794660897271578625)
                    e = discord.Embed(title='', description=f'{after.mention}, добро пожаловать за решётку мондштадтской темницы!', color=0x2F3136)
                    e.set_footer(text=client.user.name, icon_url=client.user.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await jail.send(embed=e)
                if diff.id == 767025328405086218:
                    jail = client.get_channel(794660897271578625)
                    e = discord.Embed(title='', description=f'{after.mention}, добро пожаловать за решётку мондштадтской темницы!', color=0x2F3136)
                    e.set_footer(text=client.user.name, icon_url=client.user.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await jail.send(embed=e)
                if diff.id == 810459698721062943:
                    if no13.count_documents({"id": str(after.id) }) == 0:
                        no13.insert_one({"id": str(after.id) })
            if to_do == "remove":
                #if diff.id == 761771540181942273:
                    #staff.delete_one({"id": str(after.id)})
                if diff.id == 767626360965038080:
                    users.update_one({"disid": str(after.id), "guild": str(after.guild.id)}, { "$set": { "view": "true" } })
                    lb.delete_one({"id": str(after.id) })
                if diff.id == 810459698721062943:
                    no13.delete_one({"id": str(after.id) })


                


    