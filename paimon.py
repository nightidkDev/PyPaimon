import discord
from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument
import pymongo
from discord_components import *
from discord.utils import get
import config

# System Librares
import datetime
import time
import os
import asyncio
import json

# Plugins
from plugins import funcb
from libs.SelectLib import on_select

login_url = config.uri
login_url2 = config.uri2
mongoclient = pymongo.MongoClient(login_url)
db = mongoclient.aimi
mongoclient2 = pymongo.MongoClient(login_url2)
db2 = mongoclient.aimi
server = db.server
users = db.prof_ec_users
extended_sub = db2.extended_sub


prefix = '.'

bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all(), strip_after_prefix=True, case_insensitive=True)
bot.remove_command('help')

from loops import *

@tasks.loop(seconds=1)
async def loops():
    await reactions(bot)
    await role_wishes(bot)
    await specials_wishes(bot)
    await chat_wishes(bot)
    await voice_wishes(bot)
    await voice_wishes_hour(bot)
    await captcha1f(bot)
    await captcha2f(bot)
    await captcha3f(bot)
    await captchajail(bot)
    await clan_captcha(bot)
    await war_captcha_clan(bot)

@tasks.loop(seconds=30)
async def loops_30sec():
    await banner_counter(bot)
    await banner(bot)

@tasks.loop(minutes=1)
async def loops_60sec():
    await welcomeusers(bot)
    #await new_year_counter(bot)

@tasks.loop(minutes=1)
async def check_subs():
    guild = bot.get_guild(604083589570625555)
    role_sub = guild.get_role(912064706414526544)
    for user in extended_sub.find():
        if user["sub_pay_time"] + 2592000 < int(time.time()):
            member = guild.get_member(int(user['id']))
            try:
                await member.remove_roles(role_sub)
                e = discord.Embed(color=0x2f3136)
                e.description = f"Ваша подписка \"{role_sub.name}\" закончилась."
                e.set_footer(text=guild.name, icon_url=guild.avatar_url)
                await member.send(embed=e)
            except:
                pass
            extended_sub.delete_one({ 'id': user['id'] })
        else:
            continue

@tasks.loop(seconds=10)
async def players_check_stopped():
    for guild in bot.guilds:
        vc_bot = get(bot.voice_clients, guild=guild)
        if not vc_bot:
            if guild.get_member(bot.user.id):
                if guild.get_member(bot.user.id).voice:
                    await guild.get_member(bot.user.id).edit(voice_channel=None)
        else:
            if vc_bot.is_paused() or not vc_bot.is_playing():
                with open("./players.json") as f:
                    plyrs = json.load(f)
                exist = False
                for el in plyrs.copy():
                    if f"{guild.id}" in el:
                        exist = True
                if exist is False:
                    plyrs.update({ f"{guild.id}": int(time.time()) + 900 })
                with open("./players.json", "w") as f:
                    f.write(json.dumps(plyrs))
            if vc_bot.is_playing() and not vc_bot.is_paused():
                with open("./players.json") as f:
                    plyrs = json.load(f)
                exist = False
                for el in plyrs.copy():
                    #print(el)
                    if f"{guild.id}" in el:
                        del plyrs[el]
                with open("./players.json", "w") as f:
                    f.write(json.dumps(plyrs))

@bot.event
async def on_select_option(inter):
    await on_select(inter)

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        d = None
        with open("restart_info.json", "r") as ri:
            d = json.load(ri)
        c = bot.get_channel(d["restart_channel"])
        message_restart = await c.fetch_message(d["restart_message"])

        e3 = discord.Embed(title="", description="Перезагрузка завершена, все команды снова работают.", color=discord.Colour(0xff0000))
        time_r = int(time.time()) - d['restart']
        e3.set_footer(text=f"Перезагрузка заняла {time_r} {funcb.declension([ 'секунда', 'секунды', 'секунд' ], time_r)}.")
        await message_restart.edit(embed=e3)
    except BaseException as e:
        pass
    try:
        with open("/root/bots/restart_info.json") as f:
            restart_data = json.load(f)
        restart_data['bpaimon']['status'] = 1
        restart_data['bpaimon']['time'] = int(time.time())
        with open("/root/bots/restart_info.json", "w") as f:
            json.dump(restart_data, f)
        channel = await bot.get_user(751145877242118246)
        await channel.send("bp\ready")
    except BaseException:
        pass
    DiscordComponents(bot)
    #print(bot.get_cog("Music"))
    #print(bot.cogs)
    config.commands_allow = list(map(lambda x: x.name, bot.get_cog("Reactions").get_commands()))
    config.commands_allow.append("arts")
    config.commands_music = list(map(lambda x: x.name, bot.get_cog("MusicCog").get_commands()))
    print("--------------------------------")
    guild = bot.get_guild(604083589570625555)
    while not guild:
        guild = bot.get_guild(604083589570625555)
        print("Wait..")
        await asyncio.sleep(1)
    print("--------------------------------")
    print(f"[{datetime.datetime.utcfromtimestamp(int(time.time()) + 10800).strftime('%H:%M:%S')}] Запустилась Paimon.exe <3")
    print("--------------------------------")
    loops.start()
    loops_30sec.start()
    loops_60sec.start()
    players_check_stopped.start()
    #print(config.commands_allow)

@bot.event
async def on_error(err, *args, **kwargs):
    if err == "on_button_click" or err == "button_click" or err == "on_select_option" or err == "select_option":
        return

@bot.event
async def on_command_error(ctx, exc):
    if isinstance(exc, commands.NotOwner):
        e = discord.Embed(color=0x2f3136)
        #owner_bot = bot.get_user(252378040024301570)
        e.description = f"Данная команда недоступна."
        e.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.reply(embed=e)
    elif isinstance(exc, (commands.MissingAnyRole, commands.MissingPermissions, commands.MissingRole, commands.CommandNotFound, commands.NotOwner, commands.CommandOnCooldown)):
        return
    else:
        e = discord.Embed(color=0x2f3136)
        #owner_bot = bot.get_user(252378040024301570)
        e.description = f"```py\n{exc}\n``````py\nCommand: {ctx.message.content}\n```"
        e.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e, delete_after=5)

@bot.event
async def on_message(message):
    if message.channel.id == 794660897271578625 and not message.content.startswith(".tmute") and str(message.author.id) not in config.ADMINS:
        return
    if message.content == f"<@!{bot.user.id}>" or message.content == f"<@{bot.user.id}>":
        if message.channel.id in config.deny_channels:
            return
        if message.author.id != 252378040024301570:
            return
        e = discord.Embed(title="Paimon.exe [Beta]", description=f"Бот в рабочем состоянии.", color=discord.Color(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
        return await message.channel.send(embed=e)
    if message.content.lower().split(" ")[0][len(prefix):] in config.commands_music:
        return await bot.process_commands(message, check_bot=False, self_check=False)
    if message.guild:
        mute_role = message.guild.get_role(767025328405086218)
        lb_role = message.guild.get_role(767626360965038080)
        if mute_role in message.author.roles or lb_role in message.author.roles:
            if not message.content.startswith(".tmute") and message.content.lower().split(" ")[0][len(prefix):] not in config.commands_allow and bot.get_command(message.content.lower().split(" ")[0][len(prefix):]) is not None:
                if message.channel.id == 794660897271578625:
                    return
                else:
                    e = discord.Embed(title="", description=f"Все команды, кроме `.tmute` и команд-реакций, запрещены в мьюте или локал бане.", color=0x2F3136)
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                    await message.channel.send(embed=e)
                    time.sleep(3)
                    try:
                        await message.delete()
                    except:
                        pass
                    return
            elif message.content.startswith(".tmute"):
                await bot.process_commands(message, check_bot=False, self_check=False)
                time.sleep(3)
                try:
                    await message.delete()
                except:
                    pass
                return
            elif message.content.lower().split(" ")[0][len(prefix):] in config.commands_allow:
                await bot.process_commands(message, check_bot=False, self_check=False)
                return
            else:
                return
        else:
            if str(message.author.id) not in config.ADMINS:
                if message.channel.type == discord.ChannelType.private:
                    return
                elif bot.get_command(message.content.lower().split(" ")[0][len(prefix):]) and message.author.bot and message.author.id != 665667955220021250:
                    return
                elif bot.get_command(message.content.lower().split(" ")[0][len(prefix):]) and message.author.id == 665667955220021250:
                    await bot.process_commands(message, check_bot=False, self_check=False)
                    time.sleep(3)
                    try:
                        await message.delete()
                    except:
                        pass
                    return
                elif message.content.lower().split(" ")[0][len(prefix):] not in config.commands_allow and message.channel.id in config.NotFloodChannels:
                    return
                elif message.channel.id in config.deny_channels:
                    return
                elif message.content.lower().split(" ")[0][len(prefix):] not in config.commands_allow and bot.get_command(message.content.lower().split(" ")[0][len(prefix):]):
                    await bot.process_commands(message)
                    time.sleep(3)
                    try:
                        await message.delete()
                    except:
                        pass
                    return
                elif message.content.lower().split(" ")[0][len(prefix):] in config.commands_allow and bot.get_command(message.content.lower().split(" ")[0][len(prefix):]):
                    await bot.process_commands(message)
            elif bot.get_command(message.content.lower().split(" ")[0][len(prefix):]) and str(message.author.id) in config.ADMINS:
                if message.content.lower().split(" ")[0][len(prefix):] in config.commands_allow:
                    await bot.process_commands(message)
                else:
                    await bot.process_commands(message, check_bot=False, self_check=False)
                    time.sleep(3)
                    try:
                        await message.delete()
                    except:
                        pass
                    return
    else:
        return



for filename in os.listdir('./commands'):
    if filename.endswith('.py'):
        bot.load_extension(f'commands.{filename[:-3]}')
        print(f'[Cog] {filename[:-3]} подключен!')

for filename in os.listdir('./listeners'):
    if filename.endswith('.py'):
        bot.load_extension(f'listeners.{filename[:-3]}')
        print(f'[Listener] {filename[:-3]} подключен!')

# Run loops
"""
bot.loop.create_task(loops())
bot.loop.create_task(loops_30sec())
bot.loop.create_task(loops_60sec())
bot.loop.create_task(players_check_stopped())
"""

# Run client
bot.run(config.TOKEN)
