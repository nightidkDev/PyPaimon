import discord
from discord import permissions
from discord.ext import commands
import pymongo
import time
import os
import sys
import datetime
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
voice_wishes = db2.voices_wishes
chat_wishes = db2.chats_wishes
users = db.prof_ec_users
sdb = db.u_settings

def zero_adds(value, length):
    """ Adds zeros """
    return f'{"0" * (length - len(value))}{value}' if len(value) < length else value 

class ServerWishesControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="wishchat", invoke_without_command=True, aliases=["wchat", "wc"])
    async def wish_chat(self, ctx):
        chat_info = chat_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not chat_info:
            chat_info_text = "Информация не найдена."
        else:
            if chat_info["chatID"] == "": 
                chat_info_text = f"""Чат: не создан.
Дата окончания: {datetime.datetime.utcfromtimestamp(chat_info['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}
"""
            else:
                channelw = self.bot.get_channel(int(chat_info['chatID']))
                if channelw:
                    chat_info_text = f"""Чат: <#{chat_info['chatID']}>
Дата окончания: {datetime.datetime.utcfromtimestamp(chat_info['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}
"""
                else:
                    chat_info_text = f"""Чат: не создан.
Дата окончания: {datetime.datetime.utcfromtimestamp(chat_info['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}
"""
        e = discord.Embed(color=0x2f3136)
        e.description = f"""
`.wc name [name]` - изменение названия чата на `[name]`.
`.wc add [member]` - добавить права просмотра для пользователя в чат.
`.wc remove [member]` - удалить права просмотра для пользователя в чат.
`.wc radd [roleID]` - добавить права просмотра для роли в чат.
`.wc rremove [roleID]` - удалить права просмотра для роли в чат.
`.wc create` - создать личный чат.

**Информация:**
{chat_info_text}
"""
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @wish_chat.command(name="add")
    async def wish_chat_add(self, ctx, member:discord.User=None):
        chat_info = chat_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not chat_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете чатом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if chat_info['chatID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(chat_info['chatID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not member:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите пользователя."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if member == ctx.author:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не можете добавить себя."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        user_add = sdb.find_one({ 'id': f"{member.id}", 'guild': f"{ctx.guild.id}" })

        if user_add['selfrooms_inter'] == 1:
            e = discord.Embed(color=0x2f3136)
            e.description = "Этот пользователь запретил добавлять его в личные комнаты."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if channel.overwrites_for(member).view_channel is True:
            e = discord.Embed(color=0x2f3136)
            e.description = "Этот пользователь уже добавлен в права чата."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        

        await channel.set_permissions(member, view_channel=True,
                                            read_messages=True,
                                            send_messages=True,
                                            read_message_history=True)

        chat_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$push": { "permissions": { "type": "member", "id": f"{member.id}" } } })

        e = discord.Embed(color=0x2f3136)
        e.description = f"В права чата был добавлен пользователь {member.mention}"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @wish_chat.command(name="radd")
    async def wish_chat_radd(self, ctx, role:discord.Role=None):
        chat_info = chat_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not chat_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете чатом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if chat_info['chatID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(chat_info['chatID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not role:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите роль."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if role.id == 767626360965038080 or role.id == 604083589570625555 or role.id == 767012156557623356:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эту роль нельзя добавить в права чата."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if role.position < 125:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эту роль нельзя добавить в права чата."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        role_min_admin = ctx.guild.get_role(885610515743772752)
        if role.position > role_min_admin.position:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эту роль нельзя добавить в права чата."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if channel.overwrites_for(role).view_channel is True:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эта роль уже добавлена в права чата."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        

        await channel.set_permissions(role, view_channel=True,
                                            read_messages=True,
                                            send_messages=True,
                                            read_message_history=True)

        chat_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$push": { "permissions": { "type": "role", "id": f"{role.id}" } } })

        e = discord.Embed(color=0x2f3136)
        e.description = f"В права чата был добавлена роль {role.mention}"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @wish_chat.command(name="remove")
    async def wish_chat_remove(self, ctx, member:discord.User=None):
        chat_info = chat_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not chat_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете чатом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if chat_info['chatID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(chat_info['chatID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not member:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите пользователя."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if member == ctx.author:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не можете удалить себя."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if channel.overwrites_for(member).view_channel is False or channel.overwrites_for(member).view_channel is None:
            e = discord.Embed(color=0x2f3136)
            e.description = "Этот пользователь и так не имеет прав в чате."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        await channel.set_permissions(member, overwrite=None)

        chat_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$pull": { "permissions": { "type": "member", "id": f"{member.id}" } } })

        e = discord.Embed(color=0x2f3136)
        e.description = f"В права чата был удален пользователь {member.mention}"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @wish_chat.command(name="rremove")
    async def wish_chat_rremove(self, ctx, role:discord.Role=None):
        chat_info = chat_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not chat_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете чатом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if chat_info['chatID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(chat_info['chatID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not role:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите роль."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if channel.overwrites_for(role).view_channel is False or channel.overwrites_for(role).view_channel is None:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эта роль и так не имеет прав в чате."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        await channel.set_permissions(role, overwrite=None)

        chat_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$pull": { "permissions": { "type": "role", "id": f"{role.id}" } } })

        e = discord.Embed(color=0x2f3136)
        e.description = f"В права чата был удалена роль {role.mention}"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @wish_chat.command(name="name")
    async def wish_chat_name(self, ctx, *, name=None):
        chat_info = chat_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not chat_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете чатом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if chat_info['chatID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(chat_info['chatID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Чат ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not name:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите название чата."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        name = name.replace("\n", "")

        if len(name) <= 0 or len(name) > 100:
            e = discord.Embed(color=0x2f3136)
            e.description = "Название чата не может привышать 100 символов."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        try:
            await channel.edit(name=name)
        except BaseException as e:
            print(e)
        chat_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$set": { "name": f"{name}" } })
        e = discord.Embed(color=0x2f3136)
        e.description = f"Название чата было изменено на: **{name}**"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)
        
    @wish_chat.command(name="create")
    async def wish_chat_create(self, ctx):
        chat_info = chat_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not chat_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете чатом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if chat_info['chatID'] != "":
            channel = self.bot.get_channel(int(chat_info['chatID']))

            if channel:
                e = discord.Embed(color=0x2f3136)
                e.description = "Чат уже создан."
                e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                return await ctx.send(embed=e)

        category = ctx.guild.get_channel(886918268521164860)

        overwrites = {
            ctx.author: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True, read_message_history=True),
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }

        if chat_info["name"] != "":
            namec = chat_info["name"]
        else:
            namec = ctx.author.name

        channelw = await ctx.guild.create_text_channel(name=namec, overwrites=overwrites, category=category)
        for i in range(len(chat_info['permissions'])):
            a = chat_info['permissions'][i]["type"]
            b = chat_info['permissions'][i]["id"]
            try:
                if a == "member":
                    perm = ctx.guild.get_member(int(b))
                else:
                    perm = ctx.guild.get_role(int(b))
                await channelw.set_permissions(perm, view_channel=True,
                                                    read_messages=True,
                                                    send_messages=True,
                                                    read_message_history=True)
            except:
                pass
        chat_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$set": { "chatID": f"{channelw.id}" } })
        e = discord.Embed(color=0x2f3136)
        e.description = "Чат был создан."
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @commands.group(name="wishvoice", invoke_without_command=True, aliases=["wvoice", "wv"])
    async def wish_voice(self, ctx):
        voice_info = voice_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not voice_info:
            voice_info_text = "Информация не найдена."
        else:
            if voice_info["voiceID"] == "": 
                voice_info_text = f"""Войс: не создан.
Дата окончания: {datetime.datetime.utcfromtimestamp(voice_info['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}
"""
            else:
                channel = self.bot.get_channel(int(voice_info['voiceID']))
                if channel is None:
                    voice_info_text = f"""Войс: не создан.
Дата окончания: {datetime.datetime.utcfromtimestamp(voice_info['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}
"""
                else:
                    voice_info_text = f"""Войс: <#{voice_info['voiceID']}>
Дата окончания: {datetime.datetime.utcfromtimestamp(voice_info['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}
"""
        e = discord.Embed(color=0x2f3136)
        e.description = f"""
`.wv name [name]` - изменение названия войс на `[name]`.
`.wv add [member]` - добавить права для пользователя в войсе.
`.wv radd [roleID]` - добавить права для роли в войсе.
`.wv remove [member]` - удалить права для пользователя в войсе.
`.wv rremove [roleID]` - удалить права для роли в войсе.
`.wv limit [0-99]` - установить максимальное количество пользователей в войсе.
`.wv create` - создать личный войс.

**Внимание**
При команде `.wv create` войс создаётся на час.
Если через час не будет никого в канале - войс удалится, но его можно будет повторно создать (создание идёт со всеми настройками, что были прописаны до удаления).
Но если же в канале через час кто-то будет - войс продлиться ещё на час.

**Информация:**
{voice_info_text}
"""
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @wish_voice.command(name="limit")
    async def wish_voice_limit(self, ctx, limit_count=None):
        voice_info = voice_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not voice_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете войсом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if voice_info['voiceID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(voice_info['voiceID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not limit_count:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите лимит от 0 до 99."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        try:
            limit_count = int(limit_count)
        except:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите лимит от 0 до 99."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if limit_count < 0 or limit_count > 99:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите лимит от 0 до 99."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        voice_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$set": { "limit": limit_count } })

        await channel.edit(user_limit=limit_count)

        e = discord.Embed(color=0x2f3136)
        e.description = f"Войс лимит установлен на: **{'неограниченное' if limit_count == 0 else f'{limit_count}'}**"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @wish_voice.command(name="add")
    async def wish_voice_add(self, ctx, member:discord.User=None):
        voice_info = voice_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not voice_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете войсом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if voice_info['voiceID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(voice_info['voiceID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not member:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите пользователя."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        user_add = sdb.find_one({ 'id': f"{member.id}", 'guild': f"{ctx.guild.id}" })

        if user_add['selfrooms_inter'] == 1:
            e = discord.Embed(color=0x2f3136)
            e.description = "Этот пользователь запретил добавлять его в личные комнаты."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if channel.overwrites_for(member).connect is True:
            e = discord.Embed(color=0x2f3136)
            e.description = "Этот пользователь уже добавлен в права войса."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        

        await channel.set_permissions(member, view_channel=True,
                                            connect=True,
                                            speak=True,
                                            stream=True,
                                            use_voice_activation=True)

        voice_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$push": { "permissions": { "type": "member", "id": f"{member.id}" } } })

        e = discord.Embed(color=0x2f3136)
        e.description = f"В права войса был добавлен пользователь {member.mention}"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @wish_voice.command(name="radd")
    async def wish_voice_radd(self, ctx, role:discord.Role=None):
        print(role)
        voice_info = voice_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not voice_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете войсом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if voice_info['voiceID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(voice_info['voiceID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not role:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите роль."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if role.id == 767626360965038080 or role.id == 604083589570625555:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эту роль нельзя добавить в права войса."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if role.position < 125:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эту роль нельзя добавить в права чата."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        role_min_admin = ctx.guild.get_role(885610515743772752)
        if role.position > role_min_admin.position:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эту роль нельзя добавить в права чата."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if channel.overwrites_for(role).connect is True:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эта роль уже добавлена в права войса."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        await channel.set_permissions(role, view_channel=True,
                                            connect=True,
                                            speak=True,
                                            stream=True,
                                            use_voice_activation=True)

        voice_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$push": { "permissions": { "type": "role", "id": f"{role.id}" } } })

        e = discord.Embed(color=0x2f3136)
        e.description = f"В права войса был добавлена роль {role.mention}"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @wish_voice.command(name="remove")
    async def wish_voice_remove(self, ctx, member:discord.User=None):
        voice_info = voice_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not voice_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете войсом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if voice_info['voiceID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(voice_info['voiceID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not member:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите пользователя."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if channel.overwrites_for(member).connect is False or channel.overwrites_for(member).connect is None:
            e = discord.Embed(color=0x2f3136)
            e.description = "Этот пользователь и так не имеет прав в войсе."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        await channel.set_permissions(member, overwrite=None)

        voice_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$pull": { "permissions": { "type": "member", "id": f"{member.id}" } } })

        e = discord.Embed(color=0x2f3136)
        e.description = f"В права войса был удален пользователь {member.mention}"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @wish_voice.command(name="rremove")
    async def wish_voice_rremove(self, ctx, role:discord.Role=None):
        voice_info = voice_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not voice_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете войсом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if voice_info['voiceID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(voice_info['voiceID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not role:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите роль."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if channel.overwrites_for(role).connect is False or channel.overwrites_for(role).connect is None:
            e = discord.Embed(color=0x2f3136)
            e.description = "Эта роль и так не имеет прав в войсе."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        await channel.set_permissions(role, overwrite=None)

        voice_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$pull": { "permissions": { "type": "role", "id": f"{role.id}" } } })

        e = discord.Embed(color=0x2f3136)
        e.description = f"В права войса был удалена роль {role.mention}"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @wish_voice.command(name="name")
    async def wish_voice_name(self, ctx, *, name=None):
        voice_info = voice_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not voice_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете войсом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if voice_info['voiceID'] == "":
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        channel = self.bot.get_channel(int(voice_info['voiceID']))

        if not channel:
            e = discord.Embed(color=0x2f3136)
            e.description = "Войс ещё не создан."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not name:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите название войса."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        name = name.replace("\n", "")

        if len(name) <= 0 or len(name) > 100:
            e = discord.Embed(color=0x2f3136)
            e.description = "Название войса не может привышать 100 символов."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        try:
            await channel.edit(name=name)
        except BaseException as e:
            print(e)
        voice_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$set": { "name": f"{name}" } })
        e = discord.Embed(color=0x2f3136)
        e.description = f"Название войса было изменено на: **{name}**"
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)
        
    @wish_voice.command(name="create")
    async def wish_voice_create(self, ctx):
        voice_info = voice_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not voice_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете войсом."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if voice_info['voiceID'] != "":
            channel = self.bot.get_channel(int(voice_info['voiceID']))

            if channel:
                e = discord.Embed(color=0x2f3136)
                e.description = "Войс уже создан."
                e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                return await ctx.send(embed=e)

        category = ctx.guild.get_channel(886917957865865266)

        overwrites = {
            ctx.author: discord.PermissionOverwrite(view_channel=True,
                                                    connect=True,
                                                    speak=True,
                                                    stream=True,
                                                    use_voice_activation=True),
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False)
        }

        if voice_info["name"] != "":
            namec = voice_info["name"]
        else:
            namec = ctx.author.name

        channelw = await ctx.guild.create_voice_channel(name=namec, overwrites=overwrites, category=category, user_limit=voice_info['limit'])
        for i in range(len(voice_info['permissions'])):
            a = voice_info['permissions'][i]["type"]
            b = voice_info['permissions'][i]["id"]
            try:
                if a == "member":
                    perm = ctx.guild.get_member(int(b))
                else:
                    perm = ctx.guild.get_role(int(b))
                await channelw.set_permissions(perm, view_channel=True,
                                                    connect=True,
                                                    speak=True,
                                                    stream=True,
                                                    use_voice_activation=True)
            except:
                pass
        voice_wishes.update_one({ "owner": f"{ctx.author.id}" }, { "$set": { "voiceID": f"{channelw.id}", "timeoutHour": int(time.time() + 3600) } })
        e = discord.Embed(color=0x2f3136)
        e.description = "Войс был создан."
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=e)

    @commands.group(name="wishrole", invoke_without_command=True, aliases=['wrole', 'wr'])
    async def wish_role(self, ctx):
        role_info = roles_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not role_info:
            role_info_text = "Информация не найдена."
        else:
            role_info_text = f"""Роль: <@&{role_info['roleID']}>
Дата окончания: {datetime.datetime.utcfromtimestamp(role_info['timeout'] + 10800).strftime('%d.%m.%Y %H:%M')}
"""
        e = discord.Embed(color=0x2f3136)
        e.description = f"""
`.wr color #RRGGBB` - смена цвета роли.
`.wr center` - центрирование роли.
`.wr name [name]` - изменение названия роли на `[name]`.
`.wr equip` - надеть личную роль.
`.wr unequip` - снять личную роль.

**Информация:**
{role_info_text}
"""
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @wish_role.command(name="color")
    async def wish_role_color(self, ctx, color=None):
        role_info = roles_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not role_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете ролью."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if not color:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите цвет в формате `#8aff8a` или `8aff8a`."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        try:
            colorsharp = color.replace('#', '')
            colorsixteen = int(colorsharp, 16)
        except:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите цвет в формате `#8aff8a` или `8aff8a`."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        rolew = ctx.guild.get_role(int(role_info['roleID']))
        await rolew.edit(color=colorsixteen)
        e = discord.Embed(color=0x2f3136)
        colorhex = f'{zero_adds(str(hex(colorsixteen)).replace("0x", ""), 6)}'
        e.description = f"""
Успешно установлен цвет: `#{colorhex}`
"""
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @wish_role.command(name="center")
    async def wish_role_center(self, ctx):
        role_info = roles_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not role_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете ролью."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        rolew = ctx.guild.get_role(int(role_info['roleID']))

        if len(rolew.name) >= 40:
            e = discord.Embed(color=0x2f3136)
            e.description = "Роль максимального размера."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if "⠀" in rolew.name:
            e = discord.Embed(color=0x2f3136)
            e.description = "Роль уже центрировалась."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        lenspaces = (37 - len(rolew.name)) // 3
        lenspaces2 = (37 - len(rolew.name)) % 3

        namespaces = ""
        aspaces = 0
        for i in range(lenspaces):
            if aspaces == lenspaces2:
                namespaces += "⠀"
            else:
                namespaces += "⠀ "
                aspaces += 1

        await rolew.edit(name=f"{namespaces}{rolew.name}{namespaces}")

        e = discord.Embed(color=0x2f3136)
        e.description = "Центрирование роли завершено."
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @wish_role.command(name="name")
    async def wish_role_name(self, ctx, *, name=None):
        role_info = roles_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not role_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете ролью."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if not name:
            e = discord.Embed(color=0x2f3136)
            e.description = "Укажите название роли."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        rolew = ctx.guild.get_role(int(role_info['roleID']))
        name = name.replace('\n', '')
        await rolew.edit(name=name)
        e = discord.Embed(color=0x2f3136)
        e.description = f"""
Установлено название: `{name}`
"""
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @wish_role.command(name='equip', aliases=['eq'])
    async def wish_role_equip(self, ctx):
        role_info = roles_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not role_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете ролью."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        rolew = ctx.guild.get_role(int(role_info['roleID']))
        if rolew in ctx.author.roles:
            e = discord.Embed(color=0x2f3136)
            e.description = "Роль уже надета."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        await ctx.author.add_roles(rolew)

        e = discord.Embed(color=0x2f3136)
        e.description = "Роль была успешно надета."
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @wish_role.command(name='unequip', aliases=['uneq'])
    async def wish_role_unequip(self, ctx):
        role_info = roles_wishes.find_one({ "owner": f"{ctx.author.id}" })
        if not role_info:
            e = discord.Embed(color=0x2f3136)
            e.description = "Вы не владеете ролью."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        rolew = ctx.guild.get_role(int(role_info['roleID']))
        if rolew not in ctx.author.roles:
            e = discord.Embed(color=0x2f3136)
            e.description = "Роль уже снята."
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        await ctx.author.remove_roles(rolew)

        e = discord.Embed(color=0x2f3136)
        e.description = "Роль была успешно снята."
        e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(ServerWishesControl(bot))