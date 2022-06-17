import asyncio
import datetime
from async_timeout import timeout
from discord.ext.commands.core import cooldown
import pymongo
import sqlite3
import os
import discord
from discord.ext import commands
from discord_components import *
from plugins import funcb
import time
import random
import sys
sys.path.append("../../")
import config 
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
susers = db.prof_ec_users
sdb = db.u_settings

def is_channel_me():
    def predicate(ctx):
        return ctx.message.channel.id == 927296029336961134
    return commands.check(predicate)

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def throw(self, ctx):
        data = susers.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < config.reaction_one:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e)
        
        mm = ctx.message.mentions
        mm = list(filter(lambda x: x.bot is False and x.id != ctx.author.id, mm))
        if len(mm) == 0:
            member = None
        else:
            member = mm[0]

        if member is not None:
            user_m = susers.find_one({ "disid": str(member.id), "guild": str(ctx.guild.id) })

            if str(ctx.author.id) in user_m["ignore_list"]:
                member = None

        photo = [
            "https://cdn.discordapp.com/attachments/666234650758348820/918578028529995826/7584075476631eff251862bb9fc0cd7c.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578029083631666/original_29.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578029628887060/AdorableGreedyFlyingsquirrel-size_restricted.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578030174142485/tenor_17.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578030639742976/original_28.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578032078356540/CelebratedAridHake-size_restricted.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578032510373908/1120431665167b3b1a627b99466df51b.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578033055649863/original_27.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578033349234718/6ur-oQU86GICt3uuc4-q35LxZ5eecKn7xpNO9HdXwLpoa33ZsEwDachADt8oIu72aAoyroC1YPaXgFfNDGQkJw.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578051917443112/Omake_Gif_Anime_-_Sakura_Quest_-_Episode_20_-_Maki_Beans_Yoshino_with_Snowball.gif",
            "https://cdn.discordapp.com/attachments/666234650758348820/918578051472818236/1a5c4f2b2617e2d5adbb1366e4fdc2fd.gif"
        ]
        userwith = ""
        if member is None:
            miss = random.randint(0, 2)
            userwith = f"кидает снежки во всех. {'О нет, все увернулись от снежков, увы!' if miss == 0 else 'О нет, половина участников увернулась, как же так!' if miss == 1 else 'О да! Попадание во всех участников, какая же меткость! *ну или же удача c:*'}"
        else:
            miss = random.randint(0, 1)
            place = ['лоб. Мозги застудит! *если они там есть..* c:', 'тело. Чего так живот заболел?..', 'ноги! Координация пользователя потеряна c:', 'лицо, как же это больно!']
            userwith = f"кидает снежок в {member.mention}. {'О нет, пользователь смог увернуться!' if miss == 0 else f'Попадание! Прямо в {random.choice(place)}'}"
        e = discord.Embed(title="Реакция: кинуть снежок", description=f"{ctx.author.mention} {userwith}", color=discord.Color(0x2F3136))
        e.set_footer(text=f"{ctx.author.display_name} • {config.reaction_one} примогемов", icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        e.set_image(url=random.choice(photo))
        await ctx.send(embed=e)
        ms = data["moneystats"]
        ms["1d"] -= config.reaction_one
        ms["7d"] -= config.reaction_one
        ms["14d"] -= config.reaction_one
        ms["all"] -= config.reaction_one
        if ms["history_1d"]["reactions"]["view"] == 0:
            ms["history_1d"]["reactions"]["view"] = 1
        ms["history_1d"]["reactions"]["count"] -= config.reaction_one
        if ms["history"]["reactions"]["view"] == 0:
            ms["history"]["reactions"]["view"] = 1
        ms["history"]["reactions"]["count"] -= config.reaction_one

        susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - config.reaction_one, "moneystats": ms } })

    @commands.command()
    @commands.check_any(commands.is_nsfw(), is_channel_me())
    async def fuck(self, ctx):
        data = susers.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < 150:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e)
        
        if len(ctx.message.mentions) == 0 or ctx.message.mentions[0].bot:
            e = discord.Embed(title="", description=f"{ctx.author.mention}, укажи ник кого ты хочешь **трахнуть**.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=e)
        if ctx.message.mentions[0].id == ctx.author.id:
            e = discord.Embed(title="", description=f"{ctx.author.mention}, не лучшая идея.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=e)

        member = ctx.message.mentions[0]

        if sdb.count_documents({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) }) == 0:
                sdb.insert_one({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

        user_m_s = sdb.find_one({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })

        user_m = susers.find_one({ "disid": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })

        if user_m['partner'] != '' and user_m['partner'] != f"{ctx.author.id}" and user_m_s["deny_all_marry"] == 1 and ctx.author.id != 252378040024301570:
            e = discord.Embed(title="Авто-отказ", description="Данный пользователь сосотоит в браке.", color=discord.Color(0x2F3136))
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.channel.send(embed=e)

        if str(ctx.author.id) in user_m["ignore_list"]:
            return

        photo = f"https://cdn.filobot.xyz/assets/commands/fuck/{random.randint(1, 20)}.gif"
        if user_m['partner'] == f"{ctx.author.id}":
            e = discord.Embed(title="Реакция: трахнуть", description=f"{ctx.author.mention} трахнул(-а) {str(member.mention)}", color=discord.Color(0x2F3136))
            e.set_footer(text=f"{ctx.author.display_name} • 150 примогемов", icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=photo)
            await ctx.send(embed=e)
            ms = data["moneystats"]
            ms["1d"] -= 150
            ms["7d"] -= 150
            ms["14d"] -= 150
            ms["all"] -= 150
            if ms["history_1d"]["reactions"]["view"] == 0:
                ms["history_1d"]["reactions"]["view"] = 1
            ms["history_1d"]["reactions"]["count"] -= 150
            if ms["history"]["reactions"]["view"] == 0:
                ms["history"]["reactions"]["view"] = 1
            ms["history"]["reactions"]["count"] -= 150

            susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - 150, "moneystats": ms } })
        else:
            e = discord.Embed(color=0x2f3136, title="Реакция: трахнуть")
            e.description = f"{member.mention}, тебя хочет трахнуть {ctx.author.mention}. Что ответишь?"
            e.set_footer(text=f"{ctx.author.display_name} • 150 примогемов", icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            msg = await ctx.send(embed=e, components=[
                [
                    Button(emoji="✅", style=ButtonStyle.green, id='reaction_fuck_yes'),
                    Button(emoji="❌", style=ButtonStyle.red, id='reaction_fuck_no')
                ]
            ])
            try:
                i = await self.bot.wait_for("button_click", check=lambda i: i.component.id.startswith("reaction_fuck") and i.user.id == member.id, timeout=20.0)
                susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$inc": { "money": -150 } })
                if i.component.id == "reaction_fuck_yes":
                    e.description = f"{ctx.author.mention} трахнул(-а) {member.mention}"
                    e.set_image(url=photo)
                    await i.respond(type=7, embed=e, components=[])
                    ms = data["moneystats"]
                    ms["1d"] -= 150
                    ms["7d"] -= 150
                    ms["14d"] -= 150
                    ms["all"] -= 150
                    if ms["history_1d"]["reactions"]["view"] == 0:
                        ms["history_1d"]["reactions"]["view"] = 1
                    ms["history_1d"]["reactions"]["count"] -= 150
                    if ms["history"]["reactions"]["view"] == 0:
                        ms["history"]["reactions"]["view"] = 1
                    ms["history"]["reactions"]["count"] -= 150

                    susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "moneystats": ms } })
                else:
                    e.description = f"{member.mention} отказался(ась)."
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await i.respond(type=7, embed=e, components=[])
                    susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$inc": { "money": 150 } })
            except asyncio.TimeoutError:
                e.description = f"{member.mention} проигнорировал(-а) данное предложение."
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await msg.edit(embed=e, components=[])
                susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$inc": { "money": 150 } })
    
    @commands.command()
    @commands.check_any(commands.is_nsfw(), is_channel_me())
    async def suck(self, ctx):
        data = susers.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < 150:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e)

        if len(ctx.message.mentions) == 0 or ctx.message.mentions[0].bot:
            e = discord.Embed(title="", description=f"{ctx.author.mention}, укажи ник кого у кого ты хочешь **отсосать**.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=e)
        if ctx.message.mentions[0].id == ctx.author.id:
            e = discord.Embed(title="", description=f"{ctx.author.mention}, не лучшая идея.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=e)

        if sdb.count_documents({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) }) == 0:
                sdb.insert_one({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

        user_m_s = sdb.find_one({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })
        user_m = susers.find_one({ "disid": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })

        if user_m['partner'] != '' and user_m['partner'] != f"{ctx.author.id}" and user_m_s["deny_all_marry"] == 1 and ctx.author.id != 252378040024301570:
            e = discord.Embed(title="Авто-отказ", description="Данный пользователь сосотоит в браке.", color=discord.Color(0x2F3136))
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.channel.send(embed=e)

        if str(ctx.author.id) in user_m["ignore_list"]:
            return

        member = ctx.message.mentions[0]

        photo = f"https://cdn.filobot.xyz/assets/commands/suck/{random.randint(1, 20)}.gif"
        if user_m['partner'] == f"{ctx.author.id}":
            e = discord.Embed(title="Реакция: отсосать", description=f"{ctx.author.mention} отсосал(-а) у {str(member.mention)}", color=discord.Color(0x2F3136))
            e.set_footer(text=f"{ctx.author.display_name} • 150 примогемов", icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=photo)
            await ctx.send(embed=e)
            ms = data["moneystats"]
            ms["1d"] -= 150
            ms["7d"] -= 150
            ms["14d"] -= 150
            ms["all"] -= 150
            if ms["history_1d"]["reactions"]["view"] == 0:
                ms["history_1d"]["reactions"]["view"] = 1
            ms["history_1d"]["reactions"]["count"] -= 150
            if ms["history"]["reactions"]["view"] == 0:
                ms["history"]["reactions"]["view"] = 1
            ms["history"]["reactions"]["count"] -= 150

            susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - 150, "moneystats": ms } })
        else:
            e = discord.Embed(color=0x2f3136, title="Реакция: отсосать")
            e.description = f"{member.mention}, у тебя хочет отсосать {ctx.author.mention}. Что ответишь?"
            e.set_footer(text=f"{ctx.author.display_name} • 150 примогемов", icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            msg = await ctx.send(embed=e, components=[
                [
                    Button(emoji="✅", style=ButtonStyle.green, id='reaction_suck_yes'),
                    Button(emoji="❌", style=ButtonStyle.red, id='reaction_suck_no')
                ]
            ])
            try:
                i = await self.bot.wait_for("button_click", check=lambda i: i.component.id.startswith("reaction_suck") and i.user.id == member.id, timeout=20.0)
                susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$inc": { "money": -150 } })
                if i.component.id == "reaction_suck_yes":
                    e.description = f"{ctx.author.mention} отсосал(-а) у {member.mention}"
                    e.set_image(url=photo)
                    await i.respond(type=7, embed=e, components=[])
                    ms = data["moneystats"]
                    ms["1d"] -= 150
                    ms["7d"] -= 150
                    ms["14d"] -= 150
                    ms["all"] -= 150
                    if ms["history_1d"]["reactions"]["view"] == 0:
                        ms["history_1d"]["reactions"]["view"] = 1
                    ms["history_1d"]["reactions"]["count"] -= 150
                    if ms["history"]["reactions"]["view"] == 0:
                        ms["history"]["reactions"]["view"] = 1
                    ms["history"]["reactions"]["count"] -= 150

                    susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "moneystats": ms } })
                else:
                    e.description = f"{member.mention} отказался(ась)."
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await i.respond(type=7, embed=e, components=[])
                    susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$inc": { "money": 150 } })
            except asyncio.TimeoutError:
                e.description = f"{member.mention} проигнорировал(-а) данное предложение."
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await msg.edit(embed=e, components=[])
                susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$inc": { "money": 150 } })

    @commands.command()
    @commands.check_any(commands.is_nsfw(), is_channel_me())
    async def cum(self, ctx):
        data = susers.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < 150:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e)
        
        withcum = ""

        if len(ctx.message.mentions) > 0:
            if ctx.message.mentions[0].id != ctx.author.id:
                user_m = susers.find_one({ "disid": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })

                if str(ctx.author.id) not in user_m["ignore_list"]:
                    withcum = f" из-за {ctx.message.mentions[0].mention}"

        photo = f"https://cdn.filobot.xyz/assets/commands/cum/{random.randint(1, 20)}.gif"
        e = discord.Embed(title="Реакция: кончить", description=f"{ctx.author.mention} кончил(-а){withcum}", color=discord.Color(0x2F3136))
        e.set_footer(text=f"{ctx.author.display_name} • 150 примогемов", icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        e.set_image(url=photo)
        await ctx.send(embed=e)
        ms = data["moneystats"]
        ms["1d"] -= 150
        ms["7d"] -= 150
        ms["14d"] -= 150
        ms["all"] -= 150
        if ms["history_1d"]["reactions"]["view"] == 0:
            ms["history_1d"]["reactions"]["view"] = 1
        ms["history_1d"]["reactions"]["count"] -= 150
        if ms["history"]["reactions"]["view"] == 0:
            ms["history"]["reactions"]["view"] = 1
        ms["history"]["reactions"]["count"] -= 150

        susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - 150, "moneystats": ms } })
    
    @commands.command()
    @commands.check_any(commands.is_nsfw(), is_channel_me())
    async def kuni(self, ctx):

        data = susers.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < 150:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e)

        if len(ctx.message.mentions) == 0 or ctx.message.mentions[0].bot:
            e = discord.Embed(title="", description=f"{ctx.author.mention}, укажи ник у кого ты хочешь **отлизать**.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=e)
        if ctx.message.mentions[0].id == ctx.author.id:
            e = discord.Embed(title="", description=f"{ctx.author.mention}, не лучшая идея.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=e)
        

        if sdb.count_documents({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) }) == 0:
                sdb.insert_one({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

        user_m_s = sdb.find_one({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })
        user_m = susers.find_one({ "disid": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })

        if user_m['partner'] != '' and user_m['partner'] != f"{ctx.author.id}" and user_m_s["deny_all_marry"] == 1 and ctx.author.id != 252378040024301570:
            e = discord.Embed(title="Авто-отказ", description="Данный пользователь сосотоит в браке.", color=discord.Color(0x2F3136))
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.channel.send(embed=e)

        if str(ctx.author.id) in user_m["ignore_list"]:
            return

        member = ctx.message.mentions[0]

        photo = f"https://cdn.filobot.xyz/assets/commands/kuni/{random.randint(1, 20)}.gif"
        if user_m['partner'] == f"{ctx.author.id}":
            e = discord.Embed(title="Реакция: отлизать", description=f"{ctx.author.mention} отлизал(-а) у {str(member.mention)}", color=discord.Color(0x2F3136))
            e.set_footer(text=f"{ctx.author.display_name} • 150 примогемов", icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=photo)
            await ctx.send(embed=e)
            ms = data["moneystats"]
            ms["1d"] -= 150
            ms["7d"] -= 150
            ms["14d"] -= 150
            ms["all"] -= 150
            if ms["history_1d"]["reactions"]["view"] == 0:
                ms["history_1d"]["reactions"]["view"] = 1
            ms["history_1d"]["reactions"]["count"] -= 150
            if ms["history"]["reactions"]["view"] == 0:
                ms["history"]["reactions"]["view"] = 1
            ms["history"]["reactions"]["count"] -= 150

            susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - 150, "moneystats": ms } })
        else:
            e = discord.Embed(color=0x2f3136, title="Реакция: отзлизать")
            e.description = f"{member.mention}, у тебя хочет отлизать {ctx.author.mention}. Что ответишь?"
            e.set_footer(text=f"{ctx.author.display_name} • 150 примогемов", icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            msg = await ctx.send(embed=e, components=[
                [
                    Button(emoji="✅", style=ButtonStyle.green, id='reaction_kuni_yes'),
                    Button(emoji="❌", style=ButtonStyle.red, id='reaction_kuni_no')
                ]
            ])
            ms = data["moneystats"]
            ms["1d"] -= 150
            ms["7d"] -= 150
            ms["14d"] -= 150
            ms["all"] -= 150
            if ms["history_1d"]["reactions"]["view"] == 0:
                ms["history_1d"]["reactions"]["view"] = 1
            ms["history_1d"]["reactions"]["count"] -= 150
            if ms["history"]["reactions"]["view"] == 0:
                ms["history"]["reactions"]["view"] = 1
            ms["history"]["reactions"]["count"] -= 150

            susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - 150, "moneystats": ms } })
            try:
                i = await self.bot.wait_for("button_click", check=lambda i: i.component.id.startswith("reaction_kuni") and i.user.id == member.id, timeout=20.0)
                susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$inc": { "money": -150 } })
                if i.component.id == "reaction_kuni_yes":
                    e.description = f"{ctx.author.mention} отлизал(-а) у {member.mention}"
                    e.set_image(url=photo)
                    await i.respond(type=7, embed=e, components=[])
                    ms = data["moneystats"]
                    ms["1d"] -= 150
                    ms["7d"] -= 150
                    ms["14d"] -= 150
                    ms["all"] -= 150
                    if ms["history_1d"]["reactions"]["view"] == 0:
                        ms["history_1d"]["reactions"]["view"] = 1
                    ms["history_1d"]["reactions"]["count"] -= 150
                    if ms["history"]["reactions"]["view"] == 0:
                        ms["history"]["reactions"]["view"] = 1
                    ms["history"]["reactions"]["count"] -= 150

                    susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "moneystats": ms } })
                else:
                    e.description = f"{member.mention} отказался(ась)."
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    await i.respond(type=7, embed=e, components=[])
                    susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$inc": { "money": 150 } })
            except asyncio.TimeoutError:
                e.description = f"{member.mention} проигнорировал(-а) данное предложение."
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await msg.edit(embed=e, components=[])
                susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$inc": { "money": 150 } })

    @commands.command()
    async def drink(self, ctx):
        coll = db.prof_ec_users
        data = coll.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < config.reaction_one:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e)
        else:
            money_emoji = self.bot.get_emoji(746756714484727828)
            photo = [
                        "https://cdn.discordapp.com/attachments/856960219052638248/900083834547224636/1488910524_giphy-1.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900083837256740956/Anime-anime-gif-Uzaki-chan-wa-Asobitai----6127583.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900083839563599912/OK6W_koKDTOqqqLDbIoPAtdwEn95KKfg6-0TqY1AJtA.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900083841711112212/anime-girl.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900083848388440104/CharmingGeneralIrishwolfhound-size_restricted.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900083855241920512/d4975ac96cb2d0cf987c447b82c96afa.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900085469897953320/original.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900085653843370004/171021_1866.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900085658436141106/Omake_Gif_Anime_-_Osake_wa_Fuufu_ni_Natte_Kara_-_Episode_6_-_Yui_Drowns_Her_Sorrows.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900085793371091004/OfficialFlashyHorsemouse-size_restricted.gif",
                        "https://cdn.discordapp.com/attachments/856960219052638248/900085802070073384/Noragami-OVA-episodio-2-Yato-e-Bishamon.gif"
                    ]

            userwith = ""

            mm = ctx.message.mentions
            if len(mm) > 0:
                while ctx.author in mm:
                    mm.remove(ctx.author)

                user_m = susers.find_one({ "disid": str(mm[0].id), "guild": str(ctx.guild.id) })

                if str(ctx.author.id) not in user_m["ignore_list"]:
                    userwith = f" c <@!{mm[0].id}>"

            e = discord.Embed(title="Реакция: выпивать", description=f"<@{str(ctx.author.id)}> пьёт{userwith}", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{ctx.author.display_name} • {config.reaction_one} примогемов", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
            ms = data["moneystats"]
            ms["1d"] -= config.reaction_one
            ms["7d"] -= config.reaction_one
            ms["14d"] -= config.reaction_one
            ms["all"] -= config.reaction_one
            if ms["history_1d"]["reactions"]["view"] == 0:
                ms["history_1d"]["reactions"]["view"] = 1
            ms["history_1d"]["reactions"]["count"] -= config.reaction_one
            if ms["history"]["reactions"]["view"] == 0:
                ms["history"]["reactions"]["view"] = 1
            ms["history"]["reactions"]["count"] -= config.reaction_one

            susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - config.reaction_one, "moneystats": ms } })

    @commands.command()
    async def angry(self, ctx):
        coll = db.prof_ec_users
        data = coll.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < config.reaction_one:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e)
        else:
            money_emoji = self.bot.get_emoji(746756714484727828)
            photo = ["https://cdn.discordapp.com/attachments/666234650758348820/712229640084652092/orig_4.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712229646938406932/orig_3.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712229646930018374/tenor_7.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712229651384107028/tenor_8.gif",
                    "https://cdn.discordapp.com/attachments/666234650758348820/712229651506003978/tenor_9.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826447627453333584/844ae17aaa1920db86bacc44767202f7.gif",
                    "https://cdn.discordapp.com/attachments/811515393860042773/826447667563331584/79621a0ecaef96b0ae412aa9ca79463a.gif"
                    ]

            userwith = ""

            mm = ctx.message.mentions
            if len(mm) > 0:
                while ctx.author in mm:
                    mm.remove(ctx.author)

                user_m = susers.find_one({ "disid": str(mm[0].id), "guild": str(ctx.guild.id) })

                if str(ctx.author.id) not in user_m["ignore_list"]:
                    userwith = f" из-за <@!{mm[0].id}>"

            e = discord.Embed(title="Реакция: злиться", description=f"<@{str(ctx.author.id)}> злится{userwith}", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{ctx.author.display_name} • {config.reaction_one} примогемов", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
            ms = data["moneystats"]
            ms["1d"] -= config.reaction_one
            ms["7d"] -= config.reaction_one
            ms["14d"] -= config.reaction_one
            ms["all"] -= config.reaction_one
            if ms["history_1d"]["reactions"]["view"] == 0:
                ms["history_1d"]["reactions"]["view"] = 1
            ms["history_1d"]["reactions"]["count"] -= config.reaction_one
            if ms["history"]["reactions"]["view"] == 0:
                ms["history"]["reactions"]["view"] = 1
            ms["history"]["reactions"]["count"] -= config.reaction_one

            susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - config.reaction_one, "moneystats": ms } })

    @commands.command()
    async def bite(self, ctx):
        coll = db.prof_ec_users
        data = coll.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < config.reaction_two:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e)
        else:
            money_emoji = self.bot.get_emoji(746756714484727828)
            if len(ctx.message.mentions) == 0:
                photo = ["https://media.discordapp.net/attachments/666234650758348820/712204563033096202/original_2.gif",
                        "https://media.discordapp.net/attachments/666234650758348820/712204566296264704/original_3.gif",
                        "https://media.discordapp.net/attachments/666234650758348820/712204567407755335/ezgif-126620093.gif",
                        "https://media.discordapp.net/attachments/666234650758348820/712204566518562887/9fjF.gif",
                        "https://media.discordapp.net/attachments/666234650758348820/712204568989007911/ce71c977d33284c485e21c95096a9ccadb7f2941_hq.gif",
                        "https://media.discordapp.net/attachments/666234650758348820/712204569857490954/tenor_4.gif",
                        "https://media.discordapp.net/attachments/768157522825183263/823305703003390052/tenor_1.gif"
                        ]

                e = discord.Embed(title="Реакция: укусить", description=f"<@{str(ctx.author.id)}> укусил(-а) всех.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_image(url=random.choice(photo))
                e.set_footer(text=f"{ctx.author.display_name} • {config.reaction_two} примогемов", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            if ctx.message.mentions[0].id == ctx.author.id:
                e = discord.Embed(title="", description=f"<@{str(ctx.author.id)}>, не лучшая идея.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            photo = ["https://media.discordapp.net/attachments/666234650758348820/712204563033096202/original_2.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712204566296264704/original_3.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712204567407755335/ezgif-126620093.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712204566518562887/9fjF.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712204568989007911/ce71c977d33284c485e21c95096a9ccadb7f2941_hq.gif",
                    "https://media.discordapp.net/attachments/666234650758348820/712204569857490954/tenor_4.gif",
                    "https://media.discordapp.net/attachments/768157522825183263/823305703003390052/tenor_1.gif"
                    ]

            user_m = susers.find_one({ "disid": f"{ctx.message.mentions[0].id}", "guild": f"{ctx.guild.id}" })

            if str(ctx.author.id) in user_m["ignore_list"]:
                return None

            e = discord.Embed(title="Реакция: укусить", description=f"<@{str(ctx.author.id)}> укусил(-а) <@{str(ctx.message.mentions[0].id)}>", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_image(url=random.choice(photo))
            e.set_footer(text=f"{ctx.author.display_name} • {config.reaction_two} примогемов", icon_url=ctx.author.avatar_url)
            await ctx.channel.send(embed=e)
            
            ms = data["moneystats"]
            ms["1d"] -= config.reaction_two
            ms["7d"] -= config.reaction_two
            ms["14d"] -= config.reaction_two
            ms["all"] -= config.reaction_two
            if ms["history_1d"]["reactions"]["view"] == 0:
                ms["history_1d"]["reactions"]["view"] = 1
            ms["history_1d"]["reactions"]["count"] -= config.reaction_two
            if ms["history"]["reactions"]["view"] == 0:
                ms["history"]["reactions"]["view"] = 1
            ms["history"]["reactions"]["count"] -= config.reaction_two

            db.prof_ec_users.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - config.reaction_two, "moneystats": ms } })

    @commands.command()
    async def cheek(self, ctx):

        if sdb.count_documents({ "id": str(ctx.author.id), "guild": str(ctx.guild.id) }) == 0:
            sdb.insert_one({ "id": str(ctx.author.id), "guild": str(ctx.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

        coll = db.prof_ec_users
        data = coll.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < config.reaction_two:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e) 
        else:
            if len(ctx.message.mentions) == 0:
                e = discord.Embed(title="", description=f"<@{str(ctx.author.id)}>, укажи ник кого ты хочешь **поцеловать в щёку**.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            if ctx.message.mentions[0].id == ctx.author.id:
                e = discord.Embed(title="", description=f"<@{str(ctx.author.id)}>, не лучшая идея.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)

            if sdb.count_documents({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) }) == 0:
                sdb.insert_one({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

            user_m_s = sdb.find_one({ "id": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })
            user_m = susers.find_one({ "disid": str(ctx.message.mentions[0].id), "guild": str(ctx.guild.id) })

            if str(ctx.author.id) in user_m["ignore_list"]:
                return None

            if user_m["partner"] != "":
                if user_m["partner"] == str(ctx.author.id):
                    if user_m_s["command_cheek_marry"] == 0:
                        photo = config.cheek
                        e = discord.Embed(title="Реакция: поцелуй в щёку", description=f"<@{str(ctx.author.id)}> поцеловал(-а) **в щёку** <@{str(ctx.message.mentions[0].id)}>", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{ctx.author.display_name} • {config.reaction_two} примогемов", icon_url=ctx.author.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_image(url=random.choice(photo))
                        author_m = susers.find_one({"disid": str(ctx.author.id), "guild": f"{ctx.guild.id}"})
                        ms = author_m["moneystats"]
                        ms["1d"] -= config.reaction_two
                        ms["7d"] -= config.reaction_two
                        ms["14d"] -= config.reaction_two
                        ms["all"] -= config.reaction_two
                        if ms["history_1d"]["reactions"]["view"] == 0:
                            ms["history_1d"]["reactions"]["view"] = 1
                        ms["history_1d"]["reactions"]["count"] -= config.reaction_two
                        if ms["history"]["reactions"]["view"] == 0:
                            ms["history"]["reactions"]["view"] = 1
                        ms["history"]["reactions"]["count"] -= config.reaction_two
                        susers.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": author_m["money"] - config.reaction_two, "moneystats": ms } })
                        return await ctx.channel.send(embed=e)
                else:
                    if user_m_s["deny_all_marry"] == 1:
                        e = discord.Embed(title="Авто-отказ", description="Данный пользователь запретил использовать на себе эту команду всем, кроме партнера в браке.", color=discord.Color(0x2F3136))
                        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        return await ctx.channel.send(embed=e)
            e = discord.Embed(title="Реакция: поцелуй в щёку", description=f"<@{str(ctx.message.mentions[0].id)}>, тебя хочет **поцеловать в щёку** <@{ctx.author.id}>. Что ответишь?", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            message_s = await ctx.channel.send(embed=e)
            await message_s.add_reaction("✅")
            await message_s.add_reaction("❌")
            author_m = db.prof_ec_users.find_one({"disid": str(ctx.author.id), "guild": f"{ctx.guild.id}"})
            ms = author_m["moneystats"]
            ms["1d"] -= config.reaction_two
            ms["7d"] -= config.reaction_two
            ms["14d"] -= config.reaction_two
            ms["all"] -= config.reaction_two
            if ms["history_1d"]["reactions"]["view"] == 0:
                ms["history_1d"]["reactions"]["view"] = 1
            ms["history_1d"]["reactions"]["count"] -= config.reaction_two
            if ms["history"]["reactions"]["view"] == 0:
                ms["history"]["reactions"]["view"] = 1
            ms["history"]["reactions"]["count"] -= config.reaction_two
            db.prof_ec_users.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": author_m["money"] - config.reaction_two, "moneystats": ms } })
            coll = db.reactions
            coll.insert_one({"message_id": str(message_s.id), "id": str(ctx.author.id), "mention_id": str(ctx.message.mentions[0].id), "time": int(time.time()) + 30, "react": 2, "guild_id": str(ctx.guild.id), "channel_id": str(ctx.channel.id), "type": "reaction"})

    
    # @commands.command()
    # @commands.is_owner()
    # @commands.cooldown(1, 15, commands.BucketType.user)
    # async def duel(self, ctx, *messageArray):
    #     if ctx.author.id == 518427777523908608:
    #         return await ctx.message.delete()
    #     message = ctx.message
    #     money_emoji = self.bot.get_emoji(775362271085461565)
    #     coll = db.prof_ec_users
    #     data = coll.find_one({"disid": str(message.author.id), "guild": str(message.guild.id)})
    #     if (len(messageArray) == 0 or messageArray[0] == "") or len(message.mentions) == 0:
    #         e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, укажи ник кому ты хочешь предложить **дуэль**.", color=discord.Color(0x2F3136))
    #         e.timestamp = datetime.datetime.utcnow()
    #         e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #         ctx.command.reset_cooldown(ctx)
    #         return await message.channel.send(embed=e)
    #     if len(messageArray) < 2 or messageArray[1] == "":
    #         e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, укажи сумму.", color=discord.Color(0x2F3136))
    #         e.timestamp = datetime.datetime.utcnow()
    #         e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #         ctx.command.reset_cooldown(ctx)
    #         return await message.channel.send(embed=e)
    #     try:
    #         sum = int(messageArray[1])
    #     except:
    #         e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, укажи сумму.", color=discord.Color(0x2F3136))
    #         e.timestamp = datetime.datetime.utcnow()
    #         e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #         ctx.command.reset_cooldown(ctx)
    #         return await message.channel.send(embed=e)
    #     if data["money"] < sum:
    #         e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
    #         e.timestamp = datetime.datetime.utcnow()
    #         e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #         ctx.command.reset_cooldown(ctx)
    #         return await message.channel.send(embed = e)
    #     elif sum <= 0:
    #         e = discord.Embed(title="", description=f"Укажите сумму более 0.", color=discord.Color(0x2F3136))
    #         e.timestamp = datetime.datetime.utcnow()
    #         e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #         ctx.command.reset_cooldown(ctx)
    #         return await message.channel.send(embed = e)
    #     else:

    #         if len(message.mentions) == 0 or message.mentions[0].bot:
    #             e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, укажи ник кому ты хочешь предложить **дуэль**.", color=discord.Color(0x2F3136))
    #             e.timestamp = datetime.datetime.utcnow()
    #             e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #             ctx.command.reset_cooldown(ctx)
    #             return await message.channel.send(embed=e)
    #         if message.mentions[0].id == message.author.id:
    #             e = discord.Embed(title="", description=f"<@{str(message.author.id)}>, ты не можешь предложить дуэль сам(-а) себе.", color=discord.Color(0x2F3136))
    #             e.timestamp = datetime.datetime.utcnow()
    #             e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #             ctx.command.reset_cooldown(ctx)
    #             return await message.channel.send(embed=e)
    #         if message.mentions[0].id == 518427777523908608:
    #             ctx.command.reset_cooldown(ctx)
    #             return await message.delete()
    #         mention_m = db.prof_ec_users.find_one({"disid": str(message.mentions[0].id), "guild": f"{message.guild.id}"})["money"]
    #         user_m = susers.find_one({ "disid": f"{message.mentions[0].id}", "guild": f"{message.guild.id}" })

    #         if str(message.author.id) in user_m["ignore_list"]:
    #             return None
    #         react = db.reactions
    #         if sum > 10000 and str(message.author.id) not in config.ADMINS:
    #             e = discord.Embed(title="", description=f"Временно невозможны дуэли на суммы более 10.000.", color=discord.Color(0x2F3136))
    #             e.timestamp = datetime.datetime.utcnow()
    #             e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #             ctx.command.reset_cooldown(ctx)
    #             return await ctx.send(embed = e)
            
    #         if mention_m < sum:
    #             e = discord.Embed(title="", description=f"Недостаточно примогемов у противника.", color=discord.Color(0x2F3136))
    #             e.timestamp = datetime.datetime.utcnow()
    #             e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #             ctx.command.reset_cooldown(ctx)
    #             return await ctx.send(embed=e)
    #         e = discord.Embed(title="Реакция: дуэль", description=f"<@{str(message.mentions[0].id)}>, тебе предложил(-а) дуэль <@{message.author.id}> на {sum}{money_emoji}. Что ответишь?", color=discord.Color(0x2F3136))
    #         e.timestamp = datetime.datetime.utcnow()
    #         e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    #         message_s = await message.channel.send(embed=e)
    #         await message_s.add_reaction("✅")
    #         await message_s.add_reaction("❌")
    #         con = sqlite3.connect('duels.db', check_same_thread=False)
    #         cur = con.cursor()
    #         cur.execute(f"INSERT INTO duels VALUES({message_s.id}, {message.author.id}, {message.mentions[0].id}, {int(time.time()) + 15}, {message.guild.id}, {message.channel.id}, {sum}, 'wait')")
    #         con.commit()
    #         con.close()
    
    @commands.command()
    async def bondage(self, ctx, *messageArray):
        coll = db.prof_ec_users
        data = coll.find_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)})
        if data["money"] < config.reaction_two:
            e = discord.Embed(title="", description=f"Недостаточно примогемов.", color=discord.Color(0x2F3136))
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.channel.send(embed = e)
        else:
            money_emoji = self.bot.get_emoji(746756714484727828)
            if len(ctx.message.mentions) == 0:
                e = discord.Embed(title="Реакции", description=f"Укажите пользователя.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)
            if ctx.message.mentions[0].id == ctx.author.id:
                e = discord.Embed(title="", description=f"<@{str(ctx.author.id)}>, не лучшая идея.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)

            
            photo = [
                "https://cdn.discordapp.com/attachments/875437092006658089/877994984329072650/2021-08-19-22-59-41.gif",
                "https://cdn.discordapp.com/attachments/875437092006658089/877994984819798066/2021-08-19-23-00-58.gif",
                "https://media.discordapp.net/attachments/875437092006658089/877994985235050566/2021-08-19-23-03-30.gif",
                "https://cdn.discordapp.com/attachments/875437092006658089/877994986447179856/2021-08-19-23-06-53.gif",
                "https://cdn.discordapp.com/attachments/875437092006658089/877995879699734538/2021-08-19-23-21-15.gif",
                "https://cdn.discordapp.com/attachments/875437092006658089/877996743533408256/2021-08-19-23-22-52.gif"
            ]

            user_m = susers.find_one({ "disid": f"{ctx.message.mentions[0].id}", "guild": f"{ctx.guild.id}" })

            if str(ctx.author.id) in user_m["ignore_list"]:
                return None

            if user_m["partner"] != "":
                if user_m["partner"] == str(ctx.author.id):
                    e = discord.Embed(title="Реакция: связать", description=f"<@{str(ctx.author.id)}> связал(-а) <@{str(ctx.message.mentions[0].id)}>", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_image(url=random.choice(photo))
                    e.set_footer(text=f"{ctx.author.display_name} • {config.reaction_two} примогемов", icon_url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=e)
                    
                    ms = data["moneystats"]
                    ms["1d"] -= config.reaction_two
                    ms["7d"] -= config.reaction_two
                    ms["14d"] -= config.reaction_two
                    ms["all"] -= config.reaction_two
                    if ms["history_1d"]["reactions"]["view"] == 0:
                        ms["history_1d"]["reactions"]["view"] = 1
                    ms["history_1d"]["reactions"]["count"] -= config.reaction_two
                    if ms["history"]["reactions"]["view"] == 0:
                        ms["history"]["reactions"]["view"] = 1
                    ms["history"]["reactions"]["count"] -= config.reaction_two

                    db.prof_ec_users.update_one({"disid": str(ctx.author.id), "guild": str(ctx.guild.id)}, { "$set": { "money": data['money'] - config.reaction_two, "moneystats": ms } })
                else:
                    e = discord.Embed(title="Реакции", description=f"Данная команда доступна только для пользователей в браке.", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                    return await ctx.channel.send(embed=e)
            else:
                e = discord.Embed(title="Реакции", description=f"Данная команда доступна только для пользователей в браке.", color=discord.Color(0x2F3136))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                return await ctx.channel.send(embed=e)

    """
    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()
    
    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()
    
    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()

    @commands.command()
    """

def setup(bot):
    bot.add_cog(Reactions(bot))