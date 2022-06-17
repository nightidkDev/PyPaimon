import discord
from discord import errors
from discord.ext import commands
import datetime
import asyncio
import time
import random
import os
import re
import sys
import string
sys.path.append("../../")
from plugins import funcb
import config 


# DataBase
#import pymongo
#login_url = config.uri
#mongoclient = pymongo.MongoClient(login_url)
#db = mongoclient.aimi

class ErrorsLog(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time_cd = round(error.retry_after)
            e = discord.Embed(title="", description=f"Подождите перед применением данной команды еще {time_cd} {funcb.declension(['секунду', 'секунды', 'секунд'], time_cd)}", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            return await ctx.send(embed = e)
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.NotOwner):
            e = discord.Embed(description="Данная команда недоступна.", color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            return ctx.send(embed=e)
        elif isinstance(error, commands.MessageNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            e = discord.Embed(description="Данная команда недоступна.", color=0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=e)
        elif isinstance(error, discord.errors.NotFound):
            return
        elif isinstance(error, RuntimeWarning):
            return
        else:
            print(error)
            
def setup(client):
    client.add_cog(ErrorsLog(client))