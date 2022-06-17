import datetime
import pymongo
import os
import discord
import time
import random
import sys
import psutil
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [
            ["musicbots|mb", mb, "flood", "all"]
            ]

async def mb(client, message, command, messageArray, lang_u):
    musicbots = [791378184972664833, 888022607025291295, 888023871377268796, 614109280508968980, 679643572814741522, 634695585508884505, 201503408652419073, 184405311681986560]
    emojibots = [888028095230124062, 888028016104570941, 888028058316050433, 821079227532705911, 821079227763523604, 821079227729182781, 821080479708086343, 821079227389706332]
    mbf = [ [True, False, False, True], [True, False, False, True], [True, False, False, True], [False, True, True, False], [False, True, True, False], [False, True, True, False], [True, True, True, False], [True, False, True, False]]
    prefixs = ["v.", "z.", "r.", "*", "**", "***", "_", ";;"]

    spotify = client.get_emoji(821079227788034098)
    broken_spotyfy = client.get_emoji(888407152551677972)
    youtube = client.get_emoji(821079227419328574)
    soundcloud = client.get_emoji(821079227603484714)

    offline = client.get_emoji(769574358225649675)
    free = client.get_emoji(769574358603399188)
    busy = client.get_emoji(769574358711926784)
    e = discord.Embed(title="", description="", color=3092790)
    e.set_author(name="Статус музыкальных ботов:", icon_url="https://cdn.discordapp.com/attachments/666234650758348820/821151899033403422/musical-note_1.png")
    e.description = f"""
{youtube} - поддерживает YouTube
{spotify} - поддерживает Spotify полностью.
{broken_spotyfy} - поддерживает Spotify, но не полностью. (берёт название песни из Spotify и ищет на YouTube)
{soundcloud} - поддерживает SoundCloud  
"""
    for i in range(len(musicbots)):
        member = message.guild.get_member(musicbots[i])
        if member.status != discord.Status.offline:
            if member.voice != None:
                e.add_field(name=f"{client.get_emoji(emojibots[i])} {member.name}", value=f"> Статус: {busy}\n> Префикс: `{prefixs[i]}`\n> Возможности:\n> {youtube if mbf[i][0] else ''}{f' {broken_spotyfy}' if mbf[i][3] else ''}{f' {spotify}' if mbf[i][1] else ''}{f' {soundcloud}' if mbf[i][2] else ''}", inline=True)
            else:
                e.add_field(name=f"{client.get_emoji(emojibots[i])} {member.name}", value=f"> Статус: {free}\n> Префикс: `{prefixs[i]}`\n> Возможности:\n> {youtube if mbf[i][0] else ''}{f' {broken_spotyfy}' if mbf[i][3] else ''}{f' {spotify}' if mbf[i][1] else ''}{f' {soundcloud}' if mbf[i][2] else ''}", inline=True)
        else:
            e.add_field(name=f"{client.get_emoji(emojibots[i])} {member.name}", value=f"> Статус: {offline}\n> Префикс: `{prefixs[i]}`\n> Возможности:\n> {youtube if mbf[i][0] else ''}{f' {broken_spotyfy}' if mbf[i][3] else ''}{f' {spotify}' if mbf[i][1] else ''}{f' {soundcloud}' if mbf[i][2] else ''}", inline=True)
    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
    e.timestamp = datetime.datetime.utcnow()
    await message.channel.send(embed=e)
        

