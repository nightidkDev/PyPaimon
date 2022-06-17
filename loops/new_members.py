import discord
from discord.ext import commands
from discord_components import *
import datetime
import time
import random
import os
import sys
sys.path.append("../../")
import config

async def welcomeusers(bot):
    wusers = config.wusers
    if len(wusers) != 0:
        wusersstr = ", ".join(f"<@!{user}>" for user in wusers)
        e = discord.Embed(title=f"<a:Z_s_ay:767983210591289414>  Встречаем {'нового участника' if len(wusers) == 1 else 'новых участников'}!", description=f"{wusersstr}, добро пожаловать в наше комьюнити!\n{'Чувствуй' if len(wusers) == 1 else 'Чувствуйте'} себя как дома ( •̀ ω •́ )✧ Чтобы {'тебе' if len(wusers) == 1 else 'вам'} было легче ориентироваться на сервере, {'прочитай' if len(wusers) == 1 else 'прочитайте'} [приветствие](https://discord.gg/ewP3UkqjEA) и [правила](https://discord.gg/4HgY9Nz5Kd) <a:A_heart13:767745438115299349>", color=discord.Color(0x2F3136))
        try:
            if len(wusers) == 1:
                user = bot.get_guild(604083589570625555).get_member(int(wusers[0]))
                e.set_thumbnail(url=user.avatar_url)
        except:
            pass
        channel = bot.get_guild(604083589570625555).get_channel(766351044380721202)
        await channel.send(embed=e)
    config.wusers = []