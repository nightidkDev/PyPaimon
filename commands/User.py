import discord
from discord.ext import commands
from discord.ext.commands.core import command
import pymongo
import time
import os
import sys
import datetime
import string
import random
from PIL import Image, ImageFont, ImageSequence, ImageDraw, ImageOps
import requests
import re
import io
sys.path.append("../../")
import config
from discord_components import *
uri = config.uri
uri2 = config.uri2
mongoclient = pymongo.MongoClient(uri)
mongoclient2 = pymongo.MongoClient(uri2)
db = mongoclient.aimi
db2 = mongoclient2.aimi
reactions = db2.reactions
bgs = db.backgrounds
shops = db.shops_list
mutes = db.mutes
roles_wishes = db2.roles_wishes
special_role = db2.special_wishes
chats_wishes = db2.chats_wishes
voices_wishes = db2.voices_wishes
extended_sub = db2.extended_sub
packs_wishes = db2.packs_wishes
banners_wishes = db2.banners_wishes

users = db.prof_ec_users

def check(member, guild, role):
    " Check user roles in inventory "
    role_g = guild.get_role(int(role))
    if role_g in member.roles:
        return "надето"
    else:
        return "снято"

def check_c(member, card):
    " Check background cards in inventory "
    if int(card) == member["background"]:
        return " - надето"
    else:
        return ""


def check_w(member, guild, role, item):
    " Check user's waifu roles in inventory "
    role_g = guild.get_role(int(role))
    if role_g in member.roles:
        return "надето"
    elif item["equip"] == 1:
        return "надето (системно)"
    else:
        return "снято"

def gen_promo(count, len_letters=4):
    letters_and_digits = string.ascii_letters + string.digits
    parts = []
    for i in range(count):
        parts.append(''.join(random.sample(letters_and_digits, len_letters)))
    enter = "-".join(parts)
    return enter

def cleanname(name):
    rus = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    ukr = "АаБбВвГгҐґДдЕеЄєЖжЗзИиІіЇїЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЬьЮюЯя"
    for x in list(name):
        if x not in string.printable and x not in rus and x not in ukr:
            name = name.replace(x, "?")

    return name

def checkname(name):
    res = False
    rus = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    for x in list(name):
        if x not in string.printable and x not in rus:
            res = True
            break

    return res

def toFixed(numObj, digits=0):
    return float(f"{numObj:.{digits}f}")

def prepare_mask(size, antialias = 2):
    mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)

def crop(im, s):
    w, h = im.size
    k = w / s[0] - h / s[1]
    if k > 0: im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
    elif k < 0: im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
    return im.resize(s, Image.ANTIALIAS)

def seconds_to_hh_mm_ss(seconds):
    " Convert seconds to d hh:mm:ss "
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}дн. {h:d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:d}:{s:02d}"

def declension(forms, val):
    cases = [ 2, 0, 1, 1, 1, 2 ]
    if val % 100 > 4 and val % 100 < 20:
        return forms[2]
    else:
        if val % 10 < 5:
            return forms[cases[val % 10]]
        else:
            return forms[cases[5]]


def check_member(guild, text):
    """ Check member ID.
    If exists -> <discord.Member>,
    else -> None
    """
    try:
        member = guild.get_member(int(text[0]))
        return member
    except:
        return None

def check_member_name(message, text):
    """ Check member name.
    If exists -> <discord.Member>,
    else -> None
    """
    name = " ".join(text)
    try:
        member = message.guild.get_member_named(name)
        return member
    except:
        return None


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="goto")
    @commands.has_permissions(administrator=True)
    async def goto(self, ctx, member: discord.Member=None):
        if not member:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"Укажите пользователя."
            return await ctx.send(embed=e)
        if not member.voice:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"Я не могу вас перенести, т.к. пользователь не находится в голосовом канале."
            return await ctx.send(embed=e)
        if not ctx.author.voice:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"Я не могу вас перенести, т.к. вы не находитесь в голосовом канале."
            return await ctx.send(embed=e)
        await ctx.author.edit(voice_channel=member.voice.channel)
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"Вы были перемещены в канал {member.voice.channel.mention} к {member.mention}"
        await ctx.send(embed=e)

    @commands.command(name="grab")
    @commands.has_permissions(administrator=True)
    async def grab(self, ctx, member: discord.Member=None):
        if not member:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"Укажите пользователя."
            return await ctx.send(embed=e)
        if not member.voice:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"Я не могу перенести пользователя к вам, т.к. пользователь не находится в голосовом канале."
            return await ctx.send(embed=e)
        if not ctx.author.voice:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"Я не могу перенести пользователя к вам, т.к. вы не находитесь в голосовом канале."
            return await ctx.send(embed=e)
        await member.edit(voice_channel=ctx.author.voice.channel)
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"{member.mention} был перемещён к вам в канал."
        await ctx.send(embed=e)

    @commands.command(name="tp")
    @commands.has_permissions(administrator=True)
    async def tpmember(self, ctx, member: discord.Member=None, voice: discord.VoiceChannel=None):
        if not member:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"Укажите пользователя."
            return await ctx.send(embed=e)
        if not member:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"Укажите голосовой канал."
            return await ctx.send(embed=e)
        if not member.voice:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"Я не могу перенести пользователя в {voice.mention}, т.к. пользователь не находится в голосовом канале."
            return await ctx.send(embed=e)
        await member.edit(voice_channel=voice)
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"{member.mention} был перемещён в {voice.mention}"
        await ctx.send(embed=e)

    @commands.command(name="slevel")
    @commands.is_owner()
    async def slevel(self, ctx, member: discord.Member, lvl):
        level = int(lvl) - 1
        lvl = int(lvl)
        exp = 5 * (level * level) + 50 * level + 100
        nlvl_ins = lvl * 10 + 45

        ranks = config.ranks
        last_role = None
        index_role = None
        role_lvl = None
        for rank in ranks:
            if lvl >= rank[0]:
                role_lvl = ctx.guild.get_role(int(rank[1]))
                index_role = ranks.index([rank[0], rank[1], rank[2]])
                
                if role_lvl not in member.roles:
                    await member.add_roles(role_lvl)
                break
        if index_role != len(ranks) - 1:
            for rank in ranks:
                role_check = ctx.guild.get_role(int(rank[1]))
                if role_check in member.roles:
                    if role_lvl == role_check:
                        continue
                    await member.remove_roles(role_check)
        users.update_one({ "disid": f"{member.id}", "guild": f"{ctx.guild.id}" }, { "$set": { "exp": 0, "nexp": str(exp), "lvl": lvl, "nlvl": str(nlvl_ins) } })
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        primo = self.bot.get_emoji(config.MONEY_EMOJI)
        e.description = f"У пользователя {member.mention} установлен уровень {lvl}."
        await ctx.send(embed=e)
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        primo = self.bot.get_emoji(config.MONEY_EMOJI)
        e.description = f"У вас установлен уровень {lvl}."
        try:
            await member.send(embed=e)
        except:
            pass

    @commands.command(name="betadel")
    @commands.is_owner()
    async def betadel(self, ctx, member: discord.Member, lvl, money):
        level = int(lvl) - 1
        lvl = int(lvl)
        exp = 5 * (level * level) + 50 * level + 100
        nlvl_ins = lvl * 10 + 45

        ranks = [
                    [100, "775802151405355048"],
                    [90, "775800915537166346"],
                    [80, "775797926869598249"],
                    [70, "775797342862573638"],
                    [60, "775796352163774496"],
                    [50, "775795871454724096"],
                    [40, "775795087631450112"],
                    [30, "775794183767851059"],
                    [20, "775788094368251944"],
                    [10, "775786187604361256"],
                    [5, "775785658286997514"]                        
                ]
        last_role = None
        index_role = None
        role_lvl = None
        for rank in ranks:
            if lvl >= rank[0]:
                role_lvl = ctx.guild.get_role(int(rank[1]))
                index_role = ranks.index([rank[0], rank[1]])
                
                if role_lvl not in member.roles:
                    await member.add_roles(role_lvl)
                break
        if index_role != len(ranks) - 1:
            for rank in ranks:
                role_check = ctx.guild.get_role(int(rank[1]))
                if role_check in member.roles:
                    if role_lvl == role_check:
                        continue
                    await member.remove_roles(role_check)
        users.update_one({ "disid": f"{member.id}", "guild": f"{ctx.guild.id}" }, { "$set": { f"money": int(money), "exp": 0, "nexp": str(exp), "lvl": lvl, "nlvl": str(nlvl_ins), "wishesCount": config.wishesCount } })
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        primo = self.bot.get_emoji(config.MONEY_EMOJI)
        e.description = f"У пользователю {member.mention} установлен уровень {lvl}, а так же установлен баланс {money}{primo} и забраны все молитвы."
        await ctx.send(embed=e)
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        primo = self.bot.get_emoji(config.MONEY_EMOJI)
        e.description = f"У вас установлен уровень {lvl}, а так же установлен баланс {money}{primo} и забраны все молитвы."
        try:
            await member.send(embed=e)
        except:
            pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def give_wishes(self, ctx, name_wish, count_wish, member: discord.User = None):
        if not name_wish:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = "Укажите название крутки."
            return await ctx.send(embed=e)
        if not count_wish:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = "Укажите пользователя."
            return await ctx.send(embed=e)
        if not member:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = "Укажите пользователя."
            return await ctx.send(embed=e)

        item_name = "IacquaintFate" if name_wish == "1" else "IntertwinedFate"

        #push_items = [items for a in range(int(count_wish))]

        users.update_one({ "disid": f"{member.id}", "guild": f"{ctx.guild.id}" }, { "$inc": { f"wishesCount.{item_name}": int(count_wish) } })

        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        emoji_wish = self.bot.get_emoji(772748673251016745) if name_wish == "1" else self.bot.get_emoji(772748672999620629)
        e.description = f"Пользователю {member.mention} выдано {emoji_wish}x{count_wish}."
        await ctx.send(embed=e)
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"Вам было выдано {emoji_wish}x{count_wish}"
        await member.send(embed=e)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def give_voice(self, ctx, member:discord.User=None, count_days=None):
        if not member:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = "Укажите пользователя."
            return await ctx.send(embed=e)
        if not count_days:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = "Укажите количество дней войса."
            return await ctx.send(embed=e)
        if voices_wishes.count_documents({ "owner": f'{member.id}' }) == 0:
            voices_wishes.insert_one({ "owner": f'{member.id}', 'voiceID': f"", "timeout": int(time.time()) + (int(count_days) * 86400), "permissions": [], "name": "", "limit": 0, "timeoutHour": 0 })
        else:
            voices_wishes.update_one({ "owner": f'{member.id}'}, { "$inc": { "timeout": int(count_days) * 86400 } })
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"Пользователю {member.mention} выдано {count_days} дней войса."
        await ctx.send(embed=e)
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"Вам было выдано {count_days} дней войса."
        await member.send(embed=e)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delete_inv(self, ctx, member:discord.User=None, index=None, reward=None):
        if not member:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = "Укажите пользователя."
            return await ctx.send(embed=e)
        if not index:
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = "Укажите индекс в инвентаре."
            return await ctx.send(embed=e)
        index = int(index)
        if not reward:
            reward = 0
        else:
            reward = int(reward)
        user_info = users.find_one({ "disid": f"{member.id}", "guild": f"{ctx.guild.id}" })
        inv = user_info["inv"]
        inv.pop(index - 1)
        users.update_one({ "disid": f"{member.id}", "guild": f"{ctx.guild.id}" }, { "$set": { "inv": inv }, "$inc": { "money": reward } })
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        primo = self.bot.get_emoji(config.MONEY_EMOJI)
        e.description = f"У пользователю {member.mention} забрана позиция {index} из инвентаря и выдано {reward}{primo}"
        await ctx.send(embed=e)
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"У вас забрана позиция {index} из инвентаря и выдано {reward}{primo}"
        await member.send(embed=e)

    @commands.command()
    async def buyback(self, ctx):
        #if ctx.author.id == 518427777523908608:
        #    return
        role_3 = ctx.guild.get_role(876771661628731432)
        e = discord.Embed(color=0x2f3136)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        if role_3 not in ctx.author.roles:
            e.description = "У вас нет наказаний 3 уровня."
            await ctx.send(embed=e)
        else:
            userdb = users.find_one({ "disid": f"{ctx.author.id}", "guild": f"{ctx.guild.id}" })
            if userdb["money"] < 60000:
                e.description = "Недостаточно примогемов на балансе."
                await ctx.send(embed=e)
            else:
                users.update_one({ "disid": f"{ctx.author.id}", "guild": f"{ctx.guild.id}" }, { "$set": { "warns_counter_system": 0 }, "$inc": { "money": -60000 } })
                await ctx.author.remove_roles(role_3)
                e.description = "Уровень ваших наказний был снижен на 0 уровень."
                await ctx.send(embed=e)


    @commands.command()
    async def tmute(self, ctx, *messageArray):
        message = ctx.message
        e = discord.Embed(color=discord.Colour(0x2F3136))
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        if len(message.mentions) == 0:
            if mutes.count_documents({"disid": f"{message.author.id}", "guild": f"{message.guild.id}" }) >= 1:
                time_mute = mutes.find_one({"disid": f"{message.author.id}", "guild": f"{message.guild.id}" })["time_mute"]
                time_now = int(time.time())
                left_t = int(time_mute) - time_now
                e.description = f"Осталось: {seconds_to_hh_mm_ss(left_t)}"
                e.set_author(name=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=e)
            else:
                e.description = "Ты не находишься в муте."
                e.set_author(name=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=e)
        else:
            if mutes.count_documents({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" }) >= 1:
                time_mute = mutes.find_one({"disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" })["time_mute"]
                time_now = int(time.time())
                left_t = int(time_mute) - time_now
                e.description = f"Осталось: {seconds_to_hh_mm_ss(left_t)}"
                e.set_author(name=f"{message.mentions[0].display_name}", icon_url=message.mentions[0].avatar_url)
                await message.channel.send(embed=e)
            else:
                e.description = "Пользователь не находится в муте."
                e.set_author(name=f"{message.mentions[0].display_name}", icon_url=message.mentions[0].avatar_url)
                await message.channel.send(embed=e)

    @commands.command(name="seeinventory", aliases=["seeinv", "si", "sinv", "seei"])
    @commands.has_permissions(administrator=True)
    async def seeinventory(self, ctx, *messageArray):
        message = ctx.message

        checku = check_member(message.guild, messageArray)
        check_name = check_member_name(message, messageArray)

        user = message.mentions[0] if len(message.mentions) != 0 else checku if checku is not None else check_name if check_name is not None else None
        if user is None:
            e = discord.Embed(title="", description=f"Пользователь не найден.", color=discord.Color(0x2F3136))
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await message.reply(embed=e)

        info_role = roles_wishes.find_one({ "owner": f"{user.id}" })
        info_special = special_role.find_one({ "id": f"{user.id}" })
        info_voice = voices_wishes.find_one({ "owner": f"{user.id}" })
        info_chat = chats_wishes.find_one({ "owner": f"{user.id}" })
        info_ext_sub = extended_sub.find_one({ 'id': f"{user.id}" })
        info_pack = packs_wishes.find_one({ 'id': f"{user.id}" })
        info_banner = banners_wishes.find_one({ 'id': f"{user.id}" })

        coll_user = db.prof_ec_users
        bgn = db.backgrounds
        userb = coll_user.find_one({ "disid": str(user.id), "guild": f"{message.guild.id}" })
        e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
        e.set_author(name=f"Инвентарь - {user}")
        inv = ""
        inv_c = 0
        

        count_messages = 0
        items = [""]
        IacquaintFate = userb['wishesCount']['IacquaintFate']
        IntertwinedFate = userb['wishesCount']['IntertwinedFate']
        items_inv = userb['inv']

        for i in range(len(items_inv)):
            item_info = ""
            if items_inv[i]["type"] == "role":
                role = items_inv[i]["id"]
                item_info = f"{i + 1}. <@&{role}> - {check(user, message.guild, role)}\n"
            elif items_inv[i]["type"] == "background":
                card = items_inv[i]["id"]
                bgn_item = bgn.find_one({ "id": card }) 
                custom = self.bot.get_emoji(int(bgn_item["emoji"]))
                custom_name = bgn_item["name"]
                item_info = f"{i + 1}. {custom} **{custom_name}**{check_c(userb, card)}\n"
            elif items_inv[i]["type"] == "waifu":
                role = items_inv[i]["id"]
                item_info = f"{i + 1}. <@&{role}> - {check_w(user, message.guild, role, items_inv[i])}\n"
            if len(items[count_messages] + item_info) > 2000:
                count_messages += 1
                items.append("")
            items[count_messages] += item_info

            #elif item["type"] == "wish":
            #    if item["name"] == "IacquaintFate":
            #        IacquaintFate += 1
            #    elif item["name"] == "IntertwinedFate":
            #        IntertwinedFate += 1
                
                
            
        #if inv_c == 0:
        #    inv += "Пусто\n"
        IacquaintFate_emoji = self.bot.get_emoji(772748673251016745)
        IntertwinedFate_emoji = self.bot.get_emoji(772748672999620629)
        #if message.author.guild_permissions.administrator:
        sub = 'Нет подписок' if info_ext_sub is None else f'<@&912064706414526544> до {datetime.datetime.utcfromtimestamp(info_ext_sub["sub_pay_time"] + 2592000 + 10800).strftime("%d.%m.%Y %H:%M")}'
        inv += f"**Подписки**\n {sub}\n\n"
        inv += "**Молитвы**\n"
        inv += f"**{IacquaintFate_emoji} Судьбоносные встречи** - {IacquaintFate} {declension(['молитва', 'молитвы', 'молитв'], IacquaintFate)}\n"
        inv += f"**{IntertwinedFate_emoji} Переплетающиеся судьбы** - {IntertwinedFate} {declension(['молитва', 'молитвы', 'молитв'], IntertwinedFate)}\n"
        if info_role is not None:
            inv += f"**Личная роль** - {datetime.datetime.utcfromtimestamp(info_role['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"
        if info_special is not None:
            inv += f"**Специальная роль** - {datetime.datetime.utcfromtimestamp(info_special['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"
        if info_voice is not None:
            inv += f"**Личный войс** - {datetime.datetime.utcfromtimestamp(info_voice['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"# if info_voice['timeout'] < 2524597200 else f"**Личный войс** - ∞infinity∞\n"
        if info_chat is not None:
            inv += f"**Личный чат** - {datetime.datetime.utcfromtimestamp(info_chat['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"# if info_chat['timeout'] < 2524597200 else f"**Личный чат** - ∞infinity∞\n"
        if info_pack is not None:
            inv += f"**Пак реакций** - {datetime.datetime.utcfromtimestamp(info_pack['time'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"
        if info_banner is not None:
            inv += f"**Кастомный баннер** - {datetime.datetime.utcfromtimestamp(info_banner['time'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"
        inv += "\n"
        inv += items[0]
        e.description = inv
        e.timestamp = datetime.datetime.utcnow()
        if len(items) == 1:
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        await message.channel.send(embed=e)
        e2 = discord.Embed(color=discord.Color(0x2F3136))
        e2.timestamp = datetime.datetime.utcnow()
        for z in range(1, len(items)):
            if z == len(items) - 1:
                e2.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            e2.description = items[z]
            await message.channel.send(embed=e2)

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx):

        info_role = roles_wishes.find_one({ "owner": f"{ctx.author.id}" })
        info_special = special_role.find_one({ "id": f"{ctx.author.id}" })
        info_voice = voices_wishes.find_one({ "owner": f"{ctx.author.id}" })
        info_chat = chats_wishes.find_one({ "owner": f"{ctx.author.id}" })
        info_ext_sub = extended_sub.find_one({ 'id': f"{ctx.author.id}" })
        info_pack = packs_wishes.find_one({ 'id': f"{ctx.author.id}" })
        info_banner = banners_wishes.find_one({ 'id': f"{ctx.author.id}" })

        message = ctx.message
        coll_user = db.prof_ec_users
        bgn = db.backgrounds
        user = coll_user.find_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" })
        e = discord.Embed(title="Инвентарь", description="", color=discord.Color(0x2F3136))
        inv = ""
        inv_c = 0


        count_messages = 0
        items = [""]
        IacquaintFate = user['wishesCount']['IacquaintFate']
        IntertwinedFate = user['wishesCount']['IntertwinedFate']
        items_inv = user['inv']

        for i in range(len(items_inv)):
            item_info = ""
            if items_inv[i]["type"] == "role":
                role = items_inv[i]["id"]
                item_info = f"{i + 1}. <@&{role}> - {check(message.author, message.guild, role)}\n"
            elif items_inv[i]["type"] == "background":
                card = items_inv[i]["id"]
                bgn_item = bgn.find_one({ "id": card }) 
                custom = self.bot.get_emoji(int(bgn_item["emoji"]))
                custom_name = bgn_item["name"]
                item_info = f"{i + 1}. {custom} **{custom_name}**{check_c(user, card)}\n"
            elif items_inv[i]["type"] == "waifu":
                role = items_inv[i]["id"]
                item_info = f"{i + 1}. <@&{role}> - {check_w(message.author, message.guild, role, items_inv[i])}\n"
            if len(items[count_messages] + item_info) > 2000:
                count_messages += 1
                items.append("")
            items[count_messages] += item_info
            
        #if inv_c == 0:
        #    inv += "Пусто\n"
        IacquaintFate_emoji = self.bot.get_emoji(772748673251016745)
        IntertwinedFate_emoji = self.bot.get_emoji(772748672999620629)
        #if message.author.guild_permissions.administrator:
        sub = 'Нет подписок' if info_ext_sub is None else f'<@&912064706414526544> до {datetime.datetime.utcfromtimestamp(info_ext_sub["sub_pay_time"] + 2592000 + 10800).strftime("%d.%m.%Y %H:%M")}'
        inv += f"**Подписки**\n {sub}\n\n"
        inv += "**Молитвы**\n"
        inv += f"**{IacquaintFate_emoji} Судьбоносные встречи** - {IacquaintFate} {declension(['молитва', 'молитвы', 'молитв'], IacquaintFate)}\n"
        inv += f"**{IntertwinedFate_emoji} Переплетающиеся судьбы** - {IntertwinedFate} {declension(['молитва', 'молитвы', 'молитв'], IntertwinedFate)}\n"
        if info_role is not None:
            inv += f"**Личная роль** - {datetime.datetime.utcfromtimestamp(info_role['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"
        if info_special is not None:
            inv += f"**Специальная роль** - {datetime.datetime.utcfromtimestamp(info_special['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"
        if info_voice is not None:
            inv += f"**Личный войс** - {datetime.datetime.utcfromtimestamp(info_voice['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"# if info_voice['timeout'] < 2524597200 else f"**Личный войс** - ∞infinity∞\n"
        if info_chat is not None:
            inv += f"**Личный чат** - {datetime.datetime.utcfromtimestamp(info_chat['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"# if info_chat['timeout'] < 2524597200 else f"**Личный чат** - ∞infinity∞\n"
        if info_pack is not None:
            inv += f"**Пак реакций** - {datetime.datetime.utcfromtimestamp(info_pack['time'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"
        if info_banner is not None:
            inv += f"**Кастомный баннер** - {datetime.datetime.utcfromtimestamp(info_banner['time'] + 10800).strftime('%d.%m.%Y %H:%M')}\n"
        inv += "\n"
        inv += items[0]
        e.description = inv
        e.timestamp = datetime.datetime.utcnow()
        if len(items) == 1:
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        await message.channel.send(embed=e)
        e2 = discord.Embed(color=discord.Color(0x2F3136))
        e2.timestamp = datetime.datetime.utcnow()
        for z in range(1, len(items)):
            if z == len(items) - 1:
                e2.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            e2.description = items[z]
            await message.channel.send(embed=e2)
        
    @commands.command(name="equip", aliases=["eq"])
    async def equip(self, ctx, *messageArray):
        message = ctx.message
        coll = db.prof_ec_users
        bgn = db.backgrounds
        inv = coll.find_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" })
        len_inv = len(inv["inv"])
        inv_items = inv["inv"]
        ri = None
        item = None
        if len(messageArray) == 0 or messageArray[0] == "":
            e = discord.Embed(title="", description=f"Укажите индекс предмета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        try:
            ri = int(messageArray[0])
        except:
            e = discord.Embed(title="", description=f"Укажите индекс предмета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        if ri > len_inv or ri == 0:
            e = discord.Embed(title="", description=f"Укажите индекс предмета в инвентаре.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        item = inv_items[ri - 1]
        if item["type"] == "role":
            role_g = message.guild.get_role(int(item["id"]))
            if role_g in message.author.roles:
                e = discord.Embed(title="", description=f"Эта роль уже надета.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            await message.author.add_roles(role_g)
            e = discord.Embed(title="Инвентарь", description=f"Роль <@&{role_g.id}> успешно была добавлена.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
        elif item["type"] == "waifu":
            items = list(inv_items)
            items = list(filter(lambda x: x["type"] == "waifu", items))
            items = list(filter(lambda x: x["equip"] == 1, items))
            if len(items) != 0 and items[0]["id"] != item["id"]:
                e = discord.Embed(title="", description=f"Одна из ролей вайфу уже надета.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            role_g = message.guild.get_role(int(item["id"]))
            if role_g in message.author.roles:
                e = discord.Embed(title="", description=f"Эта роль вайфу уже надета.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            await message.author.add_roles(role_g)
            e = discord.Embed(title="Инвентарь", description=f"Вайфу <@&{role_g.id}> успешно была добавлена.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
            i = inv_items
            i[ri - 1] = { "type": "waifu", "id": item["id"], "equip": 1 }
            coll.update_one({ "disid": str(message.author.id), "guild": str(message.guild.id) }, { "$set": { "inv": i } })
        elif item["type"] == "background":
            card = item["id"]
            bgn_item = bgn.find_one({ "id": card }) 
            custom = self.bot.get_emoji(int(bgn_item["emoji"]))
            custom_name = bgn_item["name"]
            if card == inv["background"]:
                e = discord.Embed(title="", description=f"Эта карточка уже надета.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            coll.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "background": card } })
            e = discord.Embed(title="Инвентарь", description=f"Карточка {custom} **{custom_name}** успешно была надета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
        
    @commands.command(name="unequip", aliases=["uneq"])
    async def unequip(self, ctx, *messageArray):
        message = ctx.message
        coll = db.prof_ec_users
        bgn = db.backgrounds
        inv = coll.find_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" })
        len_inv = len(inv["inv"])
        inv_items = inv["inv"]
        ri = None
        item = None
        if len(messageArray) == 0 or messageArray[0] == "":
            e = discord.Embed(title="", description=f"Укажите индекс предмета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        try:
            ri = int(messageArray[0])
        except:
            e = discord.Embed(title="", description=f"Укажите индекс предмета.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        if ri > len_inv or ri == 0:
            e = discord.Embed(title="", description=f"Укажите индекс предмета в инвентаре.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            return await message.channel.send(embed = e)
        item = inv["inv"][ri - 1]
        if item["type"] == "role":
            role_g = message.guild.get_role(int(item["id"]))
            if role_g not in message.author.roles:
                e = discord.Embed(title="", description=f"Эта роль уже снята.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            await message.author.remove_roles(role_g)
            e = discord.Embed(title="Инвентарь", description=f"Роль <@&{role_g.id}> успешно была удалена.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)
        elif item["type"] == "waifu":
            items = list(inv_items)
            items = list(filter(lambda x: x["type"] == "waifu", items))
            items = list(filter(lambda x: x["equip"] == 1, items))
            role_g = message.guild.get_role(int(item["id"]))
            if role_g not in message.author.roles and items[0]["id"] != item["id"]:
                e = discord.Embed(title="", description=f"Эта роль вайфу уже снята.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            elif items[0]["id"] == item["id"] and role_g not in message.author.roles:
                e = discord.Embed(title="Инвентарь", description=f"Вайфу <@&{role_g.id}> успешно была снята системно.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed = e)
            else:
                await message.author.remove_roles(role_g)
                e = discord.Embed(title="Инвентарь", description=f"Вайфу <@&{role_g.id}> успешно была снята.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                await message.channel.send(embed = e)
            inv_items[ri - 1] = { "type": "waifu", "id": item["id"], "equip": 0 }
            coll.update_one({ "disid": str(message.author.id), "guild": str(message.guild.id) }, { "$set": { "inv": inv_items } })
        elif item["type"] == "background":
            card = item["id"]
            bgn_item = bgn.find_one({ "id": card }) 
            custom = self.bot.get_emoji(int(bgn_item["emoji"]))
            custom_name = bgn_item["name"]
            if card != inv["background"]:
                e = discord.Embed(title="", description=f"Эта карточка уже снята.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                return await message.channel.send(embed = e)
            coll.update_one({ "disid": str(message.author.id), "guild": f"{message.guild.id}" }, { "$set": { "background": 0 } })
            e = discord.Embed(title="Инвентарь", description=f"Карточка {custom} **{custom_name}** успешно была снята.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed = e)

    @commands.command(name="profile", aliases=["p", "prof"])
    #@commands.is_owner()
    async def profile(self, ctx, *messageArray):
        message = ctx.message
        users = db.prof_ec_users
        check = check_member(message.guild, messageArray)
        check_name = check_member_name(message, messageArray)
        temp_name = gen_promo(1, 9)
        week_stats = db.week_stats
        if week_stats.count_documents({ "id": f"{message.author.id}" }) == 0:
            week_stats.insert_one({ "id": f"{message.author.id}", "chat": 0, "voice": 0 })

        user = message.mentions[0] if len(message.mentions) != 0 else check if check is not None else check_name if check_name is not None else message.author

        if week_stats.count_documents({ "id": f"{user.id}" }) == 0:
            week_stats.insert_one({ "id": f"{user.id}", "chat": 0, "voice": 0 })

        prof = users.find_one({ "disid": str(user.id), "guild": f"{message.guild.id}" })
        exp = int(prof["exp"])
        nexp = int(prof["nexp"])
        level = str(prof["lvl"])
        avatar = str(user.avatar_url_as(format="png", size=1024))
        regex = r'((?:(https?|s?ftp):\/\/)?(?:www\.)?((?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)([A-Z]{2,6})|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(?::(\d{1,5}))?(?:(\/\S+)*))'
        find_urls_in_string = re.compile(regex, re.IGNORECASE)
        url_check = find_urls_in_string.search(avatar)
        if url_check.groups()[5].startswith('/embed'):
            avatar = Image.open('imgs/profile/no_image.png')
        else:
            resp = requests.get(avatar, stream=True)
            #resp.raw.decode_content = True
            try:
                avatar = Image.open(io.BytesIO(resp.content))
            except:
                avatar = Image.open('imgs/profile/no_image.png')


        bgused = prof["background"]

        bgs = db.backgrounds

        bg = bgs.find_one({ "id": bgused })

        imgt = None

        if bg["type"] == "cold":
            # print("cold")
            bgn = f"imgs/profile/background/cold/{bgused}.png"
            color = "#F6FFFF"
            imgt = "cold"
        else:
            # print("hot")
            bgn = f"imgs/profile/background/warm/{bgused}.png"
            color = "#F0ECE3"
            imgt = "hot"
        
        fon = Image.open(bgn)

        if prof["clan"] == "":
            clan_t = "«Отсутствует»"
            img = Image.open(f'imgs/profile/prof_noclan_{imgt}.png')
            clan = ImageFont.truetype('fonts/genshin.ttf', size=46)
        else:
            clans = db.clans
            clan_db = clans.find_one({ "id": int(prof["clan"]) })
            clan_t = clan_db["title"]
            img = Image.open(f'imgs/profile/prof_clan_{imgt}.png')
            clan = ImageFont.truetype('fonts/genshin.ttf', size=46)


        nickname = ImageFont.truetype('fonts/Comfortaa-Bold.ttf', size=82)
        status = ImageFont.truetype('fonts/genshin.ttf', size=52)
        xp = ImageFont.truetype('fonts/genshin.ttf', size=32)

        draw_text = ImageDraw.Draw(img)

        name = user.name # cleanname(user.name)

        wn = 35
        if len(name) >= 20:
            nickname = ImageFont.truetype('fonts/Comfortaa-Bold.ttf', size=45)
            wn = 50
        #if message.author.id == 252378040024301570:
        if user.guild_permissions.administrator and user.id != 554235984070574091:
            icon_A = Image.open('imgs/profile/icons/admin.png')
            fon.paste(icon_A, (498, 54), icon_A)
            draw_text.text(
                (570, wn),
                f'{name}',
                font=nickname,
                fill=color
            )
        else:
            draw_text.text(
                (498, wn),
                f'{name}',
                font=nickname,
                fill=color
            )
        #else:     
        #    draw_text.text(
        #        (498, wn),
        #        f'{name}',
        #        font=nickname,
        #        fill=color
        #    )

        ustatus = cleanname(prof["status"])

        astr = f'''{ustatus if ustatus else "Нет подписи"}'''

        draw_text.text(
            (498, 159),
            astr,
            font=status,
            fill=f"{color if ustatus != '' else '#a0b9d0'}"
        )


        level = prof["lvl"]

        wl, hl = draw_text.textsize(str(level), font=status)

        draw_text.text(
            (1440 - wl, 346),
            f'{level}',
            font=status,
            fill=color
        )



        exp = prof["exp"]
        nexp = prof["nexp"]

        percent = int(int(exp) / int(nexp) * 100)

        if percent > 0:

            len_level_draw = round(873 / 100 * percent) + 566

            draw = ImageDraw.Draw(img)
            draw.line((572, 478, len_level_draw, 478), fill="#5b8d52")
            for i in range(479, 494):
                draw.line((572, i, len_level_draw, i), fill="#c8df6f")
            draw.line((572, 493, len_level_draw, 493), fill="#5b8d52")
            draw.line((571, 478, 571, 493), fill="#5b8d52")
            if percent >= 100:
                draw.line((len_level_draw, 478, len_level_draw, 493), fill="#5b8d52")


        xp_t = f'{exp} / {nexp}'

        w, h = draw_text.textsize(xp_t, font=xp)

        draw_text.text(
            (1440 - w, 432),
            xp_t,
            font=xp,
            fill=color
        )

        week_stats = db.week_stats

        vtarr = [x for x in week_stats.find().sort("voice", -1).limit(100)]
        vtarrid = [x["id"] for x in vtarr]
        try:
            vt = vtarrid.index(f"{user.id}")

            if week_stats.count_documents({ "id": f"{user.id}" }) == 0:
                week_stats.insert_one({ "id": f"{user.id}", "chat": 0, "voice": 0 })
            if user.voice is not None:
                x = int(time.time())
                last = int(prof["last_time"])
                vctime = x - last
                vtarr[vt]["voice"] += vctime

            vtarr.sort(key = lambda x: x["voice"], reverse=True)
            vtarrid = [x["id"] for x in vtarr]
            vt = str(vtarrid.index(f"{user.id}") + 1)
        except:
            vt = "100+"
        
        ct = [x["id"] for x in week_stats.find().sort("chat", -1).limit(100)]
        try:
            ct = str(ct.index(f"{user.id}") + 1)
        except:
            ct = "100+"

        w, h = draw_text.textsize(vt, font=status)

        draw_text.text(
            (1440 - w, 528),
            vt,
            font=status,
            fill=color
        )

        w, h = draw_text.textsize(ct, font=status)

        draw_text.text(
            (1440 - w, 631),
            ct,
            font=status,
            fill=color
        )

        if prof["partner"] == "":
            married = "«Отсутствуют»"
        else:
            married = message.guild.get_member(int(prof["partner"]))
            if married is None:
                married = "«Не найдено»"
            else:
                married = married.name # cleanname(married.name)

        mstatus = ImageFont.truetype('fonts/Comfortaa-Bold.ttf', size=57)
        w, h = draw_text.textsize(married, font=mstatus)

        draw_text.text( 
            (1440 - w, 727),
            married,
            font=mstatus,
            fill=color
        )

        w, h = draw_text.textsize(clan_t, font=clan)

        # if user.id == 252378040024301570:
        #     clan_db2 = clans.find_one({ "id": 2 })
        #     clan_t2 = clan_db2["title"]
        #     wc2, hc2 = draw_text.textsize(clan_t2, font=clan)

        # if user.id == 322100536780259328:
        #     clan_db2 = clans.find_one({ "id": 1 })
        #     clan_t2 = clan_db2["title"]
        #     wc2, hc2 = draw_text.textsize(clan_t2, font=clan)

        draw_text.text(
            ((440+57-w)/2, 489),
            clan_t,
            font=clan,
            fill=color
        )

        # if user.id == 252378040024301570 or user.id == 322100536780259328:
        #     draw_text.text(
        #         ((440+57-wc2)/2, 549),
        #         clan_t2,
        #         font=clan,
        #         fill=color
        #     )

        size = avatar.size

        size = (256, 256)

        
        if avatar.mode != "RGBA":
            avatar = avatar.convert("RGBA")
        avatar = crop(avatar, size)
        avatar.putalpha(prepare_mask(size, 4))
        fon.paste(avatar, (121, 74), avatar)
        fon.paste(img, (0, 0), img)

        fon = fon.convert("RGB")

        fon.save(f"./profiles/{user.id}_{temp_name}.png")

        name_path = f"./profiles/{user.id}_{temp_name}.png"

        name_file = f"{user.id}_{temp_name}.png"

        file_img = discord.File(name_path, filename=name_file)

        e = discord.Embed(color=discord.Color(0x2F3136))

        e.set_author(name=f"Запрос от {message.author}", icon_url=message.author.avatar_url)
        e.set_footer(text=f"7* - ваше место в топе за 7 дней.")
        e.timestamp = datetime.datetime.utcnow()
        e.set_image(url=f"attachment://{name_file}")

        await message.channel.send(embed=e, file=file_img)

        os.remove(f"./profiles/{name_file}")

def setup(bot):
    bot.add_cog(User(bot))