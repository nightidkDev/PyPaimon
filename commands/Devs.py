import discord, asyncio, aiohttp, os, sys, time, datetime, random, requests, aeval
from discord.ext import commands, tasks
import pymongo
import config
mc = pymongo.MongoClient(config.uri)
db = mc.aimi
mc2 = pymongo.MongoClient(config.uri2)
db2 = mc.aimi
users = db.prof_ec_users

def is_admin_paimon():
    def predicate(ctx):
        return f"{ctx.author.id}" in config.ADMINS 
    return commands.check(predicate)

def minify_text(txt):
    try:
        if len(txt) >= 1024:
            return f'''{str(txt)[:-900]}...
            ...и ещё {len(str(txt).replace(str(txt)[:-900], ""))} символов...'''
        else:
            return str(txt)
    except:
        if len(repr(txt)) >= 1024:
            return f'''{repr(txt)[:-900]}...
            ...и ещё {len(repr(txt).replace(repr(txt)[:-900], ""))} символов...'''
        else:
            return repr(txt)


class DevCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='checkwarning', aliases=['checkw'])
    @commands.check_any(commands.has_guild_permissions(administrator=True), is_admin_paimon(), commands.is_owner(), commands.has_role(767084198816776262))
    async def checkwarning(self, ctx, member: discord.Member=None):
        if member is None:
            return
        user = users.find_one({ "disid": f"{member.id}", "guild": f'{ctx.guild.id}' })
        warning_system = user['warns_counter_system']
        warns = user['warns']
        warns_count = len(warns)
        e = discord.Embed(color=0x2f3136)
        e.description = f"У пользователя {member.mention} {'3' if warning_system >= 9 else '2' if warning_system >= 6 else '1' if warning_system >= 3 else '0'} уровень предупреждений с {warns_count} предупреждениями в данный момент."
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @commands.command(name='setwarning', aliases=['setw'])
    @commands.check_any(commands.has_guild_permissions(administrator=True), is_admin_paimon(), commands.is_owner(), commands.has_role(767084198816776262))
    async def setwarning(self, ctx, member: discord.Member=None, level=None):
        if member is None:
            return
        if level is None:
            return
        try:
            level = int(level)
        except:
            return
        user = users.find_one({ "disid": f"{member.id}", "guild": f'{ctx.guild.id}' })
        warns_count = len(user['warns'])
        if level == 0:
            warnings = 0 + warns_count
            role = None
        elif level == 1:
            warnings = 3 + warns_count
            role = 876711190091423816
        elif level == 2:
            warnings = 6 + warns_count
            role = 876714788732952637
        elif level == 3:
            warnings = 9 + warns_count
            role = 876771661628731432
        else:
            return
        users.update_one({ "disid": f"{member.id}", "guild": f'{ctx.guild.id}' }, { "$set": { "warns_counter_system": warnings } })
        try:
            role_1 = ctx.guild.get_role(876711190091423816)
            role_2 = ctx.guild.get_role(876714788732952637)
            role_3 = ctx.guild.get_role(876771661628731432)
            await member.remove_roles(role_1)
            await member.remove_roles(role_2)
            await member.remove_roles(role_3)
        except:
            pass
        try:
            role = ctx.guild.get_role(role)
            await member.add_roles(role)
        except:
            pass
        e = discord.Embed(color=0x2f3136)
        e.description = f"У пользователя {member.mention} установлен {level} уровень предупреждений с {warns_count} предупреждениями в данный момент."
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)

    @commands.command()
    @commands.check_any(commands.has_guild_permissions(administrator=True), is_admin_paimon())
    async def members(self, ctx, role: discord.Role=None):
        if role is None:
            return
        count_users = len(role.members)
        users = role.members
        e1 = discord.Embed(color=0x2f3136)
        e1.timestamp = datetime.datetime.utcnow()
        e1.set_author(name=f"С ролью \"{role.name}\" {count_users} человек(а)")
        e2 = discord.Embed(color=0x2f3136)
        e2.timestamp = datetime.datetime.utcnow()
        e3 = discord.Embed(color=0x2f3136)
        e3.timestamp = datetime.datetime.utcnow()
        e3.set_footer(text=f"Запросил: {ctx.author.name}", icon_url=ctx.author.avatar_url)
        e4 = discord.Embed(color=0x2f3136)
        e4.set_author(name=f"С ролью \"{role.name}\" {count_users} человек(а)")
        e4.timestamp = datetime.datetime.utcnow()
        e4.set_footer(text=f"Запросил: {ctx.author.name}", icon_url=ctx.author.avatar_url)

        users_msg = [""]
        count_messages = 0
        for x in range(len(users)):
            if len(users_msg[count_messages] + f"{x + 1}. {users[x].mention}") > 2000:
                count_messages += 1
                users_msg.append("")
            else:
                users_msg[count_messages] += f"{x + 1}. {users[x].mention}\n"
        for z in range(len(users_msg)):
            if z == 0 and z == len(users_msg) - 1:
                e4.description = users_msg[z]
                await ctx.send(embed=e4)
            elif z == 0:
                e1.description = users_msg[z]
                await ctx.send(embed=e1)
            elif z == len(users_msg) - 1:
                e3.description = users_msg[z]
                await ctx.send(embed=e3)
            else:
                e2.description = users_msg[z]
                await ctx.send(embed=e2)
            

    @commands.command(aliases = ['eval', 'aeval', 'evaulate', 'выполнить', 'exec', 'execute'])
    @commands.is_owner()
    async def __eval(self, ctx, *, content):
        #if ctx.author.id not in self.bot.owner_ids: return await ctx.reply("Кыш!") # Защита от os.system('format C') :)
        # Проверка на то, записан ли код в Markdown'овском блоке кода и его "очистка":
        code = "\n".join(content.split("\n")[1:])[:-3] if content.startswith("```") and content.endswith("```") else content
        standart_args = { # Стандартные библиотеки и переменные, которые будут определены в коде. Для удобства. Кстати, я уже добавил несколько встроенных либ и переменных из d.py
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "tasks": tasks,
            "ctx": ctx,
            "asyncio": asyncio,
            "aiohttp": aiohttp,
            "os": os,
            'sys': sys,
            "time": time,
            "datetime": datetime,
            "random": random,
            "requests": requests,
            "db": db,
            "config": config,
            'server': ctx.guild
        }
        start = time.time() # запись стартового таймстампа для расчёта времени выполнения
        try:
            r = await aeval.aeval(f"""{code}""", standart_args, {}) # выполняем код
            ended = time.time() - start # рассчитываем конец выполнения
            if not code.startswith('#nooutput'): # Если код начинается с #nooutput, то вывода не будет
                embed = discord.Embed(title = "Успешно!", description = f"Выполнено за: {ended}", color = 0x99ff99)
                """
                Есть нюанс: если входные/выходные данные будут длиннее 1024 символов, то эмбед не отправится, а функция выдаст ошибку.
                Именно поэтому сверху стоит print(r), а так же есть функция minify_text, которая
                минифицирует текст для эмбеда во избежание БэдРеквеста (который тут возникает когда слишком много символов). Поставил специально лимит на 900, чтобы точно хватило
                """
                embed.add_field(name = f'Входные данные:', value = f'```py\n{minify_text(code) }\n```')
                embed.add_field(name = f'Выходные данные:', value = f'```py\n{minify_text(r) }\n```', inline=False) 
                await ctx.send(embed = embed) # Отправка, уиии
            if "#console" in code:
                print(r)
        except Exception as e: # Ловим ошибки из строки с выполнением нашего кода (и не только!)
            ended = time.time() - start # Сново считаем время, но на этот раз до ошибки
            if not code.startswith('#nooutput'): # Аналогично коду выше
                code = minify_text(code)
                embed = discord.Embed(title = f"При выполнении возникла ошибка.\nВремя: {ended}", description = f'Ошибка:\n```py\n{e}```', color = 0xff0000)
                embed.add_field(name = f'Входные данные:', value = f'```py\n{minify_text(code)}\n```', inline=False)
                await ctx.send(embed = embed)
            if "#console" in code:
                raise e # Ну и поднимем исключение
            

def setup(bot):
    bot.add_cog(DevCog(bot))