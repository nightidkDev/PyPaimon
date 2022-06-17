from python_gelbooru import AsyncGelbooru
import random
import discord
from discord.ext import commands
import asyncio
from discord_components import *
import datetime

loop = asyncio.get_event_loop()
api_key, user_id = ("86b094ee62392b0dbbd8d8d6385823dee57aca5b1c9024fae6bf70d880fe8687", "928542") 

def is_channel_me():
    def predicate(ctx):
        return ctx.message.channel.id == 927296029336961134
    return commands.check(predicate)

class NSFW_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='arts')
    @commands.check_any(commands.is_nsfw(), is_channel_me())
    async def arts(self, ctx, *args):
        search2 = "_".join(args)
        search2 = search2.lower().strip().replace(" ", "_")
        #a = await rule34.getImages(f"{search}_(genshin_impact)")
        async with AsyncGelbooru(api_key=api_key,
                             user_id=user_id) as gel:
            a = await gel.search_posts([f"{'_'.join(args)} genshin_impact", 'rating:explicit'], limit=100, random=True, exclude_tags='loli')
            if len(args) > 0:
               b = await gel.search_posts([f"{args[0]}_(genshin_impact)", *list(args)[1:], 'rating:explicit'], limit=100, random=True, exclude_tags='loli')
            else:
               b = tuple([])
            c = await gel.search_posts([*list(args), "genshin_impact", 'rating:explicit'], limit=100, random=True, exclude_tags='loli')
    

        if a is None:
            a = tuple([])
        if b is None:
            b = tuple([])
        if c is None:
            c = tuple([])

        d = tuple(a) + b + c
        if len(d) != 0:
            image = random.choice(d)
            e = discord.Embed(color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            tag = f"Поиск по названию \"{' '.join(args)}\"" if len(args) > 0 else "Рандомный арт" 
            e.set_author(name=tag)
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.set_image(url=image.file_url)
            await ctx.reply(embed=e)
        else:
            e = discord.Embed(color=0x2f3136)
            e.description = "Ничего не найдено."
            e.timestamp = datetime.datetime.utcnow()
            e.set_author(name=f"Поиск по названию \"{' '.join(args)}\"")
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=e)

def setup(bot):
    bot.add_cog(NSFW_Cog(bot))