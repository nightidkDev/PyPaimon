import discord
from discord.ext import commands
import pymongo
import time
import os
import sys
import datetime
sys.path.append("../../")
import config
from discord_components import *
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
users = db.prof_ec_users
rb_db = db.mutes
servers = db.server
mutes = db.mutes
lb = db.lb
staff = db.staff

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}д. {h:d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:d}:{s:02d}"

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    @commands.check_any(commands.has_any_role(760218179447685142, 767084198816776262), commands.has_permissions(administrator=True))
    async def lb(self, ctx, member: discord.Member=None, *reason):
        if not member:
            e = discord.Embed(color=0x2f3136)
            e.description = f"Укажите пользователя."
            e.set_author(name="Выдача локал бана участнику")
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if ctx.author.id == member.id:
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.description = f"Ты не можешь выдать локал бан себе."
            return await ctx.send(embed=e)
        if ctx.guild.owner_id == member.id:
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.description = f"Ты не можешь выдать локал бан владельцу сервера."
            return await ctx.send(embed=e)
        if ctx.guild.owner_id != ctx.author.id and ((member.top_role >= ctx.author.top_role) and member.top_role.id != 885610515743772752):
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.description = f"Данный пользователь находится на одной роли с тобой или выше."
            return await ctx.send(embed=e)
        lb_role = ctx.guild.get_role(767626360965038080)
        if lb_role in member.roles:
            e = discord.Embed(color=0x2f3136)
            e.description = f"Участник {member.mention} уже имеет локал бан."
            e.set_author(name="Выдача локал бана участнику")
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if len(reason) == 0:
            reason = "Не указана."
        else:
            reason = " ".join(reason)
        e = discord.Embed(color=0x2f3136)
        e.description = f"Участник {member.mention} получил локал бан от {ctx.author.mention} по причине **{reason}**"
        e.set_author(name="Выдача локал бана участнику")
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)
        for role in member.roles:
            if role.id == ctx.guild.id:
                continue
            try:
                await member.remove_roles(role)
            except:
                pass
        await member.add_roles(lb_role)
        if lb.count_documents({"id": str(member.id) }) == 0:
            users.update_one({"disid": str(member.id), "guild": str(ctx.guild.id)}, { "$set": { "view": "false" } })
            lb.insert_one({"id": str(member.id) })
    
    @commands.command()
    @commands.check_any(commands.has_any_role(760218179447685142, 767084198816776262), commands.has_permissions(administrator=True))
    async def unlb(self, ctx, member: discord.Member=None):
        if not member:
            e = discord.Embed(color=0x2f3136)
            e.description = f"Укажите пользователя."
            e.set_author(name="Снятие локал бана с участника")
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        if ctx.author.id == member.id:
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.description = f"Ты не можешь снять локал бан с себя."
            return await ctx.send(embed=e)
        if ctx.guild.owner_id == member.id:
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.description = f"Ты не можешь снять локал бан у владельца сервера."
            return await ctx.send(embed=e)
        if ctx.guild.owner_id != ctx.author.id and ((member.top_role >= ctx.author.top_role) and member.top_role.id != 885610515743772752):
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.description = f"Данный пользователь находится на одной роли с тобой или выше."
            return await ctx.send(embed=e)
        lb_role = ctx.guild.get_role(767626360965038080)
        if lb_role not in member.roles:
            e = discord.Embed(color=0x2f3136)
            e.description = f"Участник {member.mention} уже не имеет локал бан."
            e.set_author(name="Снятие локал бана с участника")
            e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=e)
        e = discord.Embed(color=0x2f3136)
        e.description = f"С участника {member.mention} снят локал бан\nСнял: {ctx.author.mention}"
        e.set_author(name="Снятие локал бана с участника")
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)
        await member.remove_roles(lb_role)
        if lb.count_documents({"id": str(member.id) }) != 0:
            users.update_one({"disid": str(member.id), "guild": str(ctx.guild.id)}, { "$set": { "view": "true" } })
            lb.delete_one({"id": str(member.id) })

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, user: discord.User):
        e = discord.Embed(color=0x2f3136)
        e.description = f"Участник {user.mention} получил разбан от {ctx.author.mention}."
        e.set_author(name="Разбан участника")
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)
        await ctx.guild.unban(user)

    @commands.command()
    @commands.check_any(commands.has_role(761771540181942273), commands.has_permissions(administrator=True))
    async def warn(self, ctx, user: discord.Member=None, *reason_warn):
        message = ctx.message
        emoji_1 = self.bot.get_emoji(780831508600062003)
        emoji_2 = self.bot.get_emoji(794180012299124737)
        e = discord.Embed(title=f"{emoji_1} {emoji_2} ♡ Выдача предупреждения", description="", color=discord.Colour(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        if user is None:
            e.description = f"Участник не найден."
            return await message.channel.send(embed=e)
        else:
            if users.count_documents({"disid": str(user.id), "guild": str(message.guild.id)}) == 0:
                e.description = f"Участник не найден."
                return await message.channel.send(embed=e)
            else:
                if message.author.id == user.id:
                    e.description = f"Ты не можешь выдать предупреждение себе."
                    return await message.channel.send(embed=e)
                if message.guild.owner_id == user.id:
                    e.description = f"Ты не можешь выдать предупреждение владельцу сервера."
                    return await message.channel.send(embed=e)
                if message.guild.owner_id != message.author.id and ((user.top_role >= message.author.top_role) and user.top_role.id != 885610515743772752):
                    e.description = f"Данный пользователь находится на одной роли с тобой или выше."
                    return await message.channel.send(embed=e)
                data11 = mutes.find_one({"disid": f"{user.id}", "guild": f"{message.guild.id}" })
                if mutes.count_documents({"disid": f"{user.id}", "guild": f"{message.guild.id}" }) == 1:
                    time_now = int(time.time())
                    left_t = int(data11['time_mute']) - time_now
                    return await message.channel.send(f"Этот пользователь уже имеет мут. Осталось: {seconds_to_hh_mm_ss(left_t)}")
                reason = ""
                userdb = users.find_one({"disid": str(user.id), "guild": str(message.guild.id) })
                if len(reason_warn) == 0:
                    reason = "Не указана"
                else:
                    reason += " ".join(reason_warn)
                    reason.strip()
                    if reason == "":
                        reason = "Не указана"
                reason = reason.strip()
                index = len(userdb["warns"])
                index_system = userdb["warns_counter_system"]
                index_r = 0
                if index_system < index:
                    index_r = index - index_system
                    users.update_one({ "disid": f"{user.id}", "guild": f"{message.guild.id}" }, { "$inc": { "warns_counter_system": index_r } })
                    index_system += index_r
                warn_info = { 
                    "index": index + 1, 
                    "mod": str(message.author.id), 
                    "reason": reason, 
                    "time": int(time.time() + 10800) 
                }
                users.update_one({"disid": str(user.id), "guild": str(message.guild.id)}, { "$push": { "warns": { "$each": [ warn_info ] }, "history_warns": { "$each": [ warn_info ] } } })
                users.update_one({ "disid": f"{user.id}", "guild": f"{message.guild.id}" }, { "$inc": { "warns_counter_system": 1 } })
                e.description = f"Участник <@!{user.id}> получил предупреждение #{index + 1}, причина: **{reason}**."
                if index + 1 >= 3:
                    role_id = servers.find_one({"server": str(message.guild.id)})["roleid_mute"]
                    rb = message.guild.get_role(int(role_id))
                    
                    x = int(time.time())
                    warn_roles = [876711190091423816, 876714788732952637, 876771661628731432]
                    warn1 = message.guild.get_role(warn_roles[0])
                    warn2 = message.guild.get_role(warn_roles[1])
                    warn3 = message.guild.get_role(warn_roles[2])
                    if index_system + 1 >= 9:
                        if index_system + 1 >= 9:
                            try:
                                await user.remove_roles(warn2)
                            except:
                                pass
                            try:
                                await user.add_roles(warn3)
                            except:
                                pass
                        xn = x + 172800
                        mute_text = "2 дня"
                    elif index_system + 1 >= 6:
                        try:
                            await user.remove_roles(warn1)
                        except:
                            pass
                        try:
                            await user.add_roles(warn2)
                        except:
                            pass
                        xn = x + 86400
                        mute_text = "24 часа"
                    elif index_system + 1 >= 3:
                        try:
                            await user.add_roles(warn1)
                        except:
                            pass
                        xn = x + 43200
                        mute_text = "12 часов"
                        
                    rb_db.insert_one({"disid": str(user.id), "time_mute": str(xn), "guild": str(message.guild.id), "mod": str(message.author.id), "roleid": str(rb.id), "reason": "Авто-мут 3/3 предупреждений."})
                    users.update_one({"disid": str(user.id), "guild": str(message.guild.id)}, { "$set": { "warns": [] } })
                    await user.add_roles(rb, reason="Warns 3/3")
                    e.description = f"Участник <@!{user.id}> получил предупреждение #{index + 1} из 3 возможных, за это ему была выдана роль <@&{rb.id}>. Она будет снята через `🕒` {mute_text}. \nПричина: **{reason}**."
                    if user.voice is not None:
                        voice_m = user.voice.channel
                        await user.edit(voice_channel=voice_m, reason="muted.")
                await message.channel.send(embed=e)
                try:
                    await user.send(embed=e)
                except:
                    await message.guild.get_channel(766390214267764786).send(content=f"<@!{user.id}>", embed=e)
                        
    @commands.command()
    @commands.check_any(commands.has_role(761771540181942273), commands.has_permissions(administrator=True))
    async def fstats(self, ctx, vorc=None, fstatstime=None, member: discord.Member=None):
        if member is None:
            if len(ctx.message.mentions) > 0:
                member = ctx.message.mentions[0]
        else:
            if member.bot:
                member = ctx.author
        if member is None:
            member = ctx.author

        if vorc != "chat" and vorc != 'voice':
            return await ctx.reply('Укажите какую статистику вывести: voice или chat', delete_after=3.5)

        #if users.count({ "id": f"{member.id}" }) == 0:
        #    user_info = config.db_user_example.copy()
        #    user_info['id'] = f"{member.id}"
        #    users.insert_one(user_info)

        user = staff.find_one({ "id": f"{member.id}" })

        fstatstime_code = ''
        if fstatstime == '7d':
            fstatstime_code = '7d'
        elif fstatstime == '14d':
            fstatstime_code = '14d'
        elif fstatstime == '30d':
            fstatstime_code = '30d'
        else:
            return await ctx.reply('Укажите какую статистику вывести: 7d/14d/30d', delete_after=3.5)

        e1 = discord.Embed(color=0x2f3136)
        e1.set_author(name=f"{'Войс' if vorc == 'voice' else 'Чат'}-статистика {member} за {'7 дней' if fstatstime_code == '7d' else '14 дней' if fstatstime_code == '14d' else '30 дней'}")
        e2 = discord.Embed(color=0x2f3136)
        e3 = discord.Embed(color=0x2f3136)
        e3.timestamp = datetime.datetime.utcnow()
        e3.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e4 = discord.Embed(color=0x2f3136)
        e4.set_author(name=f"{'Войс' if vorc == 'voice' else 'Чат'}-статистика {member} за {'7 дней' if fstatstime_code == '7d' else '14 дней' if fstatstime_code == '14d' else '30 дней'}")
        e4.timestamp = datetime.datetime.utcnow()
        e4.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

        stat = user['stats'][fstatstime_code]['c_channels' if vorc == 'chat' else 'v_channels']
        stat_list = list(stat.items())
        sorted_stat_list = sorted(stat_list, key=lambda x: x[1], reverse=True)
        stat_msg = [""]
        count_messages = 0
        for x in range(len(sorted_stat_list)):
            channel = self.bot.get_channel(int(sorted_stat_list[x][0]))
            if channel is None:
                channel_name = "удаленный-канал"
            else:
                channel_name = channel.name.replace("`", "")
            if len(stat_msg[count_messages] + f"{x + 1}. #{channel_name}: {seconds_to_hh_mm_ss(sorted_stat_list[x][1]) if vorc == 'voice' else sorted_stat_list[x][1]}\n") > 2000:
                count_messages += 1
                stat_msg.append("")
            stat_msg[count_messages] += f"{x + 1}. #{channel_name}: {seconds_to_hh_mm_ss(sorted_stat_list[x][1]) if vorc == 'voice' else sorted_stat_list[x][1]}\n"

        for z in range(len(stat_msg)):
            if z == 0 and z == len(stat_msg) - 1:
                e4.description = '```css\n' + 'Активность не найдена.' + '\n```' if stat_msg[z] == '' else '```css\n' + stat_msg[z] + '\n```'
                await ctx.send(embed=e4)
            elif z == 0:
                e1.description = '```css\n' + stat_msg[z] + '\n```'
                await ctx.send(embed=e1)
            elif z == len(stat_msg) - 1:
                e3.description = '```css\n' + stat_msg[z] + '\n```'
                await ctx.send(embed=e3)
            else:
                e2.description = '```css\n' + stat_msg[z] + '\n```'
                await ctx.send(embed=e2)

    @commands.command()
    @commands.check_any(commands.has_role(761771540181942273), commands.has_permissions(administrator=True))
    async def unwarn(self, ctx, user: discord.Member=None):
        message = ctx.message
        emoji_1 = self.bot.get_emoji(780831508600062003)
        emoji_2 = self.bot.get_emoji(794180012299124737)
        e = discord.Embed(title=f"{emoji_1} {emoji_2} ♡ Снятие предупреждения", description="", color=discord.Colour(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        if user is None:
            e.description = f"Участник не найден."
            return await message.channel.send(embed=e)
        else:
            if users.count_documents({"disid": str(user.id), "guild": str(message.guild.id)}) == 0:
                e.description = f"Участник не найден."
                return await message.channel.send(embed=e)
            else:
                if message.author.id == user.id:
                    e.description = f"Ты не можешь снять предупреждение себе."
                    return await message.channel.send(embed=e)
                if message.guild.owner_id == user.id:
                    e.description = f"Ты не можешь снять предупреждение у владельца сервера."
                    return await message.channel.send(embed=e)
                if message.guild.owner_id != message.author.id and ((user.top_role >= message.author.top_role) and user.top_role.id != 885610515743772752):
                    e.description = f"Данный пользователь находится на одной роли с тобой или выше."
                    return await message.channel.send(embed=e)
                userdb = users.find_one({"disid": str(user.id), "guild": str(message.guild.id) })
                if len(userdb["warns"]) == 0:
                    e.description = f"У участника не обнаружено предупреждений."
                    return await message.channel.send(embed=e)
                users.update_one({"disid": str(user.id), "guild": str(message.guild.id)}, { "$pop": { "warns": 1 } })
                e.description = f"Предупреждение с <@!{user.id}> было снято, теперь у него {len(userdb['warns']) - 1}/3."
                await message.channel.send(embed=e)
                try:
                    await user.send(embed=e)
                except:
                    await message.guild.get_channel(766390214267764786).send(content=f"<@!{user.id}>", embed=e)

    @commands.command()
    @commands.is_owner()
    async def cw(self, ctx, *messageArray):
        message = ctx.message
        if len(messageArray) == 0 or messageArray[0] == "":
            return await message.channel.send("unknown member")
        else:
            if len(message.mentions) != 0:
                if users.count_documents({"disid": str(message.mentions[0].id), "guild": str(message.guild.id) }) == 0:
                    return await message.channel.send("unknown member")
                else:
                    users.update_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}, { "$set": { "warns": [] } })
    
    @commands.command()
    @commands.check_any(commands.has_role(761771540181942273), commands.has_permissions(administrator=True))
    async def warns(self, ctx, *messageArray):
        message = ctx.message
        emoji_1 = self.bot.get_emoji(780831508600062003)
        emoji_2 = self.bot.get_emoji(794180012299124737)
        e = discord.Embed(title=f"", description="", color=discord.Colour(0x2F3136))
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        if len(messageArray) == 0 or messageArray[0] == "":
            user = users.find_one({"disid": str(message.author.id), "guild": str(message.guild.id) })
            warns = ''
            for elem in user["warns"]:
                index = elem["index"]
                mod = elem["mod"]
                reason = elem["reason"]
                time_w = elem["time"]
                warns += f"#{index}. Выдано предупреждение от <@!{mod}> в {datetime.datetime.utcfromtimestamp(time_w).strftime('%d.%m.%Y %H:%M:%S')} с причиной: {reason}\n"
            if warns == "":
                warns = "Предупреждений не найдено."
            e.description = warns
            e.title = f"{emoji_1} {emoji_2} ♡ Предупреждения `{message.author}`"
            await message.channel.send(embed=e)
        else:
            if len(message.mentions) != 0:
                if users.count_documents({"disid": str(message.mentions[0].id), "guild": str(message.guild.id)}) == 0:
                    e.description = f"Участник не найден."
                    return await message.channel.send(embed=e)
                user = users.find_one({"disid": str(message.mentions[0].id), "guild": str(message.guild.id) })
                warns = ''
                for elem in user["warns"]:
                    index = elem["index"]
                    mod = elem["mod"]
                    reason = elem["reason"]
                    time_w = elem["time"]
                    warns += f"#{index}. Выдано предупреждение от <@!{mod}> в {datetime.datetime.utcfromtimestamp(time_w).strftime('%d.%m.%Y %H:%M:%S')} с причиной: {reason}\n"
                if warns == "":
                    warns = "Предупреждений не найдено."
                e.description = warns
                e.title = f"{emoji_1} {emoji_2} ♡ Предупреждения `{message.mentions[0]}`"
                await message.channel.send(embed=e)

def setup(bot):
    bot.add_cog(Moderation(bot))