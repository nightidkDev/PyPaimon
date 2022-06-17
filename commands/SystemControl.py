import discord
from discord.ext import commands
import datetime
import os
import sys
sys.path.append("../../")
import config
import pymongo
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
love_rooms = db.love_rooms

class CogsControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def brestart(self, ctx):
        if str(ctx.author.id) not in config.ADMINS:
            e=discord.Embed(title="Ошибка", description="Вы не являетесь разработчиком!",color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text = f"{ctx.author.name}", icon_url = ctx.author.avatar_url)
            await ctx.send(embed=e)
        emb = discord.Embed(description="**[Beta]** Paimon.exe перезагружена.", color=0x2f3136)
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=emb)
        os.system("pm2 restart paimon")

    @commands.command(name="love_room_search", aliases=["lrs"])
    @commands.has_permissions(administrator=True)
    async def love_room_search(self, ctx, id=None):
        love_room = love_rooms.find_one({ "id": id })
        channel = ctx.guild.get_channel(int(id))
        member1 = ctx.guild.get_member(int(love_room['owner1']))
        member2 = ctx.guild.get_member(int(love_room['owner2']))
        """
        {
            "id": "",
            "owner1": "",
            "owner2": "",
            "ctime": 0,
            "ptime": 0,
            "notify": "false",
            "payment": "false"
        }
        """

        e = discord.Embed(color=0x2f3136)
        e.description = f"""
ID румы: {love_room['id']}
Рума: {channel.mention}
Владельцы: {member1.mention} ({member1.id}), {member2.mention} ({member2.id})
Дата создания: {datetime.datetime.utcfromtimestamp(love_room['ctime'] + 10800).strftime('%d.%m.%Y %H:%M:%S')}
Дата платежа: {datetime.datetime.utcfromtimestamp(love_room['ptime'] + 10800).strftime('%d.%m.%Y %H:%M:%S')}
Уведомление: {'Да' if love_room['notify'] == 'true' else 'Нет'}
Платёж: {'Да' if love_room['payment'] == 'true' else 'Нет'}
"""
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=e)

    @commands.command()
    async def cls(self, ctx):
        if str(ctx.author.id) not in config.ADMINS:
            e=discord.Embed(title="Ошибка", description="Вы не являетесь разработчиком!", color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text = f"{ctx.author.name}", icon_url = ctx.author.avatar_url)
            await ctx.send(embed=e)
        os.system("cls")
        emb = discord.Embed(description="Console cleaned <:delete:864289636133634058>", color=0x2f3136)
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=emb)
    
    @commands.command()
    async def load(self, ctx, extension):
        if str(ctx.author.id) not in config.ADMINS:
            await ctx.message.delete()
            emb=discord.Embed(description = "Ошибка доступа! Недостаточно прав.", color=0xff0000)
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = emb)
        else:
            try:
                self.bot.load_extension(f'commands.{extension}')
                print("[Cog] "  + f"Загружен модуль - {extension}")
                await ctx.message.delete()
                emb=discord.Embed(description = f"[Cog] Модуль **{extension}** успешно загружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed = emb)
            except:
                emb=discord.Embed(description = f"[Cog] Модуль **{extension}** уже загружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed = emb)

    @commands.command()
    async def unload(self, ctx, extension):
        if str(ctx.author.id) not in config.ADMINS:
            await ctx.message.delete()
            emb=discord.Embed(description = "Ошибка доступа! Недостаточно прав.", color=0xff0000)
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
            await ctx.send(embed= emb)
        else:
            try:
                print("[Cog] " +  f"Выгружен модуль - {extension}")
                self.bot.unload_extension(f'commands.{extension}')
                await ctx.message.delete()
                emb=discord.Embed(description = f"[Cog] Модуль **{extension}** успешно выгружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed= emb)
            except:
                emb=discord.Embed(description = f"[Cog] Модуль **{extension}** уже выгружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed= emb)


    @commands.command()
    async def reload(self, ctx, extension):
        if str(ctx.author.id) not in config.ADMINS:
            await ctx.message.delete()
            emb=discord.Embed(description = "Ошибка доступа! Недостаточно прав.", color=0xff0000)
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
            await ctx.send(embed= emb)
        else:
            try:
                self.bot.reload_extension(f'commands.{extension}')
                print("[Cog] " + f"Перезагружен модуль - {extension}")
                await ctx.message.delete()
                emb=discord.Embed(description = f"[Cog] Модуль **{extension}** успешно перезагружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed= emb)
            except:
                emb=discord.Embed(description = f"[Cog] Модуль **{extension}** не найден.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed= emb)
            
    @commands.command()
    async def lload(self, ctx, extension):
        if str(ctx.author.id) not in config.ADMINS:
            await ctx.message.delete()
            emb=discord.Embed(description = "Ошибка доступа! Недостаточно прав.", color=0xff0000)
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = emb)
        else:
            try:
                self.bot.load_extension(f'listeners.{extension}')
                print("[Listener] "  + f"Загружен модуль - {extension}")
                await ctx.message.delete()
                emb=discord.Embed(description = f"[Listener] Модуль **{extension}** успешно загружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed = emb)
            except:
                emb=discord.Embed(description = f"[Listener] Модуль **{extension}** уже загружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed = emb)

    @commands.command()
    async def lunload(self, ctx, extension):
        if str(ctx.author.id) not in config.ADMINS:
            await ctx.message.delete()
            emb=discord.Embed(description = "Ошибка доступа! Недостаточно прав.", color=0xff0000)
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
            await ctx.send(embed= emb)
        else:
            try:
                print("[Listener] " +  f"Выгружен модуль - {extension}")
                self.bot.unload_extension(f'listeners.{extension}')
                await ctx.message.delete()
                emb=discord.Embed(description = f"[Listener] Модуль **{extension}** успешно выгружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed= emb)
            except:
                emb=discord.Embed(description = f"[Listener] Модуль **{extension}** уже выгружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed= emb)


    @commands.command()
    async def lreload(self, ctx, extension):
        if str(ctx.author.id) not in config.ADMINS:
            await ctx.message.delete()
            emb=discord.Embed(description = "Ошибка доступа! Недостаточно прав.", color=0xff0000)
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
            await ctx.send(embed= emb)
        else:
            try:
                self.bot.reload_extension(f'listeners.{extension}')
                print("[Listener] " + f"Перезагружен модуль - {extension}")
                await ctx.message.delete()
                emb=discord.Embed(description = f"[Listener] Модуль **{extension}** успешно перезагружен.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed= emb)
            except:
                emb=discord.Embed(description = f"[Listener] Модуль **{extension}** не найден.", color=0xab00ff)
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                await ctx.send(embed= emb)
          
          
          
def setup(bot):
    bot.add_cog(CogsControl(bot))