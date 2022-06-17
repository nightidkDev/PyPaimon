import datetime
from discord.ext.commands.cooldowns import BucketType
import pymongo
import os
import discord
from discord.ext import commands
import re
import time
import random
import sys
import string
import json
sys.path.append("../../")
import config 
from plugins import funcb
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

usersdb = db.prof_ec_users
users = db.prof_ec_users
clans_db = db.clans

def money_kkk(number):

    str_m = "{:,}".format(number)
    return str_m.replace(",", ".")

def toFixed(numObj, digits=0):
    return float(f"{numObj:.{digits}f}")

def declension(forms, val):
    cases = [ 2, 0, 1, 1, 1, 2 ]
    if val % 100 > 4 and val % 100 < 20:
        return forms[2]
    else:
        if val % 10 < 5:
            return forms[cases[val % 10]]
        else:
            return forms[cases[5]]

def check_number(value):
    try:
        value = int(value)
        return True
    except:
        return False

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
        return f"{h:d} {ht} {m:d} {mt} {s:d} {st}"
    elif seconds >= 60:
        return f"{m:d} {mt} {s:d} {st}"
    else:
        return f"{s:d} {st}"

def stengtime(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    #d, h = divmod(h, 24)

    if seconds >= 3600:
        return f"{h:d}h, {m:d}m"
    else:
        return f"{m:d}m"


def checkfornumber(value):
    try:
        value = int(value)
        return True
    except:
        return False

def money_kkk(number):

    str_m = "{:,}".format(int(number))
    return str_m.replace(",", " ")

class Clans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='guildinfo', aliases=['ginfo', 'gi'])
    async def ginfo(self, ctx, *messageArray):
        clans = db.clans
        title = " ".join(messageArray)
        if not title:
            e = discord.Embed(title=f"", description=f"Введите название группировки.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans.find_one({ "title": f"{title}" })
            if not clan_info:
                e = discord.Embed(title=f"", description=f"Группировка с названием \"{title}\" не найдена.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                idc = clan_info["id"]
                title = clan_info["title"]
                description = clan_info["description"]
                color = clan_info["color"]
                image = clan_info["image"]
                time_created = clan_info["time"] + 10800
                owner = clan_info["owner"]
                balance = clan_info["balance"]
                coowner = clan_info["coowner"]
                owner_user = ctx.guild.get_member(int(owner))
                if coowner:
                    coowner_user = ctx.guild.get_member(int(coowner))
                members = len(clan_info["members"])
                limitmembers = clan_info["limitmembers"]
                officers = clan_info["officers"]
                level = clan_info["lvl"]
                exp = clan_info["exp"]
                nexp = clan_info["nexp"]
                perks = clan_info["perks"]
                clan_role = perks["role"]
                booster = clan_info["booster"]
                if color == "":
                    color = discord.Colour(0x2F3136)
                else:
                    color = int(color)
                officers_list = ", ".join(f'{ctx.guild.get_member(int(officer))}' for officer in officers)
                e_dict = {
                    "title": f"[{'unknown' if level == 0 else level}] {title}",
                    "description": '**Пустое описание**' if description == '' else description,
                    "author": {
                        "name": "Группировка"
                    },
                    "color": 0,
                    'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                    "footer": {
                        "text": f"{ctx.author.name}",
                        "icon_url": f"{ctx.author.avatar_url}"
                    },
                    "image": {
                        "url": image
                    },
                    "fields": [
                            {
                            "name": "Владельцы",
                            "value": f"```{owner_user}{f', {coowner_user}' if coowner else ''}```",
                            "inline": True
                        },
                        {
                            "name": "Баланс",
                            "value": f"```{'unlimited' if str(idc) == '1' else balance}```",
                            "inline": True
                        },
                        {
                            "name": "Количество участников",
                            "value": f"```{members}/{limitmembers}```",
                            "inline": True
                        },
                        {
                            "name": "Опыт",
                            "value": f"{funcb.expbarclan(self.bot, exp, nexp)}\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{f'**{exp}/{nexp} ({toFixed(exp / nexp * 100, 2)}%)**' if level != 10 else '⠀⠀⠀⠀**MAXIMUM**'}",
                            "inline": False
                        },
                        {
                            "name": "Дата создания",
                            "value": f"```{datetime.datetime.utcfromtimestamp(time_created).strftime('%d.%m.%Y %H:%M:%S')}```",
                            "inline": True
                        },
                        {
                            "name": "Бустер группировки",
                            "value": f"```{booster}x```",
                            "inline": True
                        },
                        {
                            "name": "Офицеры",
                            "value": f"```{officers_list}```",
                            "inline": False
                        },
                        {
                            "name": "Роль группировки",
                            "value": f"```Не разблокирована.```" if clan_role["access"] == 0 else f"```Не куплена.```" if clan_role["buy"] == 0 else f"```Отсутствует.```" if clan_role["id"] == "" else f"<@&{clan_role['id']}>",
                            "inline": True
                        }
                    ]
                }
                e_obj = json.dumps(e_dict)
                e_dict = json.loads(e_obj)
                # e = discord.Embed(title=f"[{'unknown' if level == 0 else level}] {title}", description='**Пустое описание**' if description == '' else description, color=color)
                # e.set_author(name="Группировка")
                # if image != "":
                #     e.set_image(url=image)
                # e.add_field(name=f"{'Владельцы' if coowner else 'Владелец'}", value=f"```{owner_user}{f', {coowner_user}' if coowner else ''}```", inline=True)
                # e.add_field(name=f"Баланс", value=f"```{'unlimited' if idc == 1 else balance}```", inline=True)
                # e.add_field(name=f"Количество участников", value=f"```{members}/{limitmembers}```", inline=True)
                # e.add_field(name="Опыт", value=f"{funcb.expbarclan(self.bot, exp, nexp)}\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{f'**{exp}/{nexp} ({toFixed(exp / nexp * 100, 2)}%)**' if level != 10 else '⠀⠀⠀⠀**MAXIMUM**'}", inline=False)
                # e.add_field(name=f"Дата создания", value=f"```{datetime.datetime.utcfromtimestamp(time_created).strftime('%d.%m.%Y %H:%M:%S')}```", inline=True)
                # e.add_field(name="Бустер группировки", value=f"```{booster}x```", inline=True)
                # officers_list = ", ".join(f'{ctx.guild.get_member(int(officer))}' for officer in officers)
                # if officers_list == "":
                #     officers_list = "Отсутствуют."
                # e.add_field(name=f"Офицеры", value=f"```{officers_list}```", inline=False)
                # #e.add_field(name=f"`Информация`", value=f"```Лимит в день: {limit_money}\nБуст денег: {boost_money}x\nБуст опыта: {boost_exp}x\nБуст ежедневной награды: {timely_bonus}x```", inline=False)
                # if clan_role["access"] == 0:
                #     e.add_field(name=f"Роль группировки", value=f"```Не разблокирована.```", inline=False)
                # elif clan_role["buy"] == 0:
                #     e.add_field(name=f"Роль группировки", value=f"```Не куплена.```", inline=False)
                # elif clan_role["id"] == "":
                #     e.add_field(name=f"Роль группировки", value=f"```Отсутствует.```", inline=False)
                # else:
                #     e.add_field(name=f"Роль группировки", value=f"<@&{clan_role['id']}>", inline=False)
                # e.timestamp = datetime.datetime.utcnow()
                # e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                e_dict["description"] = e_dict["description"].replace("\\n", "\n")
                e = discord.Embed.from_dict(e_dict)
                await ctx.channel.send(embed=e)

    @commands.group(name="guild", aliases=['g'], invoke_without_command=True)
    async def guild_command(self, ctx):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            description = clan_info["description"]
            color = clan_info["color"]
            image = clan_info["image"]
            time_created = clan_info["time"] + 10800
            owner = clan_info["owner"]
            coowner = clan_info["coowner"]
            balance = clan_info["balance"]
            owner_user = ctx.guild.get_member(int(owner))
            if coowner:
                coowner_user = ctx.guild.get_member(int(coowner))
            members = len(clan_info["members"])
            limitmembers = clan_info["limitmembers"]
            officers = clan_info["officers"]
            #boost_money = clan_info["bmoney"]
            #boost_exp = clan_info["bexp"]
            level = clan_info["lvl"]
            exp = clan_info["exp"]
            nexp = clan_info["nexp"]
            perks = clan_info["perks"]
            clan_role = perks["role"]
            booster = clan_info["booster"]
            #clan_role = clan_info["role"]
            #limit_money = clan_info["limit_money"]
            #timely_bonus = clan_info["btimely"]
            if color == "":
                color = discord.Colour(0x2F3136)
            else:
                color = int(color)
            officers_list = ", ".join(f'{ctx.guild.get_member(int(officer))}' for officer in officers)
            e_dict = {
                "title": f"[{'unknown' if level == 0 else level}] {title}",
                "description": '**Пустое описание**' if description == '' else description,
                "author": {
                    "name": "Группировка"
                },
                "color": 0,
                'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                "footer": {
                    "text": f"{ctx.author.name}",
                    "icon_url": f"{ctx.author.avatar_url}"
                },
                "image": {
                    "url": image
                },
                "fields": [
                        {
                        "name": "Владельцы",
                        "value": f"```{owner_user}{f', {coowner_user}' if coowner else ''}```",
                        "inline": True
                    },
                    {
                        "name": "Баланс",
                        "value": f"```{'unlimited' if clan == '1' else balance}```",
                        "inline": True
                    },
                    {
                        "name": "Количество участников",
                        "value": f"```{members}/{limitmembers}```",
                        "inline": True
                    },
                    {
                        "name": "Опыт",
                        "value": f"{funcb.expbarclan(self.bot, exp, nexp)}\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{f'**{exp}/{nexp} ({toFixed(exp / nexp * 100, 2)}%)**' if level != 10 else '⠀⠀⠀⠀**MAXIMUM**'}",
                        "inline": False
                    },
                    {
                        "name": "Дата создания",
                        "value": f"```{datetime.datetime.utcfromtimestamp(time_created).strftime('%d.%m.%Y %H:%M:%S')}```",
                        "inline": True
                    },
                    {
                        "name": "Бустер группировки",
                        "value": f"```{booster}x```",
                        "inline": True
                    },
                    {
                        "name": "Офицеры",
                        "value": f"```{officers_list}```",
                        "inline": False
                    },
                    {
                        "name": "Роль группировки",
                        "value": f"```Не разблокирована.```" if clan_role["access"] == 0 else f"```Не куплена.```" if clan_role["buy"] == 0 else f"```Отсутствует.```" if clan_role["id"] == "" else f"<@&{clan_role['id']}>",
                        "inline": True
                    }
                ]
            }
            e_obj = json.dumps(e_dict)
            e_dict = json.loads(e_obj)
            # e = discord.Embed(title=f"[{'unknown' if level == 0 else level}] {title}", description=f"{'**Пустое описание**' if description == '' else f'{description}'}", color=color)
            # e.set_author(name="Группировка")
            # if image != "":
            #     e.set_image(url=image)
            # e.add_field(name=f"{'Владельцы' if coowner else 'Владелец'}", value=f"```{owner_user}{f', {coowner_user}' if coowner else ''}```", inline=True)
            # e.add_field(name=f"Баланс", value=f"```{'unlimited' if clan == '1' else balance}```", inline=True)
            # e.add_field(name=f"Количество участников", value=f"```{members}/{limitmembers}```", inline=True)
            # e.add_field(name="Опыт", value=f"{funcb.expbarclan(self.bot, exp, nexp)}\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{f'**{exp}/{nexp} ({toFixed(exp / nexp * 100, 2)}%)**' if level != 10 else '⠀⠀⠀⠀**MAXIMUM**'}", inline=False)
            # e.add_field(name=f"Дата создания", value=f"```{datetime.datetime.utcfromtimestamp(time_created).strftime('%d.%m.%Y %H:%M:%S')}```", inline=True)
            # e.add_field(name="Бустер группировки", value=f"```{booster}x```", inline=True)
            
            # if officers_list == "":
            #     officers_list = "Отсутствуют."
            # e.add_field(name=f"Офицеры", value=f"```{officers_list}```", inline=False)
            # if clan_role["access"] == 0:
            #     e.add_field(name=f"Роль группировки", value=f"```Не разблокирована.```", inline=False)
            # elif clan_role["buy"] == 0:
            #     e.add_field(name=f"Роль группировки", value=f"```Не куплена.```", inline=False)
            # elif clan_role["id"] == "":
            #     e.add_field(name=f"Роль группировки", value=f"```Отсутствует.```", inline=False)
            # else:
            #     e.add_field(name=f"Роль группировки", value=f"<@&{clan_role['id']}>", inline=False)
            # e.timestamp = datetime.datetime.utcnow()
            # e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            e_dict["description"] = e_dict["description"].replace("\\n", "\n")
            e = discord.Embed.from_dict(e_dict)
            await ctx.channel.send(embed=e)
     
    @guild_command.command(name="invite", aliases=["i"])
    async def guild_invite(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = clan_info["owner"]
            owner_user = ctx.guild.get_member(int(owner))
            coowner = clan_info["coowner"]
            if coowner:
                coowner_user = ctx.guild.get_member(int(coowner))
            else:
                coowner_user = None
            officers = clan_info["officers"]
            members = len(clan_info["members"])
            limitmembers = clan_info["limitmembers"]
            officer_torf = False
            for officer in officers:
                user1 = ctx.guild.get_member(int(officer))
                if not user1:
                    continue
                if user1.id == ctx.author.id:
                    officer_torf = True
                    break
            if officer_torf == False and owner_user != ctx.author and coowner_user != ctx.author:
                e = discord.Embed(title=f"", description=f"Недостаточно прав.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                if members >= limitmembers:
                    e = discord.Embed(title=f"", description=f"Достигнут лимит пользователей в группировке.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                elif len(ctx.message.mentions) == 0:
                    e = discord.Embed(title=f"", description=f"Укажите пользователя.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    muser = users.find_one({ "disid": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })
                    if muser["clan"] != "":
                        e = discord.Embed(title=f"", description=f"Данный пользователь уже состоит в группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    else:
                        reactions = db.reactions
                        e = discord.Embed(title=f"Приглашение в группировку", description=f"<@!{ctx.message.mentions[0].id}>, тебя приглашают в группировку \"{title}\". Что предпримешь?", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        message_s = await ctx.channel.send(embed=e)
                        await message_s.add_reaction("✅")
                        await message_s.add_reaction("❌")
                        reactions.insert_one({"message_id": str(message_s.id), "inviter": str(ctx.author.id), "invited": str(ctx.message.mentions[0].id), "time": int(time.time()) + 30, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "invite_clan", "clan": clan })
            
    @guild_command.command(name="kick", aliases=["k"])
    async def guild_kick(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = clan_info["owner"]
            owner_user = ctx.guild.get_member(int(owner))
            coowner = clan_info["coowner"]
            members = clan_info["members"]
            if coowner:
                coowner_user = ctx.guild.get_member(int(coowner))
            else:
                coowner_user = None
            #officers = clan_info["officers"]
            #officer_torf = False
            #for officer in officers:
            #    user1 = ctx.guild.get_member(int(officer))
            #    if not user1:
            #        continue
            #    if user1.id == ctx.author.id:
            #        officer_torf = True
            #        break
            if str(ctx.author.id) not in clan_info["officers"] and owner_user != ctx.author and coowner_user != ctx.author:
                e = discord.Embed(title=f"", description=f"Недостаточно прав.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                if len(ctx.message.mentions) == 0 and len(messageArray) <= 0:
                    e = discord.Embed(title=f"", description=f"Укажите пользователя.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    user = None
                    if len(ctx.message.mentions) != 0:
                        user = ctx.message.mentions[0].id
                    else:
                        try:
                            idu = int(messageArray[0])
                        except:
                            e = discord.Embed(title=f"", description=f"Пользователь не найден.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            return await ctx.channel.send(embed=e)
                        if ctx.guild.get_member(idu):
                            user = ctx.guild.get_member(idu).id
                        elif messageArray[0] in members:
                            user = idu
                        else:
                            e = discord.Embed(title=f"", description=f"Пользователь не найден.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            return await ctx.channel.send(embed=e)
                    muser = users.find_one({ "disid": str(user), "guild": str(ctx.guild.id) })
                    if str(muser["clan"]) != str(clan):
                        e = discord.Embed(title=f"", description=f"Данный пользователь уже не состоит в данной группировке.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    else:
                        #officer_torf2 = False
                        #for officer in officers:
                        #    if int(officer) == user:
                        #        officer_torf2 = True
                        #        break
                        # if ctx.author
                        coowneru = coowner_user.id if coowner_user else None
                        if ctx.author.id == user:
                            e = discord.Embed(title=f"", description=f"Нельзя исключить себя из группировки.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
                        elif owner_user.id == int(user) or coowneru == int(user):
                            e = discord.Embed(title=f"", description=f"Недостаточно прав.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
                        elif str(user) in clan_info["officers"] and (ctx.author.id != owner_user and ctx.author != coowner_user):
                            e = discord.Embed(title=f"", description=f"Недостаточно прав.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
                        else:
                            clans_db.update_one({ "id": int(clan) }, { "$pull": { "members": str(user) } })
                            #officers = clan_info["officers"]
                            #officer_torf2 = False
                            #for officer in officers:
                            #    if int(officer) == user:
                            #        officer_torf2 = True
                            #        break
                            if str(user) in clan_info["officers"]:
                                clans_db.update_one({ 'id': int(clan) }, { "$pull": { "officers": f"{user}" } })
                            users.update_one({ "disid": str(user), "guild": str(ctx.guild.id) }, { "$set": { "clan": "", "depositInClan": 0 } })
                            perks = clan_info["perks"]
                            if perks["role"]["id"] != "" and ctx.guild.get_member(int(user)):
                                clan_role = ctx.guild.get_role(int(perks["role"]["id"]))
                                user_mention = ctx.guild.get_member(int(user))
                                await user_mention.remove_roles(clan_role)
                            e = discord.Embed(title=f"", description=f"<@!{user}> был кикнут из группировки.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)

    @guild_command.command(name="promote", aliases=['p'])
    async def guild_promote(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            lvl = clan_info["lvl"]
            owner = clan_info["owner"]
            owner_user = ctx.guild.get_member(int(owner))
            coowner = clan_info["coowner"]
            if coowner:
                coowner_user = ctx.guild.get_member(int(coowner))
            else:
                coowner_user = None
            officers = clan_info["officers"]
            if owner_user != ctx.author and coowner_user != ctx.author:
                e = discord.Embed(title=f"", description=f"Недостаточно прав.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                if len(ctx.message.mentions) == 0:
                    e = discord.Embed(title=f"", description=f"Укажите пользователя.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    # muser = users.find_one({ "disid": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })
                    if str(ctx.message.mentions[0].id) in officers:
                        e = discord.Embed(title=f"", description=f"Данный пользователь уже находится в рядах офицеров.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    else:
                        if len(officers) >= 3:
                            e = discord.Embed(title=f"", description=f"Достигнуто максимальное количество офицеров.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            return await ctx.channel.send(embed=e)
                        clans_db.update_one({ "id": int(clan) }, { "$push": { "officers": str(ctx.message.mentions[0].id) } })
                        e = discord.Embed(title=f"", description=f"<@!{ctx.message.mentions[0].id}> получил повышение!", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                        if lvl == 10:
                            lvl10 = ctx.guild.get_role(841429598176804914)
                            await ctx.message.mentions[0].add_roles(lvl10)

    @guild_command.command(name="demote")
    async def guild_demote(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            lvl = clan_info["lvl"]
            owner = clan_info["owner"]
            owner_user = ctx.guild.get_member(int(owner))
            coowner = clan_info["coowner"]
            if coowner:
                coowner_user = ctx.guild.get_member(int(coowner))
            else:
                coowner_user = None
            officers = clan_info["officers"]
            if owner_user != ctx.author and coowner_user != ctx.author:
                e = discord.Embed(title=f"", description=f"Недостаточно прав.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                if len(ctx.message.mentions) == 0:
                    e = discord.Embed(title=f"", description=f"Укажите пользователя.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    # muser = users.find_one({ "disid": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })
                    if str(ctx.message.mentions[0].id) not in officers:
                        e = discord.Embed(title=f"", description=f"Данный пользователь уже не находится в рядах офицеров.", color=discord.Colour(0x2F3136))
                        await ctx.channel.send(embed=e)
                    else:
                        clans_db.update_one({ "id": int(clan) }, { "$pull": { "officers": str(ctx.message.mentions[0].id) } })
                        e = discord.Embed(title=f"", description=f"<@!{ctx.message.mentions[0].id}> был понижен в звании.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                        if lvl == 10:
                            lvl10 = ctx.guild.get_role(841429598176804914)
                            await ctx.message.mentions[0].remove_roles(lvl10)

    @guild_command.command(name="up")
    async def guild_up(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = clan_info["owner"]
            balance = clan_info["balance"]
            exp = clan_info["exp"]
            nexp = clan_info["nexp"]
            level = clan_info["lvl"]
            limitmembers = clan_info["limitmembers"]
            perks = clan_info["perks"]
            owner_user = ctx.guild.get_member(int(owner))
            coowner = clan_info["coowner"]
            officers = clan_info["officers"]
            if coowner:
                coowner_user = ctx.guild.get_member(int(coowner))
            else:
                coowner_user = None
            if owner_user != ctx.author and coowner_user != ctx.author:
                e = discord.Embed(title=f"", description=f"Недостаточно прав.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                if level == 10:
                    e = discord.Embed(title=f"", description=f"Получен и так максимальный уровень группировок.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url) 
                    return await ctx.channel.send(embed=e)
                if exp - nexp < 0:
                    e = discord.Embed(title=f"", description=f"Недостаточно опыта, чтобы повысить уровень группировки.\nНадо еще: {nexp - exp}", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    return await ctx.channel.send(embed=e)
                if balance - (config.clancostup * (level + 1)) < 0:
                    e = discord.Embed(title=f"", description=f"Недостаточно примогемов на балансе группировки, чтобы повысить уровень группировки.\nНадо еще: {(config.clancostup * (level + 1)) - balance}", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    return await ctx.channel.send(embed=e)
                if level + 1 <= 5:
                    clans_db.update_one({ "id": int(clan) }, { "$inc": { "lvl": 1, "limitmembers": 5, "nexp": 200000, "exp": -(nexp), "balance": -(config.clancostup * (level + 1)) } })
                elif level + 1 == 10:
                    clans_db.update_one({ "id": int(clan) }, { "$inc": { "lvl": 1, "balance": -(config.clancostup * (level + 1)) } })
                else:
                    clans_db.update_one({ "id": int(clan) }, { "$inc": { "lvl": 1, "nexp": 200000, "exp": -(nexp), "balance": -(config.clancostup * (level + 1)) } })
                updates = []
                if level + 1 == 2:
                    perks["interface"]["access"] = 1
                    clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks } })
                    updates.append("Открыта возможность менять картинку и цвет группировки.")
                if level + 1 == 3:
                    perks["role"]["access"] = 1
                    clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks } })
                    updates.append("Открыта покупка роли группировки.")
                if level + 1 == 5:
                    perks["spots"]["access"] = 1
                    clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks } })
                    primo = self.bot.get_emoji(config.MONEY_EMOJI)
                    updates.append(f"Открыта возможность купить место группировки за 50.000{primo}\n\nКоманда `.g spot [кол-во]`")
                if level + 1 == 6:
                    perks["room"]["access"] = 1
                    clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks } })
                    updates.append("Открыта покупка войс комнаты группировки.")
                if level + 1 == 7:
                    perks["boost24h"]["access"] = 1
                    clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks } })
                    updates.append("Открыта покупка дополнительных примогемов для группировки.")
                if level + 1 == 9:
                    perks["chat"]["access"] = 1
                    clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks } })
                    updates.append("Открыта покупка чат канала с капчей для группировки.")
                if level + 1 == 10:
                    lvl10 = ctx.guild.get_role(841429598176804914)
                    for x in officers:
                        user = ctx.guild.get_member(int(x))
                        await user.add_roles(lvl10)
                    await owner_user.add_roles(lvl10)
                    if coowner:
                        await coowner_user.add_roles(lvl10)
                    updates.append("Достигнут максимальный уровень группировки, поэтому владельцу и офицерам была выдана роль, позволяющая участвовать в собраниях сервера.")
                if level + 1 == 4 or level + 1 == 6 or level + 1 == 8:
                    booster = clan_info["booster"]
                    clans_db.update_one({ "id": int(clan) }, { "$inc": { "booster": 1 } })
                    updates.append(f"Обновлен общий бустер группировки до {booster + 1}.")
                upd = "\n"
                upd += "\n".join(f"{i + 1}. {updates[i]}" for i in range(len(updates)))
                e = discord.Embed(title=f"", description=f"Уровень группировки успешно поднят до {level + 1}!\n\n{f'Открыто: {upd}' if len(updates) != 0 else ''}", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)


    @guild_command.command(name="spot")
    async def guild_spot(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = clan_info["owner"]
            balance = clan_info["balance"]
            perks = clan_info["perks"]
            owner_user = ctx.guild.get_member(int(owner))
            coowner = clan_info["coowner"]
            if coowner:
                coowner_user = ctx.guild.get_member(int(coowner))
            else:
                coowner_user = None
            if owner_user != ctx.author and coowner_user != ctx.author:
                e = discord.Embed(title=f"", description=f"Недостаточно прав.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            elif perks["spots"]["access"] == 0:
                e = discord.Embed(title=f"", description=f"Покупка дополнительных слотов открывается на 5 уровне.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            elif len(messageArray) <= 0:
                e = discord.Embed(title=f"", description=f"Укажите количество слотов, которые хочешь купить.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            elif checkfornumber(messageArray[0]) is False:
                e = discord.Embed(title=f"", description=f"Укажите количество слотов, которые хочешь купить.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                spots = int(messageArray[0])
                if spots <= 0:
                    e = discord.Embed(title=f"", description=f"Невозможно купить `{spots}` {declension([ 'слот', 'слота', 'слотов' ], abs(spots))}.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                elif clan_info['limitmembers'] >= 100 or clan_info['limitmembers'] + spots > 100:
                    e = discord.Embed(title=f"", description=f"Невозможно купить `{spots}` {declension([ 'слот', 'слота', 'слотов' ], abs(spots))}, так как достигнут максимальный лимит в 130 участников.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    primo = self.bot.get_emoji(config.MONEY_EMOJI)
                    cost = spots * 50000
                    if balance < cost:
                        primo = self.bot.get_emoji(config.MONEY_EMOJI)
                        e = discord.Embed(title=f"", description=f"Недостаточно примогемов на балансе группировки. Цена: {money_kkk(cost)}{primo}", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    else:
                        reactions = db.reactions
                        e = discord.Embed(title=f"", description=f"Вы уверены, что хотите купить {declension([ 'дополнительный', 'дополнительные', 'дополнительных' ], spots)} {spots} {declension([ 'слот', 'слота', 'слотов' ], spots)} участников за {money_kkk(cost)}{primo}?", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name="Покупка дополнительных мест")
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        message_s = await ctx.channel.send(embed=e)
                        await message_s.add_reaction("✅")
                        await message_s.add_reaction("❌")
                        reactions.insert_one({"message_id": str(message_s.id), "author": str(ctx.author.id), "time": int(time.time()) + 20, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "spots_clan", "clan": clan, "spots": spots, "cost": cost })

    @guild_command.command(name="description")
    async def guild_description(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = clan_info["owner"]
            description = clan_info["description"]
            owner_user = ctx.guild.get_member(int(owner))
            coowner = clan_info["coowner"]
            if coowner:
                coowner_user = ctx.guild.get_member(int(coowner))
            else:
                coowner_user = None
            if owner_user != ctx.author and coowner_user != ctx.author:
                e = discord.Embed(title=f"", description=f"Недостаточно прав.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                e = discord.Embed(color=discord.Colour(0x2F3136))
                set_status = " ".join(messageArray)
                if set_status != "":
                    if len(set_status) > 1000:
                        e.description = f"Укажите описание группировки менее 1000 символов."
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        return await ctx.channel.send(embed=e)
                    clans_db.update_one({ "id": int(clan) }, { "$set": { "description": set_status } })
                    e.description = f"Описание группировки установлено."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    clans_db.update_one({ "id": int(clan) }, { "$set": { "description": "" } })
                    e.description = f"Описание группировки очищено."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)


    @guild_command.command(name="members")
    @commands.cooldown(1, 15, BucketType.user)
    async def guild_members(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info['title']
            members = clan_info['members']
            if len(members) <= 40:
                membersstr = ""
                membersstr2 = ""
                for i in range(len(members)):
                    user = ctx.guild.get_member(int(members[i]))
                    if user:
                        userdb = users.find_one({ "disid": f"{user.id}", "guild": f'{ctx.guild.id}' })
                        try:
                            alldeposclan = userdb["depositInClan"]
                        except:
                            alldeposclan = 0
                        stats_chat, stats_voice, deposclan = userdb["s_chat"], userdb["s_voice"], alldeposclan
                    else:
                        stats_chat, stats_voice, deposclan = None, None, None
                    username = str(user).replace(u'\u005C', u'\u005C\u005C').replace("`", "\`").replace('*', "\*").replace('_', '\_')
                    primo = self.bot.get_emoji(config.MONEY_EMOJI)
                    members[i] = f'{members[i]} (leaved)' if user is None else f'{username} - `{stats_chat}m` - `{stengtime(stats_voice)}` - {deposclan}{primo}'
                    entermember = f"{i + 1}. {members[i]}\n"
                    if len(membersstr) + len(entermember) <= 4096:
                        membersstr += entermember
                    else:
                        membersstr2 += entermember
                #membersstr = "\n".join(f"{i + 1}. {members[i]}" for i in range(len(members)))
                
                if membersstr2 == "":
                    e = discord.Embed(title=f"Участники группировки {title}", description=f"{membersstr}", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    e = discord.Embed(title=f"Участники группировки {title}", description=f"{membersstr}", color=discord.Colour(0x2F3136))
                    e2 = discord.Embed(title=f"", description=f"{membersstr2}", color=discord.Colour(0x2F3136))
                    e2.timestamp = datetime.datetime.utcnow()
                    e2.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                    await ctx.channel.send(embed=e2)
            else:
                temp_name = funcb.gen_promo(1, 12)

                f = open(file=f"./temp/{temp_name}.txt", mode='w', encoding="utf-8")

                i = 1
                entermember = "Из-за большого количества людей в клане бот выдает информацию в файле.\n\n"

                for i in range(len(members)):
                    user = ctx.guild.get_member(int(members[i]))
                    if user:
                        userdb = users.find_one({ "disid": f"{user.id}", "guild": f'{ctx.guild.id}' })
                        try:
                            alldeposclan = userdb["depositInClan"]
                        except:
                            alldeposclan = 0
                        stats_chat, stats_voice, deposclan = userdb["s_chat"], userdb["s_voice"], alldeposclan
                    else:
                        stats_chat, stats_voice, deposclan = None, None, None
                    username = str(user)#.replace(u'\u005C', u'\u005C\u005C').replace("`", "\`").replace('*', "\*").replace('_', '\_')
                    members[i] = f'{members[i]} (leaved)' if user is None else f'{username} ({members[i]}) - {stats_chat}m - {stengtime(stats_voice)} - {deposclan} примогемов.'
                    entermember += f"{i + 1}. {members[i]}\n"

                # with open(temp_name, "w") as f:
                f.write(entermember)
                f.close()

                file = discord.File(f"./temp/{temp_name}.txt", filename=f"{temp_name}.txt")

                await ctx.send(content=f"Запрос от {ctx.author.mention} об информация об участниках клана **{title}**", file=file)

                os.remove(f"./temp/{temp_name}.txt")

    @guild_command.command(name="smembers")
    async def guild_smembers(self, ctx, *messageArray):
        if str(ctx.author.id) not in config.ADMINS:
            return
        clans = db.clans
        title = " ".join(messageArray)
        if not title:
            e = discord.Embed(title=f"", description=f"Введите название группировки.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans.find_one({ "title": f"{title}" })
            if not clan_info:
                e = discord.Embed(title=f"", description=f"Группировка с названием \"{title}\" не найдена.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                title = clan_info['title']
                members = clan_info['members']
                if len(members) <= 40:
                    membersstr = ""
                    membersstr2 = ""
                    for i in range(len(members)):
                        user = ctx.guild.get_member(int(members[i]))
                        if user:
                            userdb = users.find_one({ "disid": f"{user.id}", "guild": f'{ctx.guild.id}' })
                            try:
                                alldeposclan = userdb["depositInClan"]
                            except:
                                alldeposclan = 0
                            stats_chat, stats_voice, deposclan = userdb["s_chat"], userdb["s_voice"], alldeposclan
                        else:
                            stats_chat, stats_voice, deposclan = None, None, None
                        username = str(user).replace(u'\u005C', u'\u005C\u005C').replace("`", "\`").replace('*', "\*").replace('_', '\_')
                        primo = self.bot.get_emoji(config.MONEY_EMOJI)
                        members[i] = f'{members[i]} (leaved)' if user is None else f'{username} - `{stats_chat}m` - `{stengtime(stats_voice)}` - {deposclan}{primo}'
                        entermember = f"{i + 1}. {members[i]}\n"
                        if len(membersstr) + len(entermember) <= 4096:
                            membersstr += entermember
                        else:
                            membersstr2 += entermember
                    
                    if membersstr2 == "":
                        e = discord.Embed(title=f"Участники группировки {title}", description=f"{membersstr}", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    else:
                        e = discord.Embed(title=f"Участники группировки {title}", description=f"{membersstr}", color=discord.Colour(0x2F3136))
                        e2 = discord.Embed(title=f"", description=f"{membersstr2}", color=discord.Colour(0x2F3136))
                        e2.timestamp = datetime.datetime.utcnow()
                        e2.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                        await ctx.channel.send(embed=e2)
                else:
                    temp_name = funcb.gen_promo(1, 12)

                    f = open(file=f"./temp/{temp_name}.txt", mode='w', encoding="utf-8")

                    i = 1
                    entermember = "Из-за большого количества людей в клане бот выдает информацию в файле.\n\n"

                    for i in range(len(members)):
                        user = ctx.guild.get_member(int(members[i]))
                        if user:
                            userdb = users.find_one({ "disid": f"{user.id}", "guild": f'{ctx.guild.id}' })
                            try:
                                alldeposclan = userdb["depositInClan"]
                            except:
                                alldeposclan = 0
                            stats_chat, stats_voice, deposclan = userdb["s_chat"], userdb["s_voice"], alldeposclan
                        else:
                            stats_chat, stats_voice, deposclan = None, None, None
                        username = str(user)#.replace(u'\u005C', u'\u005C\u005C').replace("`", "\`").replace('*', "\*").replace('_', '\_')
                        members[i] = f'{members[i]} (leaved)' if user is None else f'{username} ({members[i]}) - {stats_chat}m - {stengtime(stats_voice)} - {deposclan} примогемов.'
                        entermember += f"{i + 1}. {members[i]}\n"

                    # with open(temp_name, "w") as f:
                    f.write(entermember)
                    f.close()

                    file = discord.File(f"./temp/{temp_name}.txt", filename=f"{temp_name}.txt")

                    await ctx.send(content=f"Запрос от {ctx.author.mention} об информация об участниках клана **{title}**", file=file)

                    os.remove(f"./temp/{temp_name}.txt")
    @guild_command.command(name="deposit", aliases=['d'])
    async def guild_deposit(self, ctx, *messageArray):
        #print(messageArray[0])
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan == "":
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            #if ctx.author.id == 518427777523908608:
            #    await ctx.author.send("Вам запрещено использовать эту команду.")
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info['title']
            balance = clan_info['balance']
            if len(messageArray) < 1:
                e = discord.Embed(title=f"", description=f"Укажите сумму депозита в группировку.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            cost = messageArray[0]
            try:
                cost = int(cost)
            except:
                e = discord.Embed(title=f"", description=f"Укажите сумму для взноса депозита в группировку.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)

            if cost <= 0:
                e = discord.Embed(title=f"", description=f"Укажите сумму для взноса депозита в группировку.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            userdbx = users.find_one({ "disid": f"{ctx.author.id}", "guild": f"{ctx.guild.id}" })
            money = userdbx["money"]
            if money < cost:
                e = discord.Embed(title=f"", description=f"Недостаточно примогемов.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            primo = self.bot.get_emoji(config.MONEY_EMOJI)
            clans_db.update_one({ "id": int(clan) }, { "$inc": { "balance": cost } })
            users.update_one({ "disid": f"{ctx.author.id}", "guild": f"{ctx.guild.id}" }, { "$inc": { "money": -(cost) } })
            try:
                alldeposclan = userdbx["depositInClan"] + cost
            except:
                alldeposclan = cost
            
            users.update_one({ "disid": f"{ctx.author.id}", "guild": f"{ctx.guild.id}" }, { "$set": { "depositInClan": alldeposclan } })
            
            e = discord.Embed(title=f"", description=f"Внесено {cost}{primo} в группировку.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)

    @guild_command.command(name="create")
    async def guild_create(self, ctx, *messageArray):
        users = db.prof_ec_users
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if clan:
            e = discord.Embed(title=f"", description=f"Ты уже находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            primo = self.bot.get_emoji(config.MONEY_EMOJI)
            users = db.prof_ec_users
            user = users.find_one({ "disid": f"{ctx.author.id}", "guild": f"{ctx.guild.id}" })
            if user["money"] < config.clancostup:
                e = discord.Embed(title=f"", description=f"Недостаточно примогемов. Цена: {config.clancostup}{primo}", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            if len(messageArray) <= 0:
                e = discord.Embed(title=f"", description=f"Укажите название группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e) 
            clan_name = " ".join(messageArray)
            rus = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
            for x in list(clan_name):
                if x not in string.printable and x not in rus:
                    e = discord.Embed(title=f"", description=f"В названии присутствует недопустимый символ \"{x}\".", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    return await ctx.channel.send(embed=e)
            if len(clan_name) > 15:
                e = discord.Embed(title=f"", description=f"Укажите название короче 15 символов.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            elif clans_db.count_documents({ "title": clan_name }) != 0:
                    e = discord.Embed(title=f"", description=f"Группировка с таким названием уже существует.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
            else:
                reactions = db.reactions
                e = discord.Embed(title=f"Создание группировки", description=f"Ты точно хочешь создать группировку **{clan_name}**?", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                message_s = await ctx.channel.send(embed=e)
                await message_s.add_reaction("✅")
                await message_s.add_reaction("❌")
                reactions.insert_one({"message_id": str(message_s.id), "owner_clan": str(ctx.author.id), "time": int(time.time()) + 15, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "create_clan", "name_clan": clan_name })
                    
    @guild_command.command(name="transfer")
    async def guild_transfer(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if not clan:
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = ctx.guild.get_member(int(clan_info["owner"]))
            
            if ctx.author != owner:
                e = discord.Embed(title=f"", description=f"Ты не владелец группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            elif len(ctx.message.mentions) == 0:
                e = discord.Embed(title=f"", description=f"Укажи пользователя, которому ты хочешь передать права владельца группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            elif ctx.message.mentions[0] == owner:
                e = discord.Embed(title=f"", description=f"Ты не можешь передать права владельца в группировке самому себе.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                reactions = db.reactions
                e = discord.Embed(title=f"Передача прав группировки", description=f"Вы уверены, что хотите передать права владельца группировки <@!{ctx.message.mentions[0].id}>?", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                message_s = await ctx.channel.send(embed=e)
                await message_s.add_reaction("✅")
                await message_s.add_reaction("❌")
                reactions.insert_one({"message_id": str(message_s.id), "author": str(ctx.author.id), "transfer": str(ctx.message.mentions[0].id), "time": int(time.time()) + 30, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "transfer_clan", "clan": clan, "title": title })
            
    @guild_command.command(name="disband")
    async def guild_disband(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if not clan:
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = ctx.guild.get_member(int(clan_info["owner"]))
            
            if ctx.author != owner:
                e = discord.Embed(title=f"", description=f"Ты не владелец группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                reactions = db.reactions
                e = discord.Embed(title=f"Удаление группировки", description=f"Вы уверены, что хотите удалить группировку **\"{title}\"**?", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                message_s = await ctx.channel.send(embed=e)
                await message_s.add_reaction("✅")
                await message_s.add_reaction("❌")
                reactions.insert_one({"message_id": str(message_s.id), "author": str(ctx.author.id), "time": int(time.time()) + 30, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "delete_clan", "clan": clan, "title": title })
    
    @guild_command.command(name="leave")
    async def guild_leave(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if not clan:
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = ctx.guild.get_member(int(clan_info["owner"]))
            
            if ctx.author == owner:
                e = discord.Embed(title=f"", description=f"Ты владелец группировки.\n\nДля удаления группировки пропиши: `.g disband`", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                reactions = db.reactions
                e = discord.Embed(title=f"Выход из группировки", description=f"Вы уверены, что хотите покинуть группировку **\"{title}\"**?", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                message_s = await ctx.channel.send(embed=e)
                await message_s.add_reaction("✅")
                await message_s.add_reaction("❌")
                reactions.insert_one({"message_id": str(message_s.id), "author": str(ctx.author.id), "time": int(time.time()) + 15, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "leave_clan", "clan": clan, "title": title })

    @guild_command.command(name="rename")
    async def guild_rename(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if not clan:
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = ctx.guild.get_member(int(clan_info["owner"]))
            
            if ctx.author != owner:
                e = discord.Embed(title=f"", description=f"Ты не владелец группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            elif clan_info["balance"] < 100000:
                primo = self.bot.get_emoji(config.MONEY_EMOJI)
                e = discord.Embed(title=f"", description=f"Недостаточно примогемов на балансе группировки. Цена: 100.000{primo}", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            elif len(messageArray) <= 0:
                e = discord.Embed(title=f"", description=f"Укажите новое название группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                newtitle = " ".join(messageArray)
                rus = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
                for x in list(newtitle):
                    if x not in string.printable and x not in rus:
                        e = discord.Embed(title=f"", description=f"В названии присутствует недопустимый символ \"{x}\".", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        return await ctx.channel.send(embed=e)
                if len(newtitle) > 15:
                    e = discord.Embed(title=f"", description=f"Укажите название короче 15 символов.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                elif clans_db.count_documents({ "title": newtitle }) != 0:
                    e = discord.Embed(title=f"", description=f"Группировка с таким названием уже существует.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    reactions = db.reactions
                    e = discord.Embed(title=f"Изменение названия группировки", description=f"Вы уверены, что хотите переименовать группировку **\"{title}\"** в **\"{newtitle}\"**?", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    message_s = await ctx.channel.send(embed=e)
                    await message_s.add_reaction("✅")
                    await message_s.add_reaction("❌")
                    reactions.insert_one({"message_id": str(message_s.id), "author": str(ctx.author.id), "time": int(time.time()) + 30, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "rename_clan", "clan": clan, "title": title, "newtitle": newtitle })
    
    @guild_command.command(name="shop")
    async def guild_shop(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if not clan:
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = ctx.guild.get_member(int(clan_info["owner"]))
            perks = clan_info["perks"]
            primo = self.bot.get_emoji(config.MONEY_EMOJI)
            listshop = f"""
1. Роль группировки: {'заблокировано. (3 уровень)' if perks['role']['access'] == 0 else f'{"приобретено." if perks["role"]["buy"] == 1 else f"500.000{primo}"}'}
2. Войс комната группировки: {'заблокировано. (6 уровень)' if perks['room']['access'] == 0 else f'{"приобретено." if perks["room"]["buy"] == 1 else f"500.000{primo}"}'}
3. Дополнительные примогемы: {'заблокировано. (7 уровень)' if perks['boost24h']['access'] == 0 else f'{"приобретено." if perks["boost24h"]["buy"] == 1 else f"250.000{primo}"}'}
4. Чат канал группировки с капчей: {'заблокировано. (9 уровень)' if perks['chat']['access'] == 0 else f'{"приобретено." if perks["chat"]["buy"] == 1 else f"500.000{primo}"}'}
"""
            e = discord.Embed(title=f"", description=listshop, color=discord.Colour(0x2F3136))
            e.set_author(name=f"Магазин группировки {title}")
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
            #elif messageArray[0] == "si" or messageArray[0] == "shopinfo":
            #    return
    @guild_command.command(name="buy")
    async def guild_buy(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if not clan:
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = ctx.guild.get_member(int(clan_info["owner"]))
            perks = clan_info["perks"]
            primo = self.bot.get_emoji(config.MONEY_EMOJI)
            if ctx.author != owner:
                e = discord.Embed(title=f"", description=f"Ты не владелец группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            if len(messageArray) <= 0:
                e = discord.Embed(title=f"", description=f"Укажите номер из магазина.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                if messageArray[0] == "1":
                    if perks['role']['access'] == 0:
                        e = discord.Embed(title=f"", description=f"У вас нет доступа к этой команде, сначала разблокируйте покупку роли на 3 уровне.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name=f"Магазин группировки {title}")
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    elif perks['role']['buy'] == 0:
                        if clan_info["balance"] < 500000:
                            primo = self.bot.get_emoji(config.MONEY_EMOJI)
                            e = discord.Embed(title=f"", description=f"Недостаточно примогемов на балансе группировки. Цена: 500.000{primo}", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
                        else:
                            reactions = db.reactions
                            e = discord.Embed(title=f"", description=f"Вы уверены, что хотите купить роль группировки?", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_author(name=f"Магазин группировки {title}")
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            message_s = await ctx.channel.send(embed=e)
                            await message_s.add_reaction("✅")
                            await message_s.add_reaction("❌")
                            reactions.insert_one({"message_id": str(message_s.id), "author": str(ctx.author.id), "time": int(time.time()) + 30, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "shop_clan", "clan": clan, "item": "role" })
                    else:
                        e = discord.Embed(title=f"", description=f"У вас уже куплена роль группировки, чтобы воспользоваться: `.g role [цвет]`.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name=f"Магазин группировки {title}")
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                elif messageArray[0] == "2":
                    if perks['room']['access'] == 0:
                        e = discord.Embed(title=f"", description=f"У вас нет доступа к этой команде, сначала разблокируйте покупку войс комнаты на 6 уровне.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name=f"Магазин группировки {title}")
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    elif perks['room']['buy'] == 0:
                        if clan_info["balance"] < 500000:
                            primo = self.bot.get_emoji(config.MONEY_EMOJI)
                            e = discord.Embed(title=f"", description=f"Недостаточно примогемов на балансе группировки. Цена: 500.000{primo}", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
                        else:
                            reactions = db.reactions
                            e = discord.Embed(title=f"", description=f"Вы уверены, что хотите купить войс комнату группировки?", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_author(name=f"Магазин группировки {title}")
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            message_s = await ctx.channel.send(embed=e)
                            await message_s.add_reaction("✅")
                            await message_s.add_reaction("❌")
                            reactions.insert_one({"message_id": str(message_s.id), "author": str(ctx.author.id), "time": int(time.time()) + 30, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "shop_clan", "clan": clan, "item": "voice_room" })
                    else:
                        e = discord.Embed(title=f"", description=f"У вас уже куплена войс комната группировки.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name=f"Магазин группировки {title}")
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                elif messageArray[0] == "3":
                    if perks['boost24h']['access'] == 0:
                        e = discord.Embed(title=f"", description=f"У вас нет доступа к этой команде, сначала разблокируйте покупку дополнительных примогемов на 7 уровне.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name=f"Магазин группировки {title}")
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    elif perks['boost24h']['buy'] == 0:
                        if clan_info["balance"] < 250000:
                            primo = self.bot.get_emoji(config.MONEY_EMOJI)
                            e = discord.Embed(title=f"", description=f"Недостаточно примогемов на балансе группировки. Цена: 250.000{primo}", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
                        else:
                            if perks["boost24h"]["time"] > int(time.time()):
                                e = discord.Embed(title=f"", description=f"Данный товар можно покупать раз в 10 дней.\nДоступно будет через {seconds_to_hh_mm_ss_t(perks['boost24h']['time']-int(time.time()))}.", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=e)
                            else:
                                reactions = db.reactions
                                e = discord.Embed(title=f"", description=f"Вы уверены, что хотите купить дополнительные примогемы для группировки?", color=discord.Colour(0x2F3136))
                                e.timestamp = datetime.datetime.utcnow()
                                e.set_author(name=f"Магазин группировки {title}")
                                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                                message_s = await ctx.channel.send(embed=e)
                                await message_s.add_reaction("✅")
                                await message_s.add_reaction("❌")
                                reactions.insert_one({"message_id": str(message_s.id), "author": str(ctx.author.id), "time": int(time.time()) + 30, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "shop_clan", "clan": clan, "item": "boost24h" })
                    else:
                        e = discord.Embed(title=f"", description=f"У вас уже куплена войс комната группировки.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name=f"Магазин группировки {title}")
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                elif messageArray[0] == "4":
                    if perks['chat']['access'] == 0:
                        e = discord.Embed(title=f"", description=f"У вас нет доступа к этой команде, сначала разблокируйте покупку чат канала с капчей на 9 уровне.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name=f"Магазин группировки {title}")
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    elif perks['chat']['buy'] == 0:
                        if clan_info["balance"] < 500000:
                            primo = self.bot.get_emoji(config.MONEY_EMOJI)
                            e = discord.Embed(title=f"", description=f"Недостаточно примогемов на балансе группировки. Цена: 500.000{primo}", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
                        else:
                            reactions = db.reactions
                            e = discord.Embed(title=f"", description=f"Вы уверены, что хотите купить чат канала с капчей для группировки?", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_author(name=f"Магазин группировки {title}")
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            message_s = await ctx.channel.send(embed=e)
                            await message_s.add_reaction("✅")
                            await message_s.add_reaction("❌")
                            reactions.insert_one({"message_id": str(message_s.id), "author": str(ctx.author.id), "time": int(time.time()) + 30, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "lang": "ru", "type": "shop_clan", "clan": clan, "item": "chat" })
                    else:
                        e = discord.Embed(title=f"", description=f"У вас уже куплен чат канал с капчей для группировки.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_author(name=f"Магазин группировки {title}")
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                else:
                    e = discord.Embed(title=f"", description=f"Номер `{messageArray[0]}` в магазине не найден.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
    
    @guild_command.command(name="role")
    async def guild_role(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if not clan:
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = ctx.guild.get_member(int(clan_info["owner"]))
            if ctx.author != owner:
                e = discord.Embed(title=f"", description=f"Ты не владелец группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            perks = clan_info["perks"]
            primo = self.bot.get_emoji(config.MONEY_EMOJI)
            if perks['role']['access'] == 0:
                e = discord.Embed(title=f"", description=f"У вас нет доступа к этой команде, сначала разблокируйте покупку роли на 3 уровне.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            elif perks['role']['buy'] == 0:
                e = discord.Embed(title=f"", description=f"У вас нет доступа к этой команде, сначала купите роль в `.g shop`.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                if len(messageArray) <= 0:
                    e = discord.Embed(title=f"", description=f"Укажите цвет в формате `#8aff8a` или `8aff8a`.\n`#000000` - прозрачный цвет.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    if perks["role"]["cooldown"] > int(time.time()):
                        e = discord.Embed(title=f"", description=f"Цвет роли можно менять раз в 24 часа.\nДоступно будет через {seconds_to_hh_mm_ss_t(perks['role']['cooldown']-int(time.time()))}.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    else:
                        try:
                            colort = messageArray[0].replace('#', '')
                            colorn = int(colort, 16)
                            
                            color1 = discord.Colour(colorn)

                            loadingem = self.bot.get_emoji(794502101853798400)
                            e = discord.Embed(title="", description=f"{loadingem} Обработка...", color=discord.Color(0x2F3136))
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            msg = await ctx.channel.send(embed=e)
                            
                            roleclan = ctx.guild.get_role(int(perks["role"]["id"]))
                            await roleclan.edit(colour=color1)
                            perks["role"]["cooldown"] = int(time.time()) + 86400
                            clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks }})
                            e = discord.Embed(title=f"", description=f"{f'Цвет роли группировки изменен на `#{colort}`.' if colorn != 0 else 'Цвет роли группировки изменен на прозрачный.'}", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await msg.edit(embed=e)
                        except BaseException as e:
                            e = discord.Embed(title=f"", description=f"Укажите цвет в формате `#8aff8a` или `8aff8a`.\n`#000000` - прозрачный цвет.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
    @guild_command.command(name="color")
    async def guild_color(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if not clan:
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = ctx.guild.get_member(int(clan_info["owner"]))
            if ctx.author != owner:
                e = discord.Embed(title=f"", description=f"Ты не владелец группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            perks = clan_info["perks"]
            primo = self.bot.get_emoji(config.MONEY_EMOJI)
            if perks['interface']['access'] == 0:
                e = discord.Embed(title=f"", description=f"У вас нет доступа к этой команде, сначала достигните 2 уровня.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                if len(messageArray) <= 0:
                    e = discord.Embed(title=f"", description=f"Укажите цвет в формате `#8aff8a` или `8aff8a`.\n`#2f3136` - прозрачный цвет.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    if perks["interface"]["cooldown_color"] > int(time.time()):
                        e = discord.Embed(title=f"", description=f"Цвет группировки можно менять раз в 7 дней.\nДоступно будет через {seconds_to_hh_mm_ss_t(perks['interface']['cooldown_color']-int(time.time()))}.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    else:
                        try:
                            colort = messageArray[0].replace('#', '')
                            colorn = int(colort, 16)

                            perks["interface"]["cooldown_color"] = int(time.time()) + 604800
                            clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks, "color": f"{colorn}" }})
                            e = discord.Embed(title=f"", description=f"{f'Цвет группировки изменен на `#{colort}`.' if colorn != 3092790 else 'Цвет группировки изменен на прозрачный.'}", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
                        except BaseException as e:
                            e = discord.Embed(title=f"", description=f"Укажите цвет в формате `#8aff8a` или `8aff8a`.\n`#2f3136` - прозрачный цвет.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            await ctx.channel.send(embed=e)
    
    @guild_command.command(name="image")
    async def guild_image(self, ctx, *messageArray):
        user = users.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        clan = user["clan"]
        if not clan:
            e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
        else:
            clan_info = clans_db.find_one({"id": int(clan) })
            title = clan_info["title"]
            owner = ctx.guild.get_member(int(clan_info["owner"]))
            if ctx.author != owner:
                e = discord.Embed(title=f"", description=f"Ты не владелец группировки.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            perks = clan_info["perks"]
            primo = self.bot.get_emoji(config.MONEY_EMOJI)
            if perks['interface']['access'] == 0:
                e = discord.Embed(title=f"", description=f"У вас нет доступа к этой команде, сначала достигните 2 уровня.", color=discord.Colour(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=e)
            else:
                if len(messageArray) <= 0:
                    e = discord.Embed(title=f"", description=f"Укажите URL картинки, загруженной в Discord.", color=discord.Colour(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                else:
                    if perks["interface"]["cooldown_image"] > int(time.time()):
                        e = discord.Embed(title=f"", description=f"Картинку группировки можно менять раз в 7 дней.\nДоступно будет через {seconds_to_hh_mm_ss_t(perks['interface']['cooldown_image']-int(time.time()))}.", color=discord.Colour(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=e)
                    else:
                        a = messageArray[0]
                        regex = r'((?:(https?|s?ftp):\/\/)?(?:www\.)?((?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)([A-Z]{2,6})|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(?::(\d{1,5}))?(?:(\/\S+)*))'
                        urls1 = re.findall(r'(https?://[^\s]+)', a)
                        urls2 = re.findall(r'([^\s]+)', a)
                        find_urls_in_string = re.compile(regex, re.IGNORECASE)
                        if len(urls1) > 0:  
                            url_check1 = find_urls_in_string.search(urls1[0])
                        else:
                            url_check1 = None
                        if len(urls2) > 0:  
                            url_check2 = find_urls_in_string.search(urls2[0])
                        else:
                            url_check2 = None
                        if not url_check1 and not url_check2:
                            e = discord.Embed(title=f"", description=f"Укажите URL картинки, загруженной в Discord.", color=discord.Colour(0x2F3136))
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                            return await ctx.channel.send(embed=e)
                        if url_check1:
                            if url_check1.groups()[5]:
                                if str(url_check1.groups()[2]) != "media.discordapp.net" and str(url_check1.groups()[2]) != "cdn.discordapp.com":
                                    e = discord.Embed(title=f"", description=f"Укажите URL картинки, загруженной в Discord.", color=discord.Colour(0x2F3136))
                                    e.timestamp = datetime.datetime.utcnow()
                                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                                    return await ctx.channel.send(embed=e)
                                elif url_check1.groups()[5].lower().endswith('.png') is False and url_check1.groups()[5].lower().endswith('.jpg') is False and url_check1.groups()[5].lower().endswith('.jpeg') is False and url_check1.groups()[5].lower().endswith('.gif') is False:
                                    e = discord.Embed(title=f"", description=f"Файл должен оканчиваться на `.png`, `.jpg`, `.jpeg` или `.gif`.", color=discord.Colour(0x2F3136))
                                    e.timestamp = datetime.datetime.utcnow()
                                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                                    return await ctx.channel.send(embed=e)
                                else:
                                    perks["interface"]["cooldown_image"] = int(time.time()) + 604800
                                    clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks, "image": f"{urls1[0]}" }})
                                    e = discord.Embed(title=f"", description=f"Картинка была установлена.", color=discord.Colour(0x2F3136))
                                    e.timestamp = datetime.datetime.utcnow()
                                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                                    return await ctx.channel.send(embed=e)
                        if url_check2:
                            if url_check2.groups()[5]:
                                if str(url_check2.groups()[2]) != "media.discordapp.net" and str(url_check2.groups()[2]) != "cdn.discordapp.com":
                                    e = discord.Embed(title=f"", description=f"Укажите URL картинки, загруженной в Discord.", color=discord.Colour(0x2F3136))
                                    e.timestamp = datetime.datetime.utcnow()
                                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                                    return await ctx.channel.send(embed=e)
                                elif url_check2.groups()[5].lower().endswith('.png') is False and url_check2.groups()[5].lower().endswith('.jpg') is False and url_check2.groups()[5].lower().endswith('.jpeg') is False and url_check2.groups()[5].lower().endswith('.gif') is False:
                                    e = discord.Embed(title=f"", description=f"Файл должен оканчиваться на `.png`, `.jpg`, `.jpeg` или `.gif`.", color=discord.Colour(0x2F3136))
                                    e.timestamp = datetime.datetime.utcnow()
                                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                                    return await ctx.channel.send(embed=e)
                                else:
                                    perks["interface"]["cooldown_image"] = int(time.time()) + 604800
                                    urln = urls2[0]
                                    if urln.startswith("https://") is False and urln.startswith("http://") is False:
                                        urln = f"https://{urln}"
                                    clans_db.update_one({ "id": int(clan) }, { "$set": { "perks": perks, "image": f"{urln}" }})
                                    e = discord.Embed(title=f"", description=f"Картинка была установлена.", color=discord.Colour(0x2F3136))
                                    e.timestamp = datetime.datetime.utcnow()
                                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                                    return await ctx.channel.send(embed=e)

    @guild_command.command(name='list')
    @commands.cooldown(1, 15, BucketType.user)
    async def guild_list(self, ctx, *messageArray):
        dbclans = db.clans
        clans = dbclans.find()
        clanss = "**Название — уровень — количество участников — ID — владелец**\n"
        clanss += '\n'.join(f'{i + 1}. **{clans[i]["title"]} — {clans[i]["lvl"]} уровень — {len(clans[i]["members"])}/{clans[i]["limitmembers"]} — {clans[i]["id"]} — <@!{clans[i]["owner"]}>{", <@!" if clans[i]["coowner"] else ""}{clans[i]["coowner"] if clans[i]["coowner"] else ""}{">" if clans[i]["coowner"] else ""} **' for i in range(clans.count()))
        clanss += "\n\nДля просмотра профиля группировки: `.gi [название]`"
        e = discord.Embed(title="", description=f"{clanss}", color=discord.Colour(0x2F3136))
        e.set_author(name="Список группировок")
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=e)

            # elif messageArray[0] == "war":
            #     #if str(ctx.author.id) not in config.ADMINS:
            #     #    return
            #     if not clan:
            #         e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            #         e.timestamp = datetime.datetime.utcnow()
            #         e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #         await ctx.channel.send(embed=e)
            #     else:
            #         clan_info = clans_db.find_one({"id": int(clan) })
            #         title = clan_info["title"]
            #         owner = ctx.guild.get_member(int(clan_info["owner"]))
            #         if ctx.author != owner:
            #             e = discord.Embed(title=f"", description=f"Ты не владелец группировки.", color=discord.Colour(0x2F3136))
            #             e.timestamp = datetime.datetime.utcnow()
            #             e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #             await ctx.channel.send(embed=e)
            #         else:
            #             if clan_info["perks"]["role"]["buy"] == 0:
            #                 e = discord.Embed(title=f"", description=f"Для участия в войнах группировок нужно иметь хотя бы роль группировки.", color=discord.Colour(0x2F3136))
            #                 e.timestamp = datetime.datetime.utcnow()
            #                 e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                 await ctx.channel.send(embed=e)
            #             else:
            #                 try:
            #                     clanwar = clan_info["war"]
            #                 except:
            #                     e = discord.Embed(title=f"", description=f"Ваша группировка не зарегистрирован в войнах группировок, для регистрации владелец группировки должен ввести команду `.g warinfo`.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     return await ctx.channel.send(embed=e)
            #                 x = int(time.time())
            #                 #if x - clanwar["lastwar"]["date"] < 43200:
            #                 #    e = discord.Embed(title=f"", description=f"Войны группировок можно проводить раз в 12 часов. Осталось: {seconds_to_hh_mm_ss_t((clanwar['lastwar']['date'] + 43200) - x)}", color=discord.Colour(0x2F3136))
            #                 #    e.timestamp = datetime.datetime.utcnow()
            #                 #    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                 #    await ctx.channel.send(embed=e)
            #                 if clan_info["war_status"] == 1:
            #                     e = discord.Embed(title=f"", description=f"У вас уже идёт активная война.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif clan_info["war_status"] == 2:
            #                     e = discord.Embed(title=f"", description=f"От вас или вам уже было отправлено приглашение войны.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif len(messageArray) == 1:
            #                     e = discord.Embed(title=f"", description=f"Укажите ID группировки, которой хотите предложить войну.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif check_number(messageArray[1]) is False:
            #                     e = discord.Embed(title=f"", description=f"Укажите цифру на месте ID.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif messageArray[1] == str(clan_info["war"]["id"]):
            #                     e = discord.Embed(title=f"", description=f"Укажите ID не своей группировки.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif clans_db.find_one({ "war.id": int(messageArray[1]) }) is None:
            #                     e = discord.Embed(title=f"", description=f"Такой ID не участвует в войнах группировок.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif clans_db.find_one({ "war.id": int(messageArray[1]) })["perks"]["role"]["buy"] == 0:
            #                     e = discord.Embed(title=f"", description=f"Этой группировке нельзя отправить запрос на войну.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif len(messageArray) < 3:
            #                     e = discord.Embed(title=f"", description=f"Укажите сумму, на которую хотите воевать.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif check_number(messageArray[2]) is False:
            #                     e = discord.Embed(title=f"", description=f"Укажите цифру на месте суммы.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif int(messageArray[2]) < 15000:
            #                     e = discord.Embed(title=f"", description=f"Войны группировок доступны от 15.000 примогемов.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif clan_info["balance"] < int(messageArray[2]):
            #                     e = discord.Embed(title=f"", description=f"Недостаточно примогемов.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif clans_db.find_one({ "war.id": int(messageArray[1]) })["balance"] < int(messageArray[2]):
            #                     e = discord.Embed(title=f"", description=f"Недостаточно примогемов у противника.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 elif clans_db.find_one({ "war.id": int(messageArray[1]) })["war_status"] == 1 or clans_db.find_one({ "war.id": int(messageArray[1]) })["war_status"] == 2:
            #                     e = discord.Embed(title=f"", description=f"Невозможно отправить запрос на войну, так как у группировки противника уже идёт война.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     await ctx.channel.send(embed=e)
            #                 else:
            #                     opponent = clans_db.find_one({ "war.id": int(messageArray[1]) })
            #                     category = self.bot.get_channel(841440615770095616)
            #                     if clan_info["perks"]["chat"]["buy"] == 0:
            #                         role_clan = ctx.message.guild.get_role(int(clan_info["perks"]["role"]["id"]))
            #                         new_temp_text_chat = await ctx.message.guild.create_text_channel(name=f"{clan_info['title']} temp_chat", category=category)
            #                         await new_temp_text_chat.set_permissions(role_clan, send_messages=True,
            #                                                                             view_channel=True,
            #                                                                             add_reactions=True,
            #                                                                             attach_files=True,
            #                                                                             read_messages=True,
            #                                                                             external_emojis=True,
            #                                                                             read_message_history=True)
            #                         clans_db.update_one({ "id": clan_info["id"] }, { "$set": { "temp_chat": str(new_temp_text_chat.id) } })
            #                     else:
            #                         new_temp_text_chat = self.bot.get_channel(int(clan_info["perks"]["chat"]["id"]))
            #                     if opponent["perks"]["chat"]["buy"] == 0:
            #                         role_clan = ctx.message.guild.get_role(int(opponent["perks"]["role"]["id"]))
            #                         new_temp_text_chat2 = await ctx.message.guild.create_text_channel(name=f"{opponent['title']} temp_chat", category=category)
            #                         await new_temp_text_chat2.set_permissions(role_clan, send_messages=True,
            #                                                                             view_channel=True,
            #                                                                             add_reactions=True,
            #                                                                             attach_files=True,
            #                                                                             read_messages=True,
            #                                                                             external_emojis=True,
            #                                                                             read_message_history=True)
            #                         clans_db.update_one({ "id": opponent["id"] }, { "$set": { "temp_chat": str(new_temp_text_chat2.id) } })
            #                     else:
            #                         new_temp_text_chat2 = self.bot.get_channel(int(opponent["perks"]["chat"]["id"]))
            #                     reactions = db.reactions
            #                     money_emoji = self.bot.get_emoji(config.MONEY_EMOJI)
            #                     e = discord.Embed(title=f"", description=f"Вы уверены, что хотите начать войну с кланом \"**{opponent['title']}**\" на {messageArray[2]}{money_emoji}?", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_author(name=f"Война группировок")
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     message_s = await new_temp_text_chat.send(content=f"<@&{clan_info['perks']['role']['id']}>", embed=e)
            #                     await message_s.add_reaction("✅")
            #                     await message_s.add_reaction("❌")
            #                     reactions.insert_one({"message_id": str(message_s.id), "member": str(ctx.author.id), "costwar": int(messageArray[2]), "clan_id": clan_info["war"]["id"], "clan_id_opponent": int(messageArray[1]), "time": int(time.time()) + 300, "guild_id": str(ctx.guild.id), "channels_id": [str(new_temp_text_chat.id), str(new_temp_text_chat2.id)], "type": "war_clan" })
            #                     clans_db.update_one({ "id": clan_info["id"] }, { "$set": { "war_status": 2 } })

            # elif messageArray[0] == "warinfo":
            #     #if str(ctx.author.id) not in config.ADMINS:
            #     #    return
            #     if not clan:
            #         e = discord.Embed(title=f"", description=f"Ты не находишься в группировке.", color=discord.Colour(0x2F3136))
            #         e.timestamp = datetime.datetime.utcnow()
            #         e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #         await ctx.channel.send(embed=e)
            #     else:
            #         clan_info = clans_db.find_one({"id": int(clan) })
            #         title = clan_info["title"]
            #         image = clan_info["image"]
            #         color = clan_info["color"]
            #         owner = ctx.guild.get_member(int(clan_info["owner"]))
            #         try:
            #             clanwar = clan_info["war"]
            #             cidwar = clanwar["id"]
            #             clastwar = clanwar["lastwar"]
            #             cregwar = clanwar["regdate"]
            #             clastwardate = clastwar["date"]
            #             creslastwar = clastwar["result"]
            #             cmemberslastwar = clastwar["members"]
            #             cmoneyslastwar = clastwar["money"]
            #             cwins = clanwar["wins"]
            #             closes = clanwar["loses"]
            #             cgames = len(clanwar["games"])
            #             moneys = clanwar["money"]
            #             captches = clanwar["captches"]
            #             if color == "":
            #                 color = discord.Colour(0x2F3136)
            #             else:
            #                 color = int(color)
            #             e = discord.Embed(title='', description="", color=color)
            #             if image != "":
            #                 e.set_image(url=image)
            #             e.set_author(name=f"Войны группировок - информация группировки \"{title}\"")
            #             e.add_field(name="ID", value=f"```{cidwar}```")
            #             e.add_field(name="Дата регистрации", value=f"```{datetime.datetime.utcfromtimestamp(cregwar + 10800).strftime('%d.%m.%Y %H:%M:%S')}```")
            #             e.add_field(name="Количество войн", value=f"```{cgames}```")
            #             e.add_field(name="Количество побед", value=f"```{cwins}```")
            #             e.add_field(name="Количество поражений", value=f"```{closes}```")
            #             e.add_field(name="Последняя война", value="```Не было```" if clastwardate == 0 else f"```{datetime.datetime.utcfromtimestamp(clastwardate + 10800).strftime('%d.%m.%Y %H:%M')} - {'Победа' if creslastwar == 'win' else 'Поражение'} - {len(cmemberslastwar)} {funcb.declension(['участник', 'участника', 'участников'], len(cmemberslastwar))} - {cmoneyslastwar}```", inline=False)
            #             e.add_field(name="Решено кодов", value=f"```{captches}```")
            #             e.add_field(name="Выиграно/проиграно примогемов", value=f"```diff\n{f'+{moneys}' if moneys > 0 else f'{moneys}' if moneys == 0 else f'{moneys}'}\n```")
            #             e.timestamp = datetime.datetime.utcnow()
            #             e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        
            #             await ctx.channel.send(embed=e)
            #         except:
            #             if clan_info["perks"]["role"]["buy"] == 0:
            #                 e = discord.Embed(title=f"", description=f"Для участия в войнах группировок нужно иметь хотя бы роль группировки.", color=discord.Colour(0x2F3136))
            #                 e.timestamp = datetime.datetime.utcnow()
            #                 e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                 return await ctx.channel.send(embed=e)
            #             else:
            #                 if ctx.author != owner:
            #                     e = discord.Embed(title=f"", description=f"Ваша группировка не зарегистрирован в войнах группировок, для регистрации эту команду должен ввести владелец группировки.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     return await ctx.channel.send(embed=e)
            #                 else:
            #                     clans_db.update_one({ "id": int(clan) }, { "$set": { "war": { "id": clan_info['id'], "lastwar": { "date": 0, "result": "none", "members": [], "captches": 0, "money": 0 }, "regdate": int(time.time()), "wins": 0, "loses": 0, "games": [], "captches": 0, "money": 0 } } })
            #                     e = discord.Embed(title=f"", description=f"Ваша группировка был зарегистрирована в войнах группировок, ваш ID группировки: {clan_info['id']}.\nПовторите команду для просмотра информации о своей группировке в войнах группировок.", color=discord.Colour(0x2F3136))
            #                     e.timestamp = datetime.datetime.utcnow()
            #                     e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            #                     return await ctx.channel.send(embed=e)

def setup(bot):
    bot.add_cog(Clans(bot))