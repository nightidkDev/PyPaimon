import discord
from discord import permissions
from discord.ext import commands
import pymongo
import os
import sys
import datetime
import time
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

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def wish(self, ctx):
        if reactions.count({ "guild_id": f"{ctx.guild.id}", "user_id": f"{ctx.author.id}", "type": "banners" }) > 0:
            e = discord.Embed(title="Магазин Паймон", description="Воспользуйтесь уже открытыми молитвами или дождитесь их окончания.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=e)
        e = discord.Embed(color=0x2f3136)
        IacquaintFate_emoji = self.bot.get_emoji(772748673251016745)
        IntertwinedFate_emoji = self.bot.get_emoji(772748672999620629)
        e.description = f"""
{IacquaintFate_emoji} Молитва «Жажда странствий»
{IntertwinedFate_emoji} (I) Молитва «{config.banner_2_name}» {'- **завершён**' if config.banner_2_closed else ''}
{IntertwinedFate_emoji} (II) Молитва «{config.banner_2_2_name}» {'- **завершён**' if config.banner_2_2_closed else ''}
{IacquaintFate_emoji} Молитва «Благословение сервера» {'- **временно завершён**' if config.banner_3_closed else ''}
"""
        e.set_author(name="Баннеры")
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        
        msg = await ctx.send(embed=e, components=[
            [
                Button(emoji=IacquaintFate_emoji, id="banner_1"),
                Button(label="(I)", emoji=IntertwinedFate_emoji, id="banner_2", disabled=config.banner_2_closed),
                Button(label="(II)", emoji=IntertwinedFate_emoji, id="banner_2_2", disabled=config.banner_2_2_closed),
                Button(emoji=IacquaintFate_emoji, id="banner_3", disabled=config.banner_3_closed)
            ]
        ])
        reactions.insert_one({ "type": "banners", "user_id": f"{ctx.author.id}", "guild_id": f"{ctx.guild.id}", "channel_id": f"{ctx.channel.id}", "message_id": f'{msg.id}', "time": int(time.time() + 20) })


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shop(self, ctx):
        if reactions.count({ "guild_id": f"{ctx.guild.id}", "user_id": f"{ctx.author.id}", "type": "shop" }) > 0:
            e = discord.Embed(title="Магазин Паймон", description="Воспользуйтесь уже открытым магазином или дождитесь его окончания.", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=e)
        custom = bgs.count({ "id": { "$gte": 1 } })
        roles = shops.count({"type": "roles", "guild": f"{ctx.guild.id}"})
        e = discord.Embed(title="Магазин Паймон", description="Для выбора магазина используйте кнопки", color=discord.Color(0x2F3136))
        e.add_field(name="```Индекс```", value="```1```", inline=True)
        e.add_field(name="```Категория```", value="```Молитвы```", inline=True)
        e.add_field(name="```Предметов```", value=f"```2```", inline=True)
        e.add_field(name="```Индекс```", value="```2```", inline=True)
        e.add_field(name="```Категория```", value="```Кастомизация```", inline=True)
        e.add_field(name="```Предметов```", value=f"```{custom}```", inline=True)
        e.add_field(name="```Индекс```", value="```3```", inline=True)
        e.add_field(name="```Категория```", value="```Роли```", inline=True)
        e.add_field(name="```Предметов```", value=f"```{roles}```", inline=True)
        e.add_field(name="```Индекс```", value="```4```", inline=True)
        e.add_field(name="```Категория```", value="```Подписки```", inline=True)
        e.add_field(name="```Предметов```", value=f"```1```", inline=True)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        one = self.bot.get_emoji(826888313448562758)
        two = self.bot.get_emoji(826888462116061234)
        three = self.bot.get_emoji(826888462027194410)
        four = self.bot.get_emoji(826888461994557519)
        mess = await ctx.send(embed=e, components=[
            [
                Button(emoji=one, id='shop_1', style=ButtonStyle.gray),
                Button(emoji=two, id='shop_2', style=ButtonStyle.gray),
                Button(emoji=three, id='shop_3', style=ButtonStyle.gray),
                Button(emoji=four, id='shop_4', style=ButtonStyle.gray,)
            ]
        ])
        reactions.insert_one({ "type": "shop", "user_id": f"{ctx.author.id}", "guild_id": f"{ctx.guild.id}", "channel_id": f"{ctx.channel.id}", "message_id": f'{mess.id}', "time": int(time.time() + 20) })

def setup(bot):
    bot.add_cog(Economy(bot))