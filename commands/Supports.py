import datetime
import discord
from discord_components import Select, SelectOption, Button, ButtonStyle
from discord.utils import get
from discord.ext import commands
import pymongo
import sys
import random
import string
import asyncio
import time
sys.path.append("../../")
import config
mc = pymongo.MongoClient(config.uri2)
db = mc.aimi
supports_stats = db.supports_stats
support_settings = db.support_settings

def create_uid():
    """ Создаёт UID из 6 символов"""
    numbers = [str(random.randint(0, 9)) for i in range(3)]
    letters = [random.choice(list(string.ascii_lowercase)) for i in range(3)]
    uid_list = numbers + letters
    random.shuffle(uid_list)
    return "".join(uid_list)

def seconds_to_hh_mm_ss(seconds):
    " Convert seconds to d hh:mm:ss "
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}дн. {h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{h:02d}:{m:02d}:{s:02d}"

async def supports_check(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        support_settings_info = support_settings.find_one({"id": "604083589570625555"})
        time_check = support_settings_info["time_check"]
        if int(time.time()) - time_check >= 604800:
            supports = supports_stats.find({})
            guild = bot.get_guild(604083589570625555)
            support_role = guild.get_role(823234604550062102)
            prime_role = guild.get_role(827278746205683802)
            for support in supports:
                member = guild.get_member(int(support["id"]))
                if not member:
                    supports_stats.delete_one({ "id": support["id"] })
                    continue
                if support_role not in member.roles and prime_role not in member.roles:
                    supports_stats.delete_one({ "id": f"{member.id}" })
                    continue
            support_settings.update_one({"id": "604083589570625555"}, { "$inc": { "time_check": 604800 } })

        await asyncio.sleep(60)

async def supports_delete_stats(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        support_settings_info = support_settings.find_one({"id": "604083589570625555"})
        time_delete_7d = support_settings_info["time_delete_stats_7d"]
        time_delete_30d = support_settings_info["time_delete_stats_30d"]
        if int(time.time()) - time_delete_7d >= 604800:
            supports_stats.update_many({}, { "$set": { "7d": { "tickets": 0, "voice": 0, "chat": 0, "rating": [] } } })
            support_settings.update_one({"id": "604083589570625555"}, { "$inc": { "time_delete_stats_7d": 604800 } })
        if int(time.time()) - time_delete_30d >= 2592000:
            supports_stats.update_many({}, { "$set": { "30d": { "tickets": 0, "voice": 0, "chat": 0, "rating": [] } } })
            support_settings.update_one({"id": "604083589570625555"}, { "$inc": { "time_delete_stats_30d": 2592000 } })

        await asyncio.sleep(60)

class SupportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, b, a):
        b_roles = set(b.roles)
        a_roles = set(a.roles)
        if len(a.roles) > len(b.roles):
            diff = list(a_roles-b_roles)[0]
        else:
            return
        if diff.id == 827278746205683802 or diff.id == 823234604550062102:
            if supports_stats.count_documents({ "id": f"{a.id}" }) == 0:
                supports_stats.insert_one({
                    "id": f"{a.id}",
                    "tickets": 0,
                    "chat": 0,
                    "voice": 0,
                    "rating": [],
                    "voice_start": 0,
                    "7d": {
                        "tickets": 0,
                        "voice": 0,
                        "chat": 0,
                        "rating": []    
                    },
                    "30d": {
                        "tickets": 0,
                        "voice": 0,
                        "chat": 0,
                        "rating": []
                    }
                })

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, b, a):
        if member is None:
            return
        if member.bot:
            return
        support_role = member.guild.get_role(823234604550062102)
        prime_role = member.guild.get_role(827278746205683802)
        # if support_role not in member.roles and prime_role not in member.roles:
        #     return
        if a.channel:
            if a.channel.category.id != 823234023593213952:
                return
            if a.channel.id == 828276719215181875:
                return
            ch = a.channel
            if support_role in member.roles or prime_role in member.roles:
                members = list(filter(lambda x: support_role not in x.roles and prime_role not in x.roles, ch.members))
                if len(members) == 0:
                    return
                else:
                    supports_stats.update_one({ "id": f"{member.id}" }, { "$set": { "voice_start": int(time.time()) } })
            else:
                members = ch.members
                if len(members) == 1:
                    return
                else:
                    members_sup = list(filter(lambda x: support_role in x.roles or prime_role in x.roles, ch.members))
                    for member in members_sup:
                        supports_stats.update_one({ "id": f"{member.id}" }, { "$set": { "voice_start": int(time.time()) } })
        if b.channel:
            if b.channel.category.id != 823234023593213952:
                return
            if b.channel.id == 828276719215181875:
                return
            ch = b.channel
            if support_role in member.roles or prime_role in member.roles:
                members = list(filter(lambda x: support_role not in x.roles and prime_role not in x.roles, ch.members))
                if len(members) == 0:
                    return
                else:
                    voice_start = supports_stats.find_one({ "id": f"{member.id}" })["voice_start"]
                    time_voice = int(time.time()) - voice_start
                    supports_stats.update_one({ "id": f"{member.id}" }, { "$inc": { "voice": time_voice, "7d.voice": time_voice, "30d.voice": time_voice } })
            else:
                members = ch.members
                if len(members) == 0:
                    return
                else:
                    for member in members:
                        voice_start = supports_stats.find_one({ "id": f"{member.id}" })["voice_start"]
                        time_voice = int(time.time()) - voice_start
                        supports_stats.update_one({ "id": f"{member.id}" }, { "$inc": { "voice": time_voice, "7d.voice": time_voice, "30d.voice": time_voice } })
        


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        if message.channel.category.id != 823234023593213952:
            return
        if message.channel.id in [861256759796695050, 826855318260678656, 787038639979757618, 823253737153363979]:
            return
        support_role = message.guild.get_role(823234604550062102)
        prime_role = message.guild.get_role(827278746205683802)
        if support_role in message.author.roles or prime_role in message.author.roles:
            supports_stats.update_one({ "id": f"{message.author.id}" }, { "$inc": { "chat": 1, "7d.chat": 1, "30d.chat": 1 } })

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        if not inter.component.id.startswith("support"):
            return
        
        support_role = inter.guild.get_role(823234604550062102)
        prime_role = inter.guild.get_role(827278746205683802)
        member = inter.guild.get_member(int(inter.user.id))

        if inter.component.id == "support_voice-ticket":
            if support_role not in member.roles and prime_role not in member.roles:
                return
            sup = None
            for key in inter.channel.overwrites.copy():
                if inter.channel.overwrites[key].send_messages is True and type(key) == discord.Member:
                    if support_role in key.roles or prime_role in key.roles: 
                        sup = key
                        break
            if sup is None:
                return
            elif sup is not None and member.id != sup.id:
                return 
            vc_created = list(filter(lambda x: x.name == inter.channel.name and type(x) == discord.VoiceChannel, inter.channel.category.channels))
            if len(vc_created) == 0:
                vc = await inter.guild.create_voice_channel(name=inter.channel.name, category=inter.channel.category, overwrites=inter.channel.overwrites)
                user = None
                for key in inter.channel.overwrites.copy():
                    if inter.channel.overwrites[key].view_channel is True and type(key) == discord.Member:
                        if support_role not in key.roles and prime_role not in key.roles: 
                            user = key
                            break
                await vc.set_permissions(user, view_channel=True, connect=True)
                url = await vc.create_invite(unique=True)
                e = discord.Embed(color=0x2f3136)
                e.title = "Помощь игрокам"
                e.description = f"Войс был создан."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                await inter.respond(embed=e)
                e.description = f"Войс был создан помощником.\nURL: {url}"
                await inter.channel.send(embed=e)
            else:
                e = discord.Embed(color=0x2f3136)
                e.title = "Помощь игрокам"
                e.description = f"Войс уже создан."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                await inter.respond(embed=e)


        elif inter.component.id == "support_close-ticket":
            user = None
            for key in inter.channel.overwrites.copy():
                if inter.channel.overwrites[key].view_channel is True and type(key) == discord.Member:
                    if support_role not in key.roles and prime_role not in key.roles: 
                        user = key
                        break
            sup = None
            for key in inter.channel.overwrites.copy():
                if inter.channel.overwrites[key].send_messages is True and type(key) == discord.Member:
                    if support_role in key.roles or prime_role in key.roles: 
                        sup = key
                        break
            #print(user)
            #print(sup)
            if member != sup and member != user:
                return

            e = discord.Embed(color=0x2f3136)
            e.title = "Помощь игрокам"
            e.description = "Вы точно хотите закрыть тикет?"
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=member.name, icon_url=member.avatar_url)
            await inter.respond(embed=e, components=[
                [
                    Button(label="Да", style=ButtonStyle.green, id="support_close-ticket|yes"),
                    Button(label="Нет", style=ButtonStyle.red, id="support_close-ticket|no")
                ]
            ])

            i = await self.bot.wait_for("button_click", check=lambda i: i.user.id == member.id and i.component.id.startswith("support_close-ticket|"))

            choose = i.component.id.split("|")[1]

            if choose == "yes":
                e = discord.Embed(color=0x2f3136)
                e.title = "Помощь игрокам"
                e.description = "Тикет был закрыт."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                await i.respond(type=7, embed=e, components=[])
                e.description = "Оцените качество ответа помощника от `1` до `5`."
                
                await inter.channel.send(embed=e, components=[
                    [
                        Button(label='1', style=ButtonStyle.red, id="support_ticket-rate|1"),
                        Button(label='2', style=ButtonStyle.red, id="support_ticket-rate|2"),
                        Button(label='3', style=ButtonStyle.blue, id="support_ticket-rate|3"),
                        Button(label='4', style=ButtonStyle.green, id="support_ticket-rate|4"),
                        Button(label='5', style=ButtonStyle.green, id="support_ticket-rate|5")
                    ]
                ])
                if user:
                    await inter.channel.send(user.mention, delete_after=5.0)
                try:
                    i = await self.bot.wait_for('button_click', check=lambda i: "ticket-rate" in i.component.id and i.user.id == user.id, timeout=20.0)
                except asyncio.TimeoutError:
                    sup = None
                    for key in inter.channel.overwrites.copy():
                        if inter.channel.overwrites[key].send_messages is True and type(key) == discord.Member:
                            if support_role in key.roles or prime_role in key.roles: 
                                sup = key
                                break
                    if sup is not None:
                        supports_stats.update_one({ "id": f"{sup.id}" }, { 
                            "$inc": {
                                "tickets": 1,
                                "7d.tickets": 1,
                                "30d.tickets": 1
                            } 
                        })
                    uid = inter.channel.name.split('-')[1]
                    for channel in inter.channel.category.channels:
                        if uid in channel.name:
                            await channel.delete()
                else:
                    rate = int(i.component.id.split('|')[1])
                    sup = None
                    for key in i.channel.overwrites.copy():
                        if i.channel.overwrites[key].send_messages is True and type(key) == discord.Member:
                            if support_role in key.roles or prime_role in key.roles: 
                                sup = key
                                break
                    if sup is not None:
                        supports_stats.update_one({ "id": f"{sup.id}" }, { "$push": { 
                            "rating": rate, 
                            "7d.rating": rate, 
                            "30d.rating": rate,
                        },
                        "$inc": {
                            "tickets": 1,
                            "7d.tickets": 1,
                            "30d.tickets": 1
                        } })
                    uid = inter.channel.name.split('-')[1]
                    for channel in inter.channel.category.channels:
                        if uid in channel.name:
                            await channel.delete()
            else:
                e = discord.Embed(color=0x2f3136)
                e.title = "Помощь игрокам"
                e.description = "Закрытие тикета отменено."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                await i.respond(type=7, embed=e, components=[])

        elif inter.component.id == "support_accept-ticket":
            if support_role not in member.roles and prime_role not in member.roles:
                return
            
            embed = inter.message.embeds[0]
            member_ticket = inter.guild.get_member_named(embed.footer.text) 
            if member_ticket is not None:
                if support_role in member_ticket.roles or prime_role in member_ticket.roles:
                    if member_ticket.id == inter.user.id:
                        return
            embed.description = f"Помощник найден: {inter.user.mention}"
            await inter.respond(type=7, embed=embed, components=[
                Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket'),
                Button(label="Создать войс", style=ButtonStyle.blue, id='support_voice-ticket')
            ])
            await inter.channel.set_permissions(inter.user, send_messages=True)

        elif inter.component.id == "support_init-ticket":
            if support_role not in member.roles and prime_role not in member.roles:
                return

            e = discord.Embed(color=0x2f3136)
            e.title = "Помощь игрокам"
            e.description = f"""Вопрос был обработан вручную, ожидайте помощника."""
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=member.name, icon_url=member.avatar_url)
            await inter.respond(type=7, embed=e, components=[
                Button(label="Принять тикет", style=ButtonStyle.green, id='support_accept-ticket'),
                Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket-notinit')
            ])

        elif inter.component.id == "support_close-ticket-notinit":
            e = discord.Embed(color=0x2f3136)
            e.title = "Помощь игрокам"
            e.description = "Вы точно хотите закрыть тикет?"
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=member.name, icon_url=member.avatar_url)
            await inter.respond(embed=e, components=[
                [
                    Button(label="Да", style=ButtonStyle.green, id="support_close-ticket-notinit|yes"),
                    Button(label="Нет", style=ButtonStyle.red, id="support_close-ticket-notinit|no")
                ]
            ])

            i = await self.bot.wait_for("button_click", check=lambda i: i.user.id == member.id and i.component.id.startswith("support_close-ticket-notinit|"))

            choose = i.component.id.split("|")[1]

            if choose == "yes":
                uid = inter.channel.name.split('-')[1]
                for channel in inter.channel.category.channels:
                    if uid in channel.name:
                        await channel.delete()
            else:
                e = discord.Embed(color=0x2f3136)
                e.title = "Помощь игрокам"
                e.description = "Закрытие тикета отменено."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                await i.respond(type=7, embed=e, components=[])

        elif inter.component.id == "support_create":
            if support_role in member.roles or prime_role in member.roles:
                e = discord.Embed(color=0x2f3136)
                e.title = "Помощь игрокам"
                e.description = "Тикеты недоступны помощникам."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
            bans = support_settings.find_one({ "id": "604083589570625555" })["tickets_bans"]
            if member.id in bans:
                e = discord.Embed(color=0x2f3136)
                e.title = "Помощь игрокам"
                e.description = "Вы находитесь в чёрном списке тикетов."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
            ch = None
            for channel in inter.channel.category.channels:
                o = channel.overwrites_for(inter.user)
                if o.view_channel is True:
                    ch = channel
                    break
            if ch is not None:
                return
            uid = create_uid()
            overwrites = {
                member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True, read_message_history=True),
                support_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, attach_files=True, embed_links=True, read_message_history=True),
                prime_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, attach_files=True, embed_links=True, read_message_history=True),
                inter.guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }
            chan = await inter.guild.create_text_channel(name=f"ticket-{uid}", category=inter.channel.category, overwrites=overwrites)
            e = discord.Embed(color=0x2f3136)
            e.title = "Помощь игрокам"
            e.description = f"""Приветствую в вашем тикете!

У вас есть 15 минут на написание вопроса, бот обработает тикет после первого вашего сообщения и позовёт помощников."""
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=member.name, icon_url=member.avatar_url)
            msg_q = await chan.send(embed=e, components=[
                Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket-notinit'),
                Button(label="Обработка (в случае не сработавшей автоматической)", style=ButtonStyle.red, id='support_init-ticket')
            ])
            await chan.send(member.mention, delete_after=2.0)
            e2 = discord.Embed(color=0x2f3136)
            e2.title = "Помощь игрокам"
            e2.description = "Тикет создан."
            e2.timestamp = datetime.datetime.utcnow()
            e2.set_footer(text=member.name, icon_url=member.avatar_url)
            await inter.respond(embed=e2)
            try:
                m = await self.bot.wait_for('message', check=lambda m: m.author.id == member.id and m.channel.id == chan.id, timeout=900.0)
            except asyncio.TimeoutError:
                await chan.delete()
            else:
                e = discord.Embed(color=0x2f3136)
                e.title = "Помощь игрокам"
                e.description = f"""Вопрос был обработан, ожидайте помощника."""
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                await msg_q.edit(embed=e, components=[
                    Button(label="Принять тикет", style=ButtonStyle.green, id='support_accept-ticket'),
                    Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket-notinit')
                ])
                await chan.send(f"{support_role.mention} {prime_role.mention}", delete_after=3.0)
                #i = await self.bot.wait_for('button_click', check=lambda i: i.component.id == "support_accept-ticket" and (support_role in i.guild.get_member(i.user.id).roles or prime_role in i.guild.get_member(i.user.id).roles))
                #e.description = f"Помощник найден: {i.user.mention}"
                #await i.respond(type=7, embed=e, components=[
                #    Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket'),
                #    Button(label="Создать войс", style=ButtonStyle.blue, id='support_voice-ticket')
                #])
                #await i.channel.set_permissions(i.user, send_messages=True)
            #support.insert_one()

    @commands.has_any_role(827278746205683802, 823234604550062102)
    @commands.command(name='suppanel', aliases=['supp'])
    async def suppanel(self, ctx):
        if ctx.channel.category.id != 823234023593213952:
            return
        if ctx.channel.id == 823253737153363979 or ctx.channel.id == 861256759796695050 or ctx.channel.id == 787038639979757618 or ctx.channel.id == 826855318260678656:
            return
        sup = None
        role1 = ctx.guild.get_role(827278746205683802)
        role2 = ctx.guild.get_role(823234604550062102)
        for key in ctx.channel.overwrites.copy():
            if ctx.channel.overwrites[key].send_messages is True and type(key) == discord.Member:
                if role1 in key.roles or role2 in key.roles: 
                    sup = key
                    break
        e = discord.Embed(color=0x2f3136)
        e.title = "Панель саппорта"
        e.description = "Выберите действие"
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        if sup is None:
            await ctx.send(embed=e, components=[
                Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket')
                #Button(label="Создать войс", style=ButtonStyle.blue, id='support_voice-ticket'),
                #Button(label="Передать тикет", style=ButtonStyle.blue, id='support_redirect-ticket')
            ])
        elif sup is not None and sup != ctx.author:
            await ctx.send(embed=e, components=[
                Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket')
                #Button(label="Создать войс", style=ButtonStyle.blue, id='support_voice-ticket'),
                #Button(label="Передать тикет", style=ButtonStyle.blue, id='support_redirect-ticket')
            ])
        else:
            await ctx.send(embed=e, components=[
                Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket'),
                Button(label="Создать войс", style=ButtonStyle.blue, id='support_voice-ticket'),
                Button(label="Передать тикет", style=ButtonStyle.blue, id='support_redirect-ticket')
            ])
        support_role = ctx.guild.get_role(823234604550062102)
        prime_role = ctx.guild.get_role(827278746205683802)
        i = await self.bot.wait_for('button_click', check=lambda i: i.component.id == "support_redirect-ticket" and i.user.id == ctx.author.id)
        if sup is not None and sup != ctx.author:
            e.description = "На данный тикет уже отвечает другой помощник."
            await i.respond(type=7, embed=e)
        elif sup is None:
            e.description = "Данный тикет никем не принят."
            await i.respond(type=7, embed=e, components=[
                Button(label="Принять тикет", style=ButtonStyle.green, id='support_accept-redirect-ticket'),
                Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket'),
                
            ])
        else:
            e.description = "Выполнена передача тикета. Ожидайте подтверждения другим помощником."
            await i.respond(type=7, embed=e, components=[
                Button(label="Принять тикет", style=ButtonStyle.green, id='support_accept-ticket'),
                Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket'),
                
            ])
            await i.channel.send(f"{support_role.mention} {prime_role.mention}", delete_after=3.0)
            #i = await self.bot.wait_for('button_click', check=lambda i: i.component.id == "support_accept-redirect-ticket" and i.user.id != ctx.author.id and (prime_role in i.guild.get_member(i.user.id).roles or support_role in i.guild.get_member(i.user.id).roles))
            #e.description = f"Помощник найден: {i.user.mention}"
            #await i.respond(type=7, embed=e, components=[
            #    Button(label="Закрыть тикет", style=ButtonStyle.red, id='support_close-ticket'),
            #    Button(label="Создать войс", style=ButtonStyle.blue, id='support_voice-ticket')
            #])
            await i.channel.set_permissions(ctx.author, send_messages=None)
            #await i.channel.set_permissions(i.user, send_messages=True)

    @commands.is_owner()
    @commands.command(name="supsetup", aliases=['sups'])
    async def supsetup(self, ctx):
        e = discord.Embed(color=0x2f3136)
        e.title = "Помощь игрокам"
        e.description = "Нажмите на кнопку \"Задать вопрос\" ниже, если вам нужно задать вопрос по игре."
        e.set_image(url="https://media.discordapp.net/attachments/795008644550623242/826952111417196564/a0ff518930cbe367.gif")
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e, components=[
            Button(label="Задать вопрос", style=ButtonStyle.green, id='support_create')
        ])

    @commands.check_any(commands.has_any_role(827278746205683802, 823234604550062102), commands.has_guild_permissions(administrator=True))
    @commands.command(name="sstats", aliases=['ss'])
    async def sstats(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        role1 = ctx.guild.get_role(827278746205683802)
        role2 = ctx.guild.get_role(823234604550062102)
        if role1 not in member.roles and role2 not in member.roles:
            return
        info = supports_stats.find_one({ "id": f"{member.id}" })
        e = discord.Embed(color=0x2f3136)
        e.title = f"Статистика помощника {member}"
        rating_all = info["rating"]
        rating_7d = info["7d"]["rating"]
        rating_30d = info["30d"]["rating"]
        mid_rating_all = sum(rating_all) / len(rating_all) if len(rating_all) != 0 else 0
        mid_rating_7dl = sum(rating_7d) / len(rating_7d) if len(rating_7d) != 0 else 0
        mid_rating_30d = sum(rating_30d) / len(rating_30d) if len(rating_30d) != 0 else 0
        voice_all = info["voice"]
        voice_7d = info["7d"]["voice"]
        voice_30d = info["30d"]["voice"]
        chat_all = info["chat"]
        chat_7d = info["7d"]["chat"]
        chat_30d = info["30d"]["chat"]
        tickets_all = info["tickets"]
        tickets_7d = info["7d"]["tickets"]
        tickets_30d = info["30d"]["tickets"]
        e.add_field(name="`Общая статистика`", value=f"```Средняя оценка: {round(mid_rating_all, 1)}\nВремя войсов: {seconds_to_hh_mm_ss(voice_all)}\nКоличество сообщений: {chat_all}\nКоличество тикетов: {tickets_all}```", inline=False)
        e.add_field(name="`Статистика за 7 дней`", value=f"```Средняя оценка: {round(mid_rating_7dl, 1)}\nВремя войсов: {seconds_to_hh_mm_ss(voice_7d)}\nКоличество сообщений: {chat_7d}\nКоличество тикетов: {tickets_7d}```", inline=False)
        e.add_field(name="`Статистика за 30 дней`", value=f"```Средняя оценка: {round(mid_rating_30d, 1)}\nВремя войсов: {seconds_to_hh_mm_ss(voice_30d)}\nКоличество сообщений: {chat_30d}\nКоличество тикетов: {tickets_30d}```", inline=False)
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @commands.has_any_role(827278746205683802)
    @commands.command(name="tkban", aliases=['tkb'])
    async def tkban(self, ctx, member: discord.Member=None):
        if member is None:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите пользователя"
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        bans = support_settings.find_one({ "id": "604083589570625555" })["tickets_bans"]
        if member.id in bans:
            e = discord.Embed(color=0x2f3136)
            e.description = "Данный пользователь уже находиться в чёрном списке тикетов."
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        support_settings.update_one({ "id": "604083589570625555" }, { "$push": { "tickets_bans": member.id } })
        e = discord.Embed(color=0x2f3136)
        e.description = f"Пользователь {member.mention} был добавлен в чёрный список тикетов."
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @commands.has_any_role(827278746205683802)
    @commands.command(name="tkunban", aliases=['tkunb'])
    async def tkunban(self, ctx, member: discord.Member=None):
        if member is None:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите пользователя"
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        bans = support_settings.find_one({ "id": "604083589570625555" })["tickets_bans"]
        if member.id not in bans:
            e = discord.Embed(color=0x2f3136)
            e.description = "Данный пользователь не найден в чёрном списке тикетов."
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        support_settings.update_one({ "id": "604083589570625555" }, { "$pull": { "tickets_bans": member.id } })
        e = discord.Embed(color=0x2f3136)
        e.description = f"Пользователь {member.mention} был удалён из чёрного списка тикетов."
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(SupportCog(bot)) 
    bot.loop.create_task(supports_check(bot))
    bot.loop.create_task(supports_delete_stats(bot))