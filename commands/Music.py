# Discord
import asyncio
import discord
from discord.ext import commands
from discord.utils import get
from discord_components import *
from library import DiscordMusic
from discord_components import Select, SelectOption, Button, ButtonStyle

# Librares
import datetime
import time
import random
import os
import sys
import time
import json
sys.path.append("../../")
import config

def is_admin_paimon():
    def predicate(ctx):
        return f"{ctx.author.id}" in config.ADMINS or ctx.author.id in [517447209504079873]
    return commands.check(predicate)

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    if seconds >= 3600:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"
    
def is_integer(value):
    try:
        value = int(value)
        return True
    except:
        return False

# Music Library
music = DiscordMusic.Music()
musicevent = DiscordMusic.event

def func_chunk(lst, n):
    for x in range(0, len(lst), n):
        e_c = lst[x : n + x]
        yield e_c

@musicevent.on("on_next")
def on_next(ctx, song, loop):
    emoji_queue = ctx.bot.get_emoji(891340769108058112)
    emoji_play = ctx.bot.get_emoji(891340743979982858)
    emoji_stop = ctx.bot.get_emoji(891340757313650698)
    player = music.get_player(guild_id=ctx.guild.id)
    queue, player_queue = player.current_queue()
    e = discord.Embed(color=0xe3a5f9)
    e.set_author(name="Сейчас играет", url=song.url, icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
    e.set_thumbnail(url=song.thumbnail)
    e.description = f"**Название**: `{song.name}`"
    e.add_field(name="```В канале```", value="```" + ctx.author.voice.channel.name + "```", inline=True)
    e.add_field(name="```Длительность```", value=f"```{seconds_to_hh_mm_ss(song.duration)}```", inline=True)
    e.add_field(name="```Треков в очереди```", value=f"```{len(queue) - 1}```", inline=True)
    e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    e.timestamp = datetime.datetime.utcnow()
    components = [
        [  
            Button(label="Пауза", emoji=emoji_play, id="music_pause"),
            Button(label="Стоп", emoji=emoji_stop, id="music_stop"),
            Button(label="Очередь", emoji=emoji_queue, id="music_queue")
        ]
    ]
    DiscordMusic.music_cfg.player_queue.time_play = int(time.time())
    loop.create_task(ctx.send(embed=e, components=components))

async def players_check(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        x = int(time.time())
        with open("./players.json") as f:
            plyrs = json.load(f)
        for el in plyrs.copy():
            guild = bot.get_guild(int(el))
            vc_bot = get(bot.voice_clients, guild=guild)
            player = music.get_player(guild_id=guild.id)
            if not vc_bot:
                del plyrs[el]
                if player:
                    player.delete()
                await bot.change_presence(status=discord.Status.idle)
            elif plyrs[el] <= x:
                await vc_bot.disconnect()
                if player:
                    player.delete()
                del plyrs[el]
                await bot.change_presence(status=discord.Status.idle)

        with open("./players.json", "w") as f:
            f.write(json.dumps(plyrs))
        
        await asyncio.sleep(10)

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        if not inter.component.id.startswith('music_'):
            return
        member = inter.user
        bot_member = inter.message.guild.get_member(self.bot.user.id)
        player = music.get_player(guild_id=inter.guild.id)
        vc_bot = get(self.bot.voice_clients, guild=inter.guild)
        if not player or not vc_bot:
            e = discord.Embed(color=0xe3a5f9)
            e.description = "Данная реакция больше недоступна."
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=member.name, icon_url=member.avatar_url)
            return await inter.respond(embed=e)
        if inter.component.id == "music_pause":
            if not member.voice:
                e = discord.Embed(color=0xe3a5f9)
                e.description = "Вы не находитесь в голосовом канале бота."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
            if member.voice.channel != bot_member.voice.channel:
                e = discord.Embed(color=0xe3a5f9)
                e.description = "Вы не находитесь в голосовом канале бота."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
            if vc_bot.is_paused():
                try:
                    await player.resume()
                    e = discord.Embed(color=0xe3a5f9)
                    e.description = "Воспроизводение продолжено."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    return await inter.respond(embed=e)
                except DiscordMusic.NotPlaying:
                    e = discord.Embed(color=0xe3a5f9)
                    e.description = "Нечего воспроизводить."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    return await inter.respond(embed=e)
            else:
                try:
                    await player.pause()
                    e = discord.Embed(color=0xe3a5f9)
                    e.description = "Поставлена пауза."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    return await inter.respond(embed=e)
                except DiscordMusic.NotPlaying:
                    e = discord.Embed(color=0xe3a5f9)
                    e.description = "Нечего останавливать."
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    return await inter.respond(embed=e)
        elif inter.component.id == "music_stop":
            if not member.voice:
                e = discord.Embed(color=0xe3a5f9)
                e.description = "Вы не находитесь в голосовом канале бота."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
            if member.voice.channel != bot_member.voice.channel:
                e = discord.Embed(color=0xe3a5f9)
                e.description = "Вы не находитесь в голосовом канале бота."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
            
            try:
                await player.stop()
                e = discord.Embed(color=0xe3a5f9)
                e.description = "Воспроизведение музыки остановлено, очередь очищена."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
            except DiscordMusic.NotPlaying:
                e = discord.Embed(color=0xe3a5f9)
                e.description = "Нечего останавливать."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
        elif inter.component.id == "music_queue":
            nextpageemoji = self.bot.get_emoji(826567984901390366)
            backpageemoji = self.bot.get_emoji(826568061854416946)
            try:
                queue, player_queue = player.current_queue()
                queue_str = ""
                if len(queue) == 0:
                    queue_str = "Очередь пустая."
                    components = []
                else:
                    if len(queue) <= 8:
                        for i in range(len(queue)):
                            if i == 0:
                                queue_str += f"Сейчас играет: `{queue[i].name}` - `{seconds_to_hh_mm_ss(queue[i].duration)}` [Осталось: `{seconds_to_hh_mm_ss(queue[i].duration - (int(time.time()) - player_queue.time_play)) if not player_queue.is_paused else seconds_to_hh_mm_ss(queue[i].duration - (player_queue.time_stop - player_queue.time_play))}`]\n\n"
                            else:
                                queue_str += f"{i}. `{queue[i].name}` - `{seconds_to_hh_mm_ss(queue[i].duration)}`\n"
                        components = []
                    else:
                        for i in range(8):
                            if i == 0:
                                queue_str += f"Сейчас играет: `{queue[i].name}` - `{seconds_to_hh_mm_ss(queue[i].duration)}` [Осталось: `{seconds_to_hh_mm_ss(queue[i].duration - (int(time.time()) - player_queue.time_play)) if not player_queue.is_paused else seconds_to_hh_mm_ss(queue[i].duration - (player_queue.time_stop - player_queue.time_play))}`]\n\n"
                            else:
                                queue_str += f"{i}. `{queue[i].name}` - `{seconds_to_hh_mm_ss(queue[i].duration)}`\n"
                        components = [
                            [
                                Button(emoji=nextpageemoji, id="music_queue_nextpage_2")
                            ]
                        ]
                e = discord.Embed(color=0xe3a5f9)
                e.description = queue_str
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e, components=components)
            except DiscordMusic.EmptyQueue:
                e = discord.Embed(color=0xe3a5f9)
                e.description = "Очередь пустая."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
        elif inter.component.id.startswith("music_queue_nextpage"):
            nextpageemoji = self.bot.get_emoji(826567984901390366)
            backpageemoji = self.bot.get_emoji(826568061854416946)
            try:
                queue, player_queue = player.current_queue()
            except DiscordMusic.EmptyQueue:
                e = discord.Embed(color=0xe3a5f9)
                e.description = "Очередь пустая."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
            interList = inter.component.id.split("_")
            page = int(interList[3])
            queue_list = list(func_chunk(queue, 8))
            queue_str = ""
            for i in range(len(queue_list[page-1])):
                get_index = queue.index(queue_list[page-1][i])
                queue_str += f"{get_index}. `{queue_list[page-1][i].name}` - `{seconds_to_hh_mm_ss(queue_list[page-1][i].duration)}`\n"

            if len(queue_list) <= page:
                components = [
                    [
                        Button(emoji=backpageemoji, id=f"music_queue_backpage_{page - 1}")
                    ]
                ]
            else:
                components = [
                    [
                        Button(emoji=backpageemoji, id=f"music_queue_backpage_{page - 1}"),
                        Button(emoji=nextpageemoji, id=f"music_queue_nextpage_{page + 1}")
                    ]
                ]
            e = discord.Embed(color=0xe3a5f9)
            e.description = queue_str
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=member.name, icon_url=member.avatar_url)
            return await inter.respond(type=7, embed=e, components=components)
        elif inter.component.id.startswith("music_queue_backpage"):
            nextpageemoji = self.bot.get_emoji(826567984901390366)
            backpageemoji = self.bot.get_emoji(826568061854416946)
            try:
                queue, player_queue = player.current_queue()
            except DiscordMusic.EmptyQueue:
                e = discord.Embed(color=0xe3a5f9)
                e.description = "Очередь пустая."
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                return await inter.respond(embed=e)
            interList = inter.component.id.split("_")
            page = int(interList[3])
            queue_list = list(func_chunk(queue, 8))
            queue_str = ""
            for i in range(len(queue_list[page-1])):
                get_index = queue.index(queue_list[page-1][i])
                if get_index == 0:
                    queue_str += f"Сейчас играет: `{queue_list[page-1][i].name}` - `{seconds_to_hh_mm_ss(queue_list[page-1][i].duration)}` [Осталось: `{seconds_to_hh_mm_ss(queue_list[page-1][i].duration - (int(time.time()) - player_queue.time_play)) if not player_queue.is_paused else seconds_to_hh_mm_ss(queue_list[page-1][i].duration - (player_queue.time_stop - player_queue.time_play))}`]\n\n"
                else:
                    queue_str += f"{get_index}. `{queue_list[page-1][i].name}`  - `{seconds_to_hh_mm_ss(queue_list[page-1][i].duration)}`\n"

            if page - 1 == 0:
                components = [
                    [
                        Button(emoji=nextpageemoji, id=f"music_queue_nextpage_{page + 1}")
                    ]
                ]
            else:
                components = [
                    [
                        Button(emoji=backpageemoji, id=f"music_queue_backpage_{page - 1}"),
                        Button(emoji=nextpageemoji, id=f"music_queue_nextpage_{page + 1}")
                    ]
                ]
            e = discord.Embed(color=0xe3a5f9)
            e.description = queue_str
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=member.name, icon_url=member.avatar_url)
            return await inter.respond(type=7, embed=e, components=components)
        #if inter.components[0].id == "queue":


    @commands.command(name="join", aliases=['j'])
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def join(self, ctx):
        if ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот уже находится в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if not ctx.author.voice:
            e = discord.Embed(title='', description='Вы не находитесь в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
          
        await ctx.author.voice.channel.connect()
        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            player = music.create_player(ctx, ffmpeg_error_betterfix=True)
        else:
            player.delete()
            player = music.create_player(ctx, ffmpeg_error_betterfix=True)

        await self.bot.change_presence(status=discord.Status.dnd)

        e = discord.Embed(title='', description='Я присоединилась к вашему голосовому каналу', color=0xe3a5f9)
        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)
    
    @commands.command(name="leave")
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def leave(self, ctx):
        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находится в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if not ctx.author.voice:
            e = discord.Embed(title='', description='Вы нe находитесь в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if ctx.guild.me.voice.channel != ctx.author.voice.channel:
            e = discord.Embed(title='', description='Вы не находитесь в голосовом канале с ботом', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
          
        vc_bot = ctx.voice_client
        if vc_bot is None:
            await ctx.guild.me.edit(voice_channel=None)
        else:
            await vc_bot.disconnect()
        
        player = music.get_player(guild_id=ctx.guild.id)
        try:
            player.delete()
        except:
            pass
            
        await self.bot.change_presence(status=discord.Status.idle)

        e = discord.Embed(title='', description='Я покинула ваш голосовой канал', color=0xe3a5f9)
        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)
        
    # @commands.command(name="queue", aliases=["q"])
    # @commands.has_role(838734399818301471)
    # async def queue(self, ctx):
    #     if not ctx.guild.me.voice:
    #         e = discord.Embed(title='', description='Бот не находится в голосовом канале', color=0xe3a5f9)
    #         e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    #         e.timestamp = datetime.datetime.utcnow()
    #         return await ctx.send(embed=e)

    @commands.command(name="loop")
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def loop(self, ctx):
        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находится в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if not ctx.author.voice:
            e = discord.Embed(title='', description='Вы нe находитесь в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if ctx.guild.me.voice.channel != ctx.author.voice.channel:
            e = discord.Embed(title='', description='Вы не находитесь в голосовом канале с ботом', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            return
        try:
            await player.toggle_song_loop()
        except DiscordMusic.NotPlaying:
            e = discord.Embed(title='', description='Нечего повторять.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if player.now_playing()[0].is_looping:
            e = discord.Embed(title='', description='Повтор одной песни включён.', color=0xe3a5f9)
        else:
            e = discord.Embed(title='', description='Повтор одной песни отключён.', color=0xe3a5f9)
        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @commands.command(name="pause")
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def pause(self, ctx):
        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находится в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if not ctx.author.voice:
            e = discord.Embed(title='', description='Вы нe находитесь в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if ctx.guild.me.voice.channel != ctx.author.voice.channel:
            e = discord.Embed(title='', description='Вы не находитесь в голосовом канале с ботом', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            e = discord.Embed(title='', description='Нечего останавливать.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not ctx.voice_client.is_paused():
            e = discord.Embed(title='', description='Воспроизведение поставлено на паузу.', color=0xe3a5f9)
            try:
                await player.pause()
            except DiscordMusic.NotPlaying:
                e = discord.Embed(title='', description='Нечего останавливать.', color=0xe3a5f9)
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                return await ctx.send(embed=e)
        else:
            e = discord.Embed(title='', description='Пауза и так поставлена.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @commands.command(name="stop")
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def stop(self, ctx):
        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находится в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if not ctx.author.voice:
            e = discord.Embed(title='', description='Вы нe находитесь в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if ctx.guild.me.voice.channel != ctx.author.voice.channel:
            e = discord.Embed(title='', description='Вы не находитесь в голосовом канале с ботом', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            e = discord.Embed(title='', description='Нечего останавливать и очищать.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        try:
            await player.stop()
        except DiscordMusic.NotPlaying:
            e = discord.Embed(title='', description='Нечего останавливать.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        e = discord.Embed(title='', description='Воспроизведение музыки остановлено, очередь очищена.', color=0xe3a5f9)
        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @commands.command(name="skip")
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def skip(self, ctx):
        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находится в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if not ctx.author.voice:
            e = discord.Embed(title='', description='Вы нe находитесь в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if ctx.guild.me.voice.channel != ctx.author.voice.channel:
            e = discord.Embed(title='', description='Вы не находитесь в голосовом канале с ботом', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            e = discord.Embed(title='', description='Нечего пропускать.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        try:
            old, new = await player.skip()
            e = discord.Embed(title='', description=f'Песня пропущена, теперь воспроизводиться `{new.name}`', color=0xe3a5f9)
        except DiscordMusic.NotPlaying:
            e = discord.Embed(title='', description='Нечего пропускать.', color=0xe3a5f9)
        except DiscordMusic.EmptyQueue:
            e = discord.Embed(title='', description='Песня пропущена, а так как в очереди песен больше нет - воспроизведение остановлено.', color=0xe3a5f9)
            await player.stop()
        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @commands.command(name="resume")
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def resume(self, ctx):
        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находится в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if not ctx.author.voice:
            e = discord.Embed(title='', description='Вы нe находитесь в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if ctx.guild.me.voice.channel != ctx.author.voice.channel:
            e = discord.Embed(title='', description='Вы не находитесь в голосовом канале с ботом', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        
        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            e = discord.Embed(title='', description='Нечего останавливать.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if ctx.voice_client.is_paused():
            e = discord.Embed(title='', description='Воспроизведение возобновлено.', color=0xe3a5f9)
            try:
                await player.resume()
            except DiscordMusic.NotPlaying:
                e = discord.Embed(title='', description='Нечего возобновлять.', color=0xe3a5f9)
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                return await ctx.send(embed=e)
        else:
            e = discord.Embed(title='', description='Мелодия и так играет.', color=0xe3a5f9)
        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @commands.command(name="nowplaying", aliases=["np"])
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def nowplaying(self, ctx):

        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находиться в голосовом канале.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            e = discord.Embed(title='', description='Ничего не играет.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        np, player_queue = player.now_playing()

        if np is None:
            e = discord.Embed(color=0xe3a5f9)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = "Ничего не играет."
            await ctx.send(embed=e)
        else:
            e = discord.Embed(color=0xe3a5f9)
            e.timestamp = datetime.datetime.utcnow()
            # queue_str += f"Сейчас играет: `{queue[i].name}` - `{seconds_to_hh_mm_ss(queue[i].duration)}` [Осталось: `{seconds_to_hh_mm_ss(queue[i].duration - (int(time.time()) - player_queue.time_play)) if not player_queue.is_paused else seconds_to_hh_mm_ss(queue[i].duration - (player_queue.time_stop - player_queue.time_play))}`]\n\n"
            e.set_author(name=f"Сейчас играет", icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
            e.set_thumbnail(url=np.thumbnail)
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.description = f"""
Название: [{np.name}]({np.url})

Длительность: `{seconds_to_hh_mm_ss(int(time.time()) - player_queue.time_play) if not player_queue.is_paused else seconds_to_hh_mm_ss(player_queue.time_stop - player_queue.time_play)}`/`{seconds_to_hh_mm_ss(np.duration)}`
"""
            await ctx.send(embed=e)

    @commands.command(name="volume", aliases=["vol"])
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def change_volume(self, ctx, value=None):

        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находиться в голосовом канале.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            e = discord.Embed(title='', description='Ничего не играет.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not value:
            e = discord.Embed(title='', description='Укажите числовое значение от `0` до `100`.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if is_integer(value) is False:
            e = discord.Embed(title='', description='Укажите числовое значение от `0` до `100`.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        value = int(value)
        value2 = int(value) / 100
        if 100 < value or value < 0:
            e = discord.Embed(title='', description='Укажите числовое значение от `0` до `100`.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        song, val = await player.change_volume(value2)

        e = discord.Embed(color=0xe3a5f9)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"Значение громкости устновлено на `{value}`."
        await ctx.send(embed=e)

    @commands.command(name="shuffle")
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def suffle(self, ctx):
        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находиться в голосовом канале.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            e = discord.Embed(title='', description='Ничего не играет.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        try:
            player.suffle_queue()
        except DiscordMusic.NotPlaying:
            e = discord.Embed(title='', description='Нечего перемешивать.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        e = discord.Embed(color=0xe3a5f9)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"Треки в очереди были перемешаны."
        await ctx.send(embed=e)

    @commands.command(name="remove")
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def remove(self, ctx, value=None):
        if not ctx.guild.me.voice:
            e = discord.Embed(title='', description='Бот не находиться в голосовом канале.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            e = discord.Embed(title='', description='Ничего не играет.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not value:
            e = discord.Embed(title='', description='Укажите номер песни.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if is_integer(value) is False:
            e = discord.Embed(title='', description='Укажите числовое значение.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        queue, player_queue = player.current_queue()

        value = int(value)

        if value < 0 or value > len(queue):
            e = discord.Embed(title='', description=f'Укажите значение от `0` до `{len(queue)}`.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        try:
            song = await player.remove_from_queue(value)
        except DiscordMusic.NotPlaying:
            e = discord.Embed(title='', description='Нечего удалять.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        e = discord.Embed(color=0xe3a5f9)
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.description = f"Трек `{song.name}` был удален из очереди."
        await ctx.send(embed=e)
    
    @commands.command(name="play")
    @commands.check_any(commands.has_role(838734399818301471), is_admin_paimon())
    async def play(self, ctx, *, url=None):
        emoji_queue = self.bot.get_emoji(891340769108058112)
        emoji_play = self.bot.get_emoji(891340743979982858)
        emoji_stop = self.bot.get_emoji(891340757313650698)

        if not ctx.author.voice:
            e = discord.Embed(title='', description='Вы не находитесь в голосовом канале', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        
        if not url:
            e = discord.Embed(title='', description='Укажите ссылку на YouTube, Spotify или укажите название песни для поиска.', color=0xe3a5f9)
            e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)

        if not ctx.guild.me.voice:
            await ctx.author.voice.channel.connect()
            await self.bot.change_presence(status=discord.Status.dnd)
            player = music.get_player(guild_id=ctx.guild.id)
            if player:
                player.delete()
        else:
            if ctx.author.voice.channel != ctx.guild.me.voice.channel:
                e = discord.Embed(title='', description='Вы не находитесь в голосовом канале с ботом', color=0xe3a5f9)
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                return await ctx.send(embed=e)
            
            vc_bot = ctx.voice_client
            if vc_bot is None:
                await ctx.guild.me.edit(voice_channel=None)
                await ctx.author.voice.channel.connect()
                player = music.get_player(guild_id=ctx.guild.id)
                if player:
                    player.delete()
                await self.bot.change_presence(status=discord.Status.dnd)
            
        
        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            player = music.create_player(ctx, ffmpeg_error_betterfix=True)
        
        if len(player.current_queue()[0]) == 0:
            if "youtube.com" not in url and "youtu.be" not in url and not DiscordMusic.is_url:
                await player.queue(url, bettersearch=True)
                songs = None
            else:
                if "playlist" in url:
                    if "open.spotify.com" in url:
                        if not DiscordMusic.check_playlist_spotify(url):
                            e = discord.Embed(color=0xe3a5f9)
                            e.set_author(name="Добавление плейлиста", icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
                            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                            e.description = f"Бот в данный момент не поддерживает плейлисты из спотифая с более чем 100 треками."
                            e.timestamp = datetime.datetime.utcnow()
                            return await ctx.send(embed=e)
                    e = discord.Embed(color=0xe3a5f9)
                    e.set_author(name="Добавление плейлиста", icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
                    e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    loading = self.bot.get_emoji(794502101853798400)
                    e.description = f"{loading} Обработка..."
                    e.timestamp = datetime.datetime.utcnow()
                    msg = await ctx.send(embed=e)
                    songs = await player.queue(url, playlist=True)
                else:
                    songs = await player.queue(url)
            song = await player.play()
            if type(songs) == list:
                e = discord.Embed(color=0xe3a5f9)
                e.set_author(name="Добавлен плейлист", url=url, icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
                e.set_thumbnail(url=song.thumbnail)
                #e.description = f"**Название**: `{song.name}`"
                duration = 0
                for song1 in songs:
                    duration += song1.duration 
                e.add_field(name="```В канале```", value="```" + ctx.author.voice.channel.name + "```", inline=True)
                e.add_field(name="```Длительность```", value=f"```{seconds_to_hh_mm_ss(duration)}```", inline=True)
                e.add_field(name="```Треков в очереди```", value=f"```{len(songs)}```", inline=True)
                e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                await msg.edit(embed=e, components=[
                    [  
                        Button(label="Пауза", emoji=emoji_play, id="music_pause"),
                        Button(label="Стоп", emoji=emoji_stop, id="music_stop"),
                        Button(label="Очередь", emoji=emoji_queue, id="music_queue")
                    ]
                ])
            e = discord.Embed(color=0xe3a5f9)
            e.set_author(name="Сейчас играет", url=song.url, icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
            e.set_thumbnail(url=song.thumbnail)
            e.description = f"**Название**: `{song.name}`"
            e.add_field(name="```В канале```", value="```" + ctx.author.voice.channel.name + "```", inline=True)
            e.add_field(name="```Длительность```", value=f"```{seconds_to_hh_mm_ss(song.duration)}```", inline=True)
            if type(songs) == list:
                e.add_field(name="```Треков в очереди```", value=f"```{len(songs) - 1}```", inline=True)
            else:
                e.add_field(name="```Треков в очереди```", value=f"```0```", inline=True)
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=e, components=[
                [  
                    Button(label="Пауза", emoji=emoji_play, id="music_pause"),
                    Button(label="Стоп", emoji=emoji_stop, id="music_stop"),
                    Button(label="Очередь", emoji=emoji_queue, id="music_queue")
                ]
            ])
        else:
            if "youtube.com" not in url and "youtu.be" not in url and not DiscordMusic.is_url:
                song = await player.queue(url, bettersearch=True)
                songs = None
            else:
                if "playlist" in url:
                    if "open.spotify.com" in url:
                        if not DiscordMusic.check_playlist_spotify(url):
                            e = discord.Embed(color=0xe3a5f9)
                            e.set_author(name="Добавление плейлиста", icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
                            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                            e.description = f"Бот в данный момент не поддерживает плейлисты из спотифая с более чем 100 треками."
                            e.timestamp = datetime.datetime.utcnow()
                            return await ctx.send(embed=e)
                    e = discord.Embed(color=0xe3a5f9)
                    e.set_author(name="Добавление плейлиста", icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
                    e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    loading = self.bot.get_emoji(794502101853798400)
                    e.description = f"{loading} Обработка..."
                    e.timestamp = datetime.datetime.utcnow()
                    msg = await ctx.send(embed=e)
                    songs = await player.queue(url, playlist=True)
                else:
                    songs = await player.queue(url)
            if type(songs) == list:
                e = discord.Embed(color=0xe3a5f9)
                e.set_author(name="Добавлен плейлист", url=url, icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
                e.set_thumbnail(url=songs[0].thumbnail)
                #e.description = f"**Название**: `{song.name}`"
                duration = 0
                for song1 in songs:
                    duration += song1.duration 
                e.add_field(name="```В канале```", value="```" + ctx.author.voice.channel.name + "```", inline=True)
                e.add_field(name="```Длительность```", value=f"```{seconds_to_hh_mm_ss(duration)}```", inline=True)
                e.add_field(name="```Треков в очереди```", value=f"```{len(player.current_queue()[0]) - 1}```", inline=True)
                e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                await msg.edit(embed=e, components=[
                    [  
                        Button(label="Пауза", emoji=emoji_play, id="music_pause"),
                        Button(label="Стоп", emoji=emoji_stop, id="music_stop"),
                        Button(label="Очередь", emoji=emoji_queue, id="music_queue")
                    ]
                ])
            elif songs is not None:
                e = discord.Embed(color=0xe3a5f9)
                e.set_author(name="Добавлено в очередь", url=songs.url, icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
                e.set_thumbnail(url=songs.thumbnail)
                e.description = f"**Название**: `{songs.name}`"
                e.add_field(name="```В канале```", value="```" + ctx.author.voice.channel.name + "```", inline=True)
                e.add_field(name="```Длительность```", value=f"```{seconds_to_hh_mm_ss(songs.duration)}```", inline=True)
                e.add_field(name="```Треков в очереди```", value=f"```{len(player.current_queue()[0]) - 1}```", inline=True)
                e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                await ctx.send(embed=e, components=[
                    [  
                        Button(label="Пауза", emoji=emoji_play, id="music_pause"),
                        Button(label="Стоп", emoji=emoji_stop, id="music_stop"),
                        Button(label="Очередь", emoji=emoji_queue, id="music_queue")
                    ]
                ])
            else:
                e = discord.Embed(color=0xe3a5f9)
                e.set_author(name="Добавлено в очередь", url=song.url, icon_url="https://media.discordapp.net/attachments/666234650758348820/773179001178423296/1525276693_youtube-logo-hd-8_1.png?width=751&height=526")
                e.set_thumbnail(url=song.thumbnail)
                e.description = f"**Название**: `{song.name}`"
                e.add_field(name="```В канале```", value="```" + ctx.author.voice.channel.name + "```", inline=True)
                e.add_field(name="```Длительность```", value=f"```{seconds_to_hh_mm_ss(song.duration)}```", inline=True)
                e.add_field(name="```Треков в очереди```", value=f"```{len(player.current_queue()[0]) - 1}```", inline=True)
                e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                await ctx.send(embed=e, components=[
                    [  
                        Button(label="Пауза", emoji=emoji_play, id="music_pause"),
                        Button(label="Стоп", emoji=emoji_stop, id="music_stop"),
                        Button(label="Очередь", emoji=emoji_queue, id="music_queue")
                    ]
                ])
        
    
        
def setup(bot):
    bot.add_cog(MusicCog(bot))
    bot.loop.create_task(players_check(bot))