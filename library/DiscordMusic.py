import asyncio
from ctypes import Array
import aiohttp
import re
from discord import player
from pymitter import EventEmitter
#import spotify
import json
import spotipy
import time
import spotipy.util as util
import random
from library import SpotifyAPI
import config
from library import music_cfg

music_cfg.player_queue = None

event = EventEmitter()

try:
    import youtube_dl
    import discord
    has_voice = True
except ImportError:
    has_voice = False

if has_voice:
    youtube_dl.utils.bug_reports_message = lambda: ''
    ydl = youtube_dl.YoutubeDL({ "cookiefile": "youtube.com_cookies.txt", "format": "bestaudio/best", "restrictfilenames": True, "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": True, "logtostderr": False, "quiet": True, "no_warnings": True, "source_address": "0.0.0.0"})

class EmptyQueue(Exception):
    """Cannot skip because queue is empty"""
    
class NotConnectedToVoice(Exception):
    """Cannot create the player because bot is not connected to voice"""
    
class NotPlaying(Exception):
    """Cannot <do something> because nothing is being played"""
    
async def ytbettersearch(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
    index = html.find('watch?v')
    url = ""
    while True:
        char = html[index]
        if char == '"':
            break
        url += char
        index += 1
    url = f"https://www.youtube.com/{url}"
    return url

async def get_video_data_spotify(url, loop):
    ytdl = youtube_dl.YoutubeDL({ "cookiefile": "youtube.com_cookies.txt", "format": "bestaudio/best", "restrictfilenames": True, "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": True, "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", "source_address": "0.0.0.0"})
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    try:
        data = data["entries"][0]
    except KeyError or TypeError:
        pass
    del ytdl
    source = data["url"]
    url = "https://www.youtube.com/watch?v="+data["id"]
    title = data["title"]
    description = data["description"]
    #likes = data["like_count"]
    #dislikes = data["dislike_count"]
    views = data["view_count"]
    duration = data["duration"]
    thumbnail = data["thumbnail"]
    channel = data["uploader"]
    channel_url = data["uploader_url"]
    return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False)
    
def check_playlist_spotify(url):
    token = SpotifyAPI.SpotifyAPI(config.SpotifyClientID, config.SpotifySecretClient).get_access_token()
    spt = spotipy.Spotify(auth=token)
    uid = url.split("/")[4].split("?")[0]
    tracks = spt.playlist_tracks(uid)
    if tracks['total'] > 100:
        return False
    else:
        return True

async def spotifysearch(url, loop):
    # "https://open.spotify.com/track/3akmS7ykvjBnDwiAgDXipd?si=8e7e1bfc1e0c4a4d"
    #url = "Rumble In The Jungle - Original Mix"
    token = SpotifyAPI.SpotifyAPI(config.SpotifyClientID, config.SpotifySecretClient).get_access_token()
    spt = spotipy.Spotify(auth=token)
    type_track = url.split("/")[3]
    uid = url.split("/")[4].split("?")[0]
    if type_track == "track":
        track = spt.track(uid)
        song = await get_video_data_spotify(f'{track["name"]} - {track["album"]["artists"][0]["name"]}', loop=loop)
        return song
        #return data
    elif type_track == "playlist":
        songs = []
        tracks = spt.playlist_tracks(uid)
        #with open("tracks_playlist.json", "w") as f:
        #    json.dump(tracks, f)
        start_x = int(time.time())
        #songs = list(map(lambda x: await get_video_data_spotify(f'{x["track"]["name"]} - {x["track"]["album"]["artists"][0]["name"]}', loop=loop), tracks['items']))
        for i in range(len(tracks['items'])):
           #start_x = int(time.time())
           track = tracks['items'][i]['track']
           #print(track["name"])
           #print(track)
           #break
           song = await get_video_data_spotify(f'{track["name"]} - {track["album"]["artists"][0]["name"]}', loop=loop)
           songs.append(song)
           #end_x = int(time.time())
           #print(end_x - start_x)
        end_x = int(time.time())
        print(end_x - start_x)
        return songs


def is_url(url):
    if re.match(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", url):
        return True
    else:
        return False

def yss(url):
    if is_url(url):
        if "youtube.com" in url or "youtu.be" in url:
            return ["youtube", False]
        elif "spotify.com":
            return ["spotify", False]
    else:
        return ["youtube", True]

async def get_video_data(url, search, bettersearch, loop, playlist=False):
    if not has_voice:
        raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")
    type_search, bettersearch = yss(url)
    if type_search == "spotify":
        res = await spotifysearch(url, loop)
        return res
    if not search and not bettersearch:
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        if playlist:
            videos = data["entries"]
            songs = []
            for i in range(len(videos)):
                source = videos[i]["url"]
                url = "https://www.youtube.com/watch?v="+videos[i]["id"]
                title = videos[i]["title"]
                description = videos[i]["description"]
                #likes = videos[i]["like_count"]
                #dislikes = videos[i]["dislike_count"]
                views = videos[i]["view_count"]
                duration = videos[i]["duration"]
                thumbnail = videos[i]["thumbnail"]
                channel = videos[i]["uploader"]
                channel_url = videos[i]["uploader_url"]
                songs.append(Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False))
            #print(songs)
            return songs
        else:
            source = data["url"]
            url = "https://www.youtube.com/watch?v="+data["id"]
            title = data["title"]
            description = data["description"]
            #likes = data["like_count"]
            #dislikes = data["dislike_count"]
            views = data["view_count"]
            duration = data["duration"]
            thumbnail = data["thumbnail"]
            channel = data["uploader"]
            channel_url = data["uploader_url"]
            return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False)
    else:
        if bettersearch:
            url = await ytbettersearch(url)
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            source = data["url"]
            url = "https://www.youtube.com/watch?v="+data["id"]
            title = data["title"]
            description = data["description"]
            #likes = data["like_count"]
            #dislikes = data["dislike_count"]
            views = data["view_count"]
            duration = data["duration"]
            thumbnail = data["thumbnail"]
            channel = data["uploader"]
            channel_url = data["uploader_url"]
            return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False)
        elif search:
            ytdl = youtube_dl.YoutubeDL({ "cookiefile": "youtube.com_cookies.txt", "format": "bestaudio/best", "restrictfilenames": True, "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": True, "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", "source_address": "0.0.0.0"})
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            try:
                data = data["entries"][0]
            except KeyError or TypeError:
                pass
            del ytdl
            source = data["url"]
            url = "https://www.youtube.com/watch?v="+data["id"]
            title = data["title"]
            description = data["description"]
            #likes = data["like_count"]
            #dislikes = data["dislike_count"]
            views = data["view_count"]
            duration = data["duration"]
            thumbnail = data["thumbnail"]
            channel = data["uploader"]
            channel_url = data["uploader_url"]
            return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False)

def check_queue(ctx, opts, music, after, on_play, loop):
    if not has_voice:
        raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")
    try:
        song = music.queue[ctx.guild.id][0]
    except IndexError:
        return
    if not song.is_looping:
        try:
            music.queue[ctx.guild.id].pop(0)
        except IndexError:
            return
        if len(music.queue[ctx.guild.id]) > 0:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(music.queue[ctx.guild.id][0].source, **opts))
            ctx.voice_client.play(source, after=lambda error: after(ctx, opts, music, after, on_play, loop))
            song = music.queue[ctx.guild.id][0]
            if on_play:
                loop.create_task(on_play(ctx, song))
            event.emit("on_next", ctx=ctx, song=song, loop=loop)
    else:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(music.queue[ctx.guild.id][0].source, **opts))
        ctx.voice_client.play(source, after=lambda error: after(ctx, opts, music, after, on_play, loop))
        song = music.queue[ctx.guild.id][0]
        if on_play:
            loop.create_task(on_play(ctx, song))
    

class Music(object):
    def __init__(self):
        if not has_voice:
            raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")
        self.queue = {}
        self.players = []
    def create_player(self, ctx, **kwargs):
        if not ctx.voice_client:
            raise NotConnectedToVoice("Cannot create the player because bot is not connected to voice")
        player = MusicPlayer(ctx, self, **kwargs)
        self.players.append(player)
        return player
    def get_player(self, **kwargs):
        guild = kwargs.get("guild_id")
        channel = kwargs.get("channel_id")
        for player in self.players:
            if guild and channel and player.ctx.guild.id == guild and player.voice.channel.id == channel:
                return player
            elif not guild and channel and player.voice.channel.id == channel:
                return player
            elif not channel and guild and player.ctx.guild.id == guild:
                return player
        else:
            return None

class MusicPlayer(object):
    def __init__(self, ctx, music, **kwargs):
        if not has_voice:
            raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")
        music_cfg.player_queue = Player(False, False, 0, 0)
        self.ctx = ctx
        self.voice = ctx.voice_client
        self.loop = ctx.bot.loop
        self.music = music
        if self.ctx.guild.id not in self.music.queue.keys():
            self.music.queue[self.ctx.guild.id] = []
        #self.after_func = check_queue
        self.on_play_func = self.on_queue_func = self.on_skip_func = self.on_stop_func = self.on_pause_func = self.on_resume_func = self.on_loop_toggle_func = self.on_volume_change_func = self.on_remove_from_queue_func = None
        ffmpeg_error = kwargs.get("ffmpeg_error_betterfix", kwargs.get("ffmpeg_error_fix"))
        if ffmpeg_error and "ffmpeg_error_betterfix" in kwargs.keys():
            self.ffmpeg_opts = {"options": "-vn -loglevel quiet -hide_banner -nostats", "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin"}
        elif ffmpeg_error:
            self.ffmpeg_opts = {"options": "-vn", "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin"}
        else:
            self.ffmpeg_opts = {"options": "-vn", "before_options": "-nostdin"}
    def disable(self):
        self.music.players.remove(self)
    def on_queue(self, func):
        self.on_queue_func = func
    def on_play(self, func):
        self.on_play_func = func
    def on_skip(self, func):
        self.on_skip_func = func
    def on_stop(self, func):
        self.on_stop_func = func
    def on_pause(self, func):
        self.on_pause_func = func
    def on_resume(self, func):
        self.on_resume_func = func
    def on_loop_toggle(self, func):
        self.on_loop_toggle_func = func
    def on_volume_change(self, func):
        self.on_volume_change_func = func
    def on_remove_from_queue(self, func):
        self.on_remove_from_queue_func = func
    async def queue(self, url, search=False, bettersearch=False, playlist=False):
        songs = await get_video_data(url, search, bettersearch, self.loop, playlist)
        #print(type(songs))
        if type(songs) == list:
            #print('-------------------------')
            #print(self.music.queue[self.ctx.guild.id])
            #print(songs)
            #print('-------------------------')
            self.music.queue[self.ctx.guild.id] = self.music.queue[self.ctx.guild.id] + songs
            if self.on_queue_func:
                await self.on_queue_func(self.ctx, songs[0])
            return songs
        else:
            self.music.queue[self.ctx.guild.id].append(songs)
            if self.on_queue_func:
                await self.on_queue_func(self.ctx, songs)
            return songs
        
        
    async def play(self):
        #print(self.music.queue[self.ctx.guild.id])
        music_cfg.player_queue.is_playing = True
        music_cfg.player_queue.time_play = int(time.time())
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.music.queue[self.ctx.guild.id][0].source, **self.ffmpeg_opts))
        #loop = asyncio.get_event_loop()
        self.voice.play(source, after=lambda error: check_queue(self.ctx, self.ffmpeg_opts, self.music, check_queue, self.on_play_func, self.loop))
        song = self.music.queue[self.ctx.guild.id][0]
        if self.on_play_func:
            await self.on_play_func(self.ctx, song)
        return song
    async def skip(self, force=False):
        if len(self.music.queue[self.ctx.guild.id]) == 0:
            raise NotPlaying("Cannot loop because nothing is being played")
        elif not len(self.music.queue[self.ctx.guild.id]) > 1 and not force:
            music_cfg.player_queue.is_playing = False
            raise EmptyQueue("Cannot skip because queue is empty")
        else:
            old = self.music.queue[self.ctx.guild.id][0]
            old.is_looping = False if old.is_looping else False
            self.voice.stop()
            try:
                new = self.music.queue[self.ctx.guild.id][1]
                if self.on_skip_func:
                    await self.on_skip_func(self.ctx, old, new)
                return (old, new)
            except IndexError:
                if self.on_skip_func:
                    await self.on_skip_func(self.ctx, old)
                return old        
    async def stop(self):
        try:
            self.music.queue[self.ctx.guild.id] = []
            self.voice.stop()
            self.music.players.remove(self)
            music_cfg.player_queue.is_playing = False
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if self.on_stop_func:
            await self.on_stop_func(self.ctx)
    async def pause(self):
        try:
            self.voice.pause()
            music_cfg.player_queue.is_paused = True
            music_cfg.player_queue.time_stop = int(time.time())
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot pause because nothing is being played")
        if self.on_pause_func:
            await self.on_pause_func(self.ctx, song)
        return song
    async def resume(self):
        try:
            self.voice.resume()
            music_cfg.player_queue.is_paused = False
            music_cfg.player_queue.time_play = int(time.time()) - (music_cfg.player_queue.time_stop - music_cfg.player_queue.time_play)
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot resume because nothing is being played")
        if self.on_resume_func:
            await self.on_resume_func(self.ctx, song)
        return song
    def current_queue(self):
        try:
            return [self.music.queue[self.ctx.guild.id], music_cfg.player_queue]
        except KeyError:
            raise EmptyQueue("Queue is empty")
    def now_playing(self):
        try:
            return [self.music.queue[self.ctx.guild.id][0], music_cfg.player_queue]
        except:
            return [None, music_cfg.player_queue]
    async def toggle_song_loop(self):
        try:
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if not song.is_looping:
            song.is_looping = True
        else:
            song.is_looping = False
        if self.on_loop_toggle_func:
            await self.on_loop_toggle_func(self.ctx, song)
        return song
    def suffle_queue(self):
        try:
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        queue_for_shuffle = self.music.queue[self.ctx.guild.id][1:]
        random.shuffle(queue_for_shuffle)
        #queue_for_shuffle = list(map(lambda x: x[0], queue_for_shuffle))
        self.music.queue[self.ctx.guild.id] = [song] + queue_for_shuffle
    async def change_volume(self, vol):
        self.voice.source.volume = vol
        try:
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if self.on_volume_change_func:
            await self.on_volume_change_func(self.ctx, song, vol)
        return [song, vol]
    async def remove_from_queue(self, index):
        if index == 0:
            try:
                song = self.music.queue[self.ctx.guild.id][0]
            except:
                raise NotPlaying("Cannot loop because nothing is being played")
            await self.skip(force=True)
            return song
        song = self.music.queue[self.ctx.guild.id][index]
        self.music.queue[self.ctx.guild.id].pop(index)
        if self.on_remove_from_queue_func:
            await self.on_remove_from_queue_func(self.ctx, song)
        return song
    def delete(self):
        self.music.players.remove(self)
        
class Song(object):
    def __init__(self, source, url, title, description, views, duration, thumbnail, channel, channel_url, loop):
        self.source = source
        self.url = url
        self.title = title
        self.description = description
        self.views = views
        self.name = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.channel = channel
        self.channel_url = channel_url
        self.is_looping = loop

class Player(object):
    def __init__(self, is_playing, is_paused, time_play, time_stop):
        self.is_playing = is_playing
        self.is_paused = is_paused
        self.time_play = time_play
        self.time_stop = time_stop