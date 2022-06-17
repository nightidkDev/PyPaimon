import discord
from discord.ext import commands
import datetime
import asyncio
import time
import random
import os
import io
import re
import uuid

# DataBase
import pymongo
login_url = os.getenv('DBURL')
mongoclient = pymongo.MongoClient(login_url)
db = mongoclient.ashuramaru

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        if message.channel.id == 760120971683299388 or message.channel.id == 760120633241370654 or message.channel.id == 767015636354203659 or message.channel.id == 772900978336727050:
            return

        if message.channel.type == discord.ChannelType.private:
            return
          
        log = self.bot.get_channel(760120971683299388)
        if len(message.attachments) == 0:
            e = discord.Embed(title="", description=f"Сообщение было удалено\n**Удаленное сообщение:**\n```{message.content}```", color=0x2f3136)
            e.add_field(name="Автор ", value=message.author.mention)
            e.add_field(name="Канал: ", value=message.channel.mention)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"ID・{message.author.id}")
            await log.send(embed=e)
        else:
            file = message.attachments[0]
            temp_name = str(uuid.uuid4())
            if file.filename[-4:] == ".png" or file.filename[-4:] == ".jpg" or file.filename[-4:] == ".jpeg" or file.filename[-4:] == ".gif":
                namef = f'log_{temp_name}.{file.filename[-3:]}'
                await file.save(fp=namef)
                e = discord.Embed(title="", description=f"Сообщение было удалено\n**Удаленное сообщение:**\n```{message.content}```", color=0x2f3136)
                e.add_field(name="Автор: ", value=message.author.mention)
                e.add_field(name="Канал: ", value=message.channel.mention)
                file = discord.File(namef, filename=namef)
                e.set_image(url=f"attachment://{namef}")
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"ID・{message.author.id}")
                await log.send(file=file, embed=e)
                os.remove(namef)
            else:
                e = discord.Embed(title="", description=f"Сообщение было удалено\n**Удаленное сообщение:**\n```{message.content}```", color=0x2f3136)
                e.add_field(name="Автор ", value=message.author.mention)
                e.add_field(name="Канал: ", value=message.channel.mention)
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"ID・{message.author.id}")
                await log.send(embed=e)
            
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
          
        if before.content == after.content:
            return

        if before.channel.id == 760120971683299388 or before.channel.id == 760120633241370654 or before.channel.id == 767015636354203659 or before.channel.id == 772900978336727050:
            return

        if before.channel.type == discord.ChannelType.private:
            return
          
        log = self.bot.get_channel(760120971683299388)
        e = discord.Embed(title="", description=f"Сообщение было отредактировано\n**Старое сообщение:**\n```\n{before.content}\n```\n**Новое сообщение:**\n```yaml\n{after.content}\n```\n", color=0x2f3136)
        e.add_field(name="Автор: ", value=before.author.mention)
        e.add_field(name="Канал: ", value=before.channel.mention)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"ID・{before.author.id}")
        await log.send(embed=e)
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_b = before.channel
        voice_a = after.channel
        log = self.bot.get_channel(760120633241370654)
  
        if not voice_b and voice_a:
            e = discord.Embed(title='', description=f'Пользователь {member.mention} подключился голосовому каналу {voice_a.mention} - `{voice_a.name}`', color=0x2f3136)
            e.set_author(name=str(member), icon_url=member.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"ID: {member.id}")
            await log.send(embed=e)
            
        elif voice_b and not voice_a:
            e = discord.Embed(title='', description=f'Пользователь {member.mention} покинул голосовой канал {voice_b.mention} - `{voice_b.name}`', color=0x2f3136)
            e.set_author(name=str(member), icon_url=member.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"ID: {member.id}")
            await log.send(embed=e)
            
            
        elif (voice_b and voice_a) and (voice_b != voice_a):
            e = discord.Embed(title='', description=f'Пользователь {member.mention} поменял канал с `{voice_b.name}` -> `{voice_a.name}`', color=0x2f3136)
            e.set_author(name=str(member), icon_url=member.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"ID: {member.id}")
            await log.send(embed=e)

    """     
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log = self.bot.get_channel(865264498813829130)
      
        if before.nick != after.nick:
            e = discord.Embed(title='', description=f'Никнейм пользователя {before.mention} был изменен', color=0x2f3136)
            e.set_author(name=str(before), icon_url=before.avatar_url)
            e.add_field(name="Старый никнейм:", value=before.nick)
            e.add_field(name="Новый никнейм:", value=after.nick)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"ID: {before.id}")
            await log.send(embed=e)
        
        if before.roles != after.roles:
            drole = before.guild.default_role
            after_r = set(after.roles)
            before_r = set(before.roles)
            to_do = ""
            if len(after.roles) > len(before.roles):
                diff = list(after_r-before_r)
                to_do = "add"
            else:
                diff = list(before_r-after_r)
                to_do = "remove"
            if to_do == "add":
                e = discord.Embed(title='', description=f'Роли пользователя {before.mention} были изменены', color=0x2f3136)
                e.set_author(name=str(before), icon_url=before.avatar_url)
                e.add_field(name='Добавлены роли', value=", ".join(x.mention for x in diff))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"ID: {before.id}")
                await log.send(embed=e)
            elif to_do == "remove":
                e = discord.Embed(title='', description=f'Роли пользователя {before.mention} были изменены', color=0x2f3136)
                e.set_author(name=str(before), icon_url=before.avatar_url)
                e.add_field(name='Удалены роли', value=", ".join(x.mention for x in diff))
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"ID: {before.id}")
                await log.send(embed=e)
    """
    """
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        log = self.bot.get_channel(865264498813829130)
        
        if before.avatar != after.avatar:
            e = discord.Embed(title='', description=f'{before.mention} Обновил свой профиль\n\n **Изменения аватара:**\n[До]({before.avatar_url_as(static_format="png")}) => [После]({after.avatar_url_as(static_format="png")})', color=0x2f3136)
            e.set_author(name=str(before), icon_url=after.avatar_url)
            e.set_thumbnail(url=after.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text="ID: before.id")
            await log.send(embed=e)
        if before.name != after.name:
            e = discord.Embed(title='', description=f'{before.mention} Обновил свой профиль\n\n **Изменения никнейма:**\n**[До]**```\n{before.name}\n```\n**[После]**```\n{after.name}\n```', color=0x2f3136)
            e.set_author(name=str(before), icon_url=after.avatar_url)
            e.set_thumbnail(url=after.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text="ID: before.id")
            await log.send(embed=e)
    """
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log = self.bot.get_channel(760120971683299388)
        
        #e = discord.Embed(title='', description=f'Пользователь {member.mention} покинул сервер', color=0x2f3136)
        #e.set_author(name=member, icon_url=member.avatar_url)
        #e.timestamp = datetime.datetime.utcnow()
        #e.set_footer(text="ID: before.id")
        
        try:
            await member.guild.fetch_ban(member)
            return
        except discord.NotFound:
            e = discord.Embed(title='', description=f'Пользователь {member.mention} был забанен', color=0x2f3136)
            e.set_author(name=member, icon_url=member.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text="ID: before.id")
        
          
        
        
        
def setup(bot):
    bot.add_cog(Logs(bot))