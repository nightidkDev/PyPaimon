from re import S
from sqlite3.dbapi2 import connect
import discord
from discord.ext.commands.core import has_any_role, has_permissions
from discord_components import ButtonStyle, Button, SelectOption, Select
from typing import Union
from discord.ext import commands
import asyncio
import datetime
import os
import sys
import random
import string
sys.path.append("../../")
import config
import pymongo
import re
mc = pymongo.MongoClient(config.uri2)
db = mc.aimi
events = db.events

def is_url(url):
    if re.match(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", url):
        return True
    else:
        return False

def create_uid():
    """ Создаёт UID из 20 символов"""
    numbers = [str(random.randint(0, 9)) for i in range(10)]
    letters = [random.choice(list(string.ascii_letters)) for i in range(10)]
    uid_list = numbers + letters
    random.shuffle(uid_list)
    return "".join(uid_list)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_button_click(self, inter):
        if inter.responded:
            return
        if not inter.component.id.startswith("events"):
            return

        user = inter.user
        message_inter = inter.message

        event_host, event_manager = message_inter.guild.get_role(768141743942008882), message_inter.guild.get_role(873997911111917598)
        if event_host not in user.roles and event_manager not in user.roles and not user.guild_permissions.administrator:
            return

        if inter.component.id == "events_home":
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=user.name, icon_url=user.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.title = "МУИ"
            e.description = """**Добро пожаловать в МУИ (Мастер Управления Ивентами).
        

Выберете действие для продолжения:
1. Создание нового ивента
2. Удаление ивентов
3. Выбор существующего ивента
4. Изменение существующего ивента**"""
            await inter.respond(type=7, embed=e, components=[
                Button(label="Создание нового ивента", style=ButtonStyle.green, id="events_create-new-events"),
                Button(label="Удаление ивентов", style=ButtonStyle.red, id="events_delete-events"),
                Button(label="Выбор существующего ивента", style=ButtonStyle.blue, id="events_choose-events"),
                Button(label="Изменение существующего ивента", style=ButtonStyle.gray, id="events_edit-events")
            ])

        elif inter.component.id == "events_edit-events":
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=user.name, icon_url=user.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.title = "МУИ"
            e.description = """Выберете ивент, который хотите отредактировать."""
            events_list = list(events.find({}))
            options = []
            for event in events_list:
                member = inter.message.guild.get_member(int(event['created_by']))
                options.append(SelectOption(label=f"{event['name']}", value=f"events_edit-{event['uid']}", description=f'Created by: {member}'))
            if options == []:
                options.append(SelectOption(label="Увы, ивентов не найдено.", value='None', default=True))
            await inter.respond(type=7, embed=e, components=[
                Select(options=options, id="events_edit-event", placeholder='Список ивентов', disabled=True if options[0].value == "None" else False),
                Button(label="Главная", style=ButtonStyle.green, id="events_home")
            ])
            if options[0].value != "None":
                inter_select = await self.bot.wait_for("select_option", check=lambda i: i.user == user and i.component.id.startswith('events_edit-event'))
                event = events.find_one({ 'uid': f"{inter_select.values[0].split('-')[1]}" })
                name = event['name']
                date = event['date']
                description = event['description']
                eev = discord.Embed(color=0x2f3136)
                eev.set_footer(text=user.name, icon_url=user.avatar_url)
                eev.timestamp = datetime.datetime.utcnow()
                channel_link = event['channel_link'] if event['channel_link'] == "Не указан" else f'[Кликни!]({event["channel_link"]})'
                eev.set_author(name="МУИ-Live - редактирование ивента - предпросмотр")
                eev.title = f"{name} | Genshin Impact [RU COM] - Ивенты"
                eev.description = f"""Время ивента: {date}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {description}"""
                if event['image'] != "":
                    eev.set_image(url=event['image'])
                await inter_select.respond(type=7, embed=eev, components=[
                    [
                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                    ],
                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                ])
                return_back = True
                while return_back:
                    inter_edit = await self.bot.wait_for("button_click", check=lambda i: i.user == user and i.component.id.startswith('events_edit-event'))
                    print(inter_edit)
                    if inter_edit.component.id == "events_edit-events":
                        return_back = False
                        return
                    else:
                        await inter_edit.respond(type=7, embed=eev, components=[])
                        type_edit = inter_edit.component.id.split('|')[1].split('.')[0]
                        uid = inter_edit.component.id.split('|')[1].split('.')[1]
                        if type_edit == "name":
                            e = discord.Embed(color=0x2f3136)
                            e.set_footer(text=user.name, icon_url=user.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.description = "Введите новое название. (для отмены действия напишите `отмена`)"
                            msg = await inter_edit.message.channel.send(embed=e)
                            message = await self.bot.wait_for("message", check=lambda m: m.author.id == inter_edit.user.id and m.channel == inter_edit.message.channel)
                            name = message.content.replace("\n", "")
                            if message.content.lower() == "отмена":
                                e.description = "Действие отменено."
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                await message.delete()
                                await msg.edit(embed=e, delete_after=5.0)
                            else:
                                eev.title = f"{name} | Genshin Impact [RU COM] - Ивенты"
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                events.update_one({ 'uid': f'{uid}' }, { "$set": { 'name': name } })
                                e.description = "Новое название установлено."
                                await msg.edit(embed=e, delete_after=5.0)
                        elif type_edit == "date":
                            e = discord.Embed(color=0x2f3136)
                            e.set_footer(text=user.name, icon_url=user.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.description = "Введите новую дату. (для отмены действия напишите `отмена`)"
                            msg = await inter_edit.message.channel.send(embed=e)
                            message = await self.bot.wait_for("message", check=lambda m: m.author.id == inter_edit.user.id and m.channel == inter_edit.message.channel)
                            date = message.content.replace("\n", "")
                            if message.content.lower() == "отмена":
                                e.description = "Действие отменено."
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                await message.delete()
                                await msg.edit(embed=e, delete_after=5.0)
                            else:
                                eev.description = f"""Время ивента: {date}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {description}"""
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                events.update_one({ 'uid': f'{uid}' }, { "$set": { 'date': date } })
                                e.description = "Новая дата установлена."
                                await msg.edit(embed=e, delete_after=5.0)
                        elif type_edit == "channel":
                            e = discord.Embed(color=0x2f3136)
                            e.set_footer(text=user.name, icon_url=user.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.description = "Введите новую ссылку на канал. Для создания нового напишите `create`. (для отмены действия напишите `отмена`)"
                            msg = await inter_edit.message.channel.send(embed=e)
                            message = await self.bot.wait_for("message", check=lambda m: m.author.id == inter_edit.user.id and m.channel == inter_edit.message.channel and (is_url(m.content) or m.content.lower() == "create" or m.content.lower() == 'отмена'))
                            if message.content.lower() == "отмена":
                                e.description = "Действие отменено."
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                await message.delete()
                                await msg.edit(embed=e, delete_after=5.0)
                            else:
                                if message.content.lower() != "create":
                                    channel_link2 = message.content
                                    channel_link = channel_link2 if channel_link2 == "Не указан" else f'[Кликни!]({channel_link2})'
                                    eev.description = f"""Время ивента: {date}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {description}"""
                                else:
                                    adv = message.guild.get_role(767012156557623356)
                                    evm = message.guild.get_role(873997911111917598)
                                    overwrites = {
                                        user: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True, manage_channels=True, manage_permissions=True, move_members=True, mute_members=True, deafen_members=True),
                                        adv: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
                                        evm: discord.PermissionOverwrite(manage_channels=True)
                                    }
                                    channel_created = await message.guild.create_voice_channel(name=f"{user.name}' event", category=message_inter.guild.get_channel(892292747816476732), overwrites=overwrites)
                                    invite = await channel_created.create_invite()
                                    url = invite.url
                                    channel_link2 = url
                                    channel_link = channel_link2 if channel_link2 == "Не указан" else f'[Кликни!]({channel_link2})'
                                    eev.description = f"""Время ивента: {date}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {description}"""
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                events.update_one({ 'uid': f'{uid}' }, { "$set": { 'channel_link': channel_link2 } })
                                e.description = "Новая ссылка установлена."
                                await msg.edit(embed=e, delete_after=5.0)
                        elif type_edit == "description":
                            e = discord.Embed(color=0x2f3136)
                            e.set_footer(text=user.name, icon_url=user.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.description = "Введите новое описание. (для отмены действия напишите `отмена`)"
                            msg = await inter_edit.message.channel.send(embed=e)
                            message = await self.bot.wait_for("message", check=lambda m: m.author.id == inter_edit.user.id and m.channel == inter_edit.message.channel)
                            description = message.content
                            if message.content.lower() == "отмена":
                                e.description = "Действие отменено."
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                await message.delete()
                                await msg.edit(embed=e, delete_after=5.0)
                            else:
                                eev.description = f"""Время ивента: {date}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {description}"""
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                events.update_one({ 'uid': f'{uid}' }, { "$set": { 'description': description } })
                                e.description = "Новое описание установлено."
                                await msg.edit(embed=e, delete_after=5.0)
                        elif type_edit == "image":
                            e = discord.Embed(color=0x2f3136)
                            e.set_footer(text=user.name, icon_url=user.avatar_url)
                            e.timestamp = datetime.datetime.utcnow()
                            e.description = "Укажите ссылку на новую картинку. (для отмены действия напишите `отмена`)"
                            msg = await inter_edit.message.channel.send(embed=e)
                            def check_(m):
                                return m.author.id == user.id and m.channel == message_inter.channel and (is_url(m.content) or m.content == "отмена")
                            
                            message = await self.bot.wait_for("message", check=check_)
                            image = message.content
                            if message.content.lower() == "отмена":
                                e.description = "Действие отменено."
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                await message.delete()
                                await msg.edit(embed=e, delete_after=5.0)
                            else:
                                eev.set_image(url=image)
                                await message_inter.edit(embed=e)
                                events.update_one({ 'uid': uid }, { "$set": { "image": image } })
                                await msg.delete()
                                await inter_edit.message.edit(embed=eev, components=[
                                    [
                                        Button(label="Название", style=ButtonStyle.green, id=f"events_edit-event|name.{event['uid']}"),
                                        Button(label="Дата", style=ButtonStyle.green, id=f"events_edit-event|date.{event['uid']}"),
                                        Button(label="Канал", style=ButtonStyle.green, id=f"events_edit-event|channel.{event['uid']}"),
                                        Button(label="Описание", style=ButtonStyle.green, id=f"events_edit-event|description.{event['uid']}"),
                                        Button(label="Картинка", style=ButtonStyle.green, id=f"events_edit-event|image.{event['uid']}")
                                    ],
                                    Button(label="Вернуться", style=ButtonStyle.green, id=f"events_edit-events")
                                ])
                                e.description = "Новая картинка установлена."
                                await msg.edit(embed=e, delete_after=5.0)


                

        elif inter.component.id == "events_choose-events":
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=user.name, icon_url=user.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.title = "МУИ"
            e.description = """Выберете ивент, который хотите опубликовать."""
            events_list = list(events.find({}))
            options = []
            for event in events_list:
                member = inter.message.guild.get_member(int(event['created_by']))
                options.append(SelectOption(label=f"{event['name']}", value=f"events_choose-{event['uid']}", description=f'Created by: {member}'))
            if options == []:
                options.append(SelectOption(label="Увы, ивентов не найдено.", value='None', default=True))
            await inter.respond(type=7, embed=e, components=[
                Select(options=options, id="events_choose-event", placeholder='Список ивентов', disabled=True if options[0].value == "None" else False),
                Button(label="Главная", style=ButtonStyle.green, id="events_home")
            ])
            if options[0].value != "None":
                inter_select = await self.bot.wait_for("select_option", check=lambda i: i.user == user and i.component.id.startswith('events_choose-event'))
                event = events.find_one({ 'uid': f"{inter_select.values[0].split('-')[1]}" })
                eev = discord.Embed(color=0x2f3136)
                eev.set_footer(text=user.name, icon_url=user.avatar_url)
                eev.timestamp = datetime.datetime.utcnow()
                channel_link = event['channel_link'] if event['channel_link'] == "Не указан" else f'[Кликни!]({event["channel_link"]})'
                eev.set_author(name="МУИ-Live - публикация ивента - предпросмотр")
                eev.title = f"{event['name']} | Genshin Impact [RU COM] - Ивенты"
                eev.description = f"""Время ивента: {event['date']}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {event['description']}"""
                if event['image'] != "":
                    eev.set_image(url=event['image'])
                yes_emoji = self.bot.get_emoji(879083428836933712)
                no_emoji = self.bot.get_emoji(879083439742152744)
                await inter_select.respond(type=7, embed=eev, components=[
                    [
                        Button(emoji=yes_emoji, id='events_choose-event-yes', style=ButtonStyle.green),
                        Button(emoji=no_emoji, id='events_choose-event-no', style=ButtonStyle.red)
                    ]
                ])
                inter_yor = await self.bot.wait_for("button_click", check=lambda i: i.user == user and i.component.id.startswith('events_choose-event'))
                if inter_yor.component.id.split("-")[2] == "yes":
                    channel_events = inter.message.guild.get_channel(874017088623218768)
                    eev = discord.Embed(color=0x2f3136)
                    eev.set_footer(text=user.name, icon_url=user.avatar_url)
                    eev.timestamp = datetime.datetime.utcnow()
                    channel_link = event['channel_link'] if event['channel_link'] == "Не указан" else f'[Кликни!]({event["channel_link"]})'
                    eev.title = f"{event['name']} | Genshin Impact [RU COM] - Ивенты"
                    eev.description = f"""Время ивента: {event['date']}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {event['description']}"""
                    if event['image'] != "":
                        eev.set_image(url=event['image'])
                    await channel_events.send(content='<@&928018145988472893>', embed=eev)
                    e_yes = discord.Embed(color=0x2f3136)
                    e_yes.set_footer(text=user.name, icon_url=user.avatar_url)
                    e_yes.timestamp = datetime.datetime.utcnow()
                    e_yes.set_author(name="МУИ")
                    e_yes.description = "Ивент был опубликован."
                    await inter_yor.respond(type=7, embed=e_yes, components=[
                        Button(label="Вернуться", style=ButtonStyle.green, id="events_choose-events")
                    ])
                else:
                    e_yes = discord.Embed(color=0x2f3136)
                    e_yes.set_footer(text=user.name, icon_url=user.avatar_url)
                    e_yes.timestamp = datetime.datetime.utcnow()
                    e_yes.set_author(name="МУИ")
                    e_yes.description = "Ивент не был опубликован."
                    await inter_yor.respond(type=7, embed=e_yes, components=[
                        Button(label="Вернуться", style=ButtonStyle.green, id="events_choose-events")
                    ])

        elif inter.component.id == "events_delete-events":
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=user.name, icon_url=user.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.title = "МУИ"
            e.description = """Выберете ивент, который хотите удалить."""
            events_list = list(events.find({}))
            options = []
            for event in events_list:
                member = inter.message.guild.get_member(int(event['created_by']))
                options.append(SelectOption(label=f"{event['name']}", value=f"events_delete-{event['uid']}", description=f'Created by: {member}'))
            if options == []:
                options.append(SelectOption(label="Увы, ивентов не найдено.", value='None', default=True))
            await inter.respond(type=7, embed=e, components=[
                Select(options=options, id="events_delete-event", placeholder='Список ивентов', disabled=True if options[0].value == "None" else False),
                Button(label="Главная", style=ButtonStyle.green, id="events_home")
            ])
            if options[0].value != "None":
                inter_select = await self.bot.wait_for("select_option", check=lambda i: i.user == user and i.component.id.startswith('events_delete-event'))
                event = events.find_one({ 'uid': f"{inter_select.values[0].split('-')[1]}" })
                eev = discord.Embed(color=0x2f3136)
                eev.set_footer(text=user.name, icon_url=user.avatar_url)
                eev.timestamp = datetime.datetime.utcnow()
                channel_link = event['channel_link'] if event['channel_link'] == "Не указан" else f'[Кликни!]({event["channel_link"]})'
                eev.set_author(name="МУИ-Live - удаление ивента - предпросмотр")
                eev.title = f"{event['name']} | Genshin Impact [RU COM] - Ивенты"
                eev.description = f"""Время ивента: {event['date']}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {event['description']}"""
                if event['image'] != "":
                    eev.set_image(url=event['image'])
                yes_emoji = self.bot.get_emoji(879083428836933712)
                no_emoji = self.bot.get_emoji(879083439742152744)
                await inter_select.respond(type=7, embed=eev, components=[
                    [
                        Button(emoji=yes_emoji, id='events_delete-event-yes', style=ButtonStyle.green),
                        Button(emoji=no_emoji, id='events_delete-event-no', style=ButtonStyle.red)
                    ]
                ])
                inter_yor = await self.bot.wait_for("button_click", check=lambda i: i.user == user and i.component.id.startswith('events_delete-event'))
                if inter_yor.component.id.split("-")[2] == "yes":
                    events.delete_one({ 'uid': f'{inter_select.values[0].split("-")[1]}' })
                    e_yes = discord.Embed(color=0x2f3136)
                    e_yes.set_footer(text=user.name, icon_url=user.avatar_url)
                    e_yes.timestamp = datetime.datetime.utcnow()
                    e_yes.set_author(name="МУИ")
                    e_yes.description = "Ивент был удалён."
                    await inter_yor.respond(type=7, embed=e_yes, components=[
                        Button(label="Вернуться", style=ButtonStyle.green, id="events_delete-events")
                    ])
                else:
                    e_yes = discord.Embed(color=0x2f3136)
                    e_yes.set_footer(text=user.name, icon_url=user.avatar_url)
                    e_yes.timestamp = datetime.datetime.utcnow()
                    e_yes.set_author(name="МУИ")
                    e_yes.description = "Ивент не был удалён."
                    await inter_yor.respond(type=7, embed=e_yes, components=[
                        Button(label="Вернуться", style=ButtonStyle.green, id="events_delete-events")
                    ])


        elif inter.component.id == "events_create-new-events":
            def check(m):
                return m.author.id == user.id and m.channel == message_inter.channel

            uid = create_uid()

            name = "Без названия"
            date = "Не указано"
            channel_link = "Не указан"
            description = "Не указано"
            image = ""

            events.insert_one({ "uid": uid, "created_by": f'{user.id}', 'name': name, 'date': date, 'channel_link': channel_link, "description": description, "image": image })

            e_err = discord.Embed(color=0x2f3136)
            e_err.set_footer(text=user.name, icon_url=user.avatar_url)
            e_err.timestamp = datetime.datetime.utcnow()
            e_err.description = "Время для ответа вышло, но новый ивент был сохранён."
            e = discord.Embed(color=0x2f3136)
            e.set_footer(text=user.name, icon_url=user.avatar_url)
            e.timestamp = datetime.datetime.utcnow()
            e.set_author(name="МУИ-Live - создание ивента - предпросмотр")
            e.title = f"{name} | Genshin Impact [RU COM] - Ивенты"
            e.description = f"""Время ивента: {date}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {description}"""
            await message_inter.edit(embed=e, components=[])
            e_name = discord.Embed(color=0x2f3136)
            e_name.set_footer(text=user.name, icon_url=user.avatar_url)
            e_name.timestamp = datetime.datetime.utcnow()
            e_name.description = "Напишите название ивента. Для пропуска этого этапа напишите `skip`"
            msg = await message_inter.channel.send(embed=e_name)
            try:
                message = await self.bot.wait_for("message", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                await message_inter.edit(embed=e_err, components=[])
                await msg.delete()
            else:
                name = message.content.replace("\n", "")
                if name != "skip":
                    e.title = f"{name} | Genshin Impact [RU COM] - Ивенты"
                    await message_inter.edit(embed=e)
                    events.update_one({ 'uid': uid }, { "$set": { "name": name } })
                await msg.delete()
                e_date = discord.Embed(color=0x2f3136)
                e_date.set_footer(text=user.name, icon_url=user.avatar_url)
                e_date.timestamp = datetime.datetime.utcnow()
                e_date.description = "Напишите дату ивента. Для пропуска этого этапа напишите `skip`"
                msg = await message_inter.channel.send(embed=e_date)
                try:
                    message = await self.bot.wait_for("message", check=check, timeout=120.0)
                except asyncio.TimeoutError:
                    await message_inter.edit(embed=e_err, components=[])
                    await msg.delete()
                else:
                    date = message.content.replace("\n", "")
                    if date != "skip":
                        e.description = f"""Время ивента: {date}
Канал ивента: {channel_link}
Ведущий: {user.mention}
Описание: {description}"""
                        await message_inter.edit(embed=e)
                        events.update_one({ 'uid': uid }, { "$set": { "date": date } })
                    await msg.delete()
                    e_channel = discord.Embed(color=0x2f3136)
                    e_channel.set_footer(text=user.name, icon_url=user.avatar_url)
                    e_channel.timestamp = datetime.datetime.utcnow()
                    e_channel.description = "Напишите ссылку на канал ивента (для создания канала напишите `create`). Для пропуска этого этапа напишите `skip`."
                    msg = await message_inter.channel.send(embed=e_channel)
                    try:
                        def check_(m):
                            return m.author.id == user.id and m.channel == message_inter.channel and (is_url(m.content) or m.content == "skip" or m.content == "create")
                        message = await self.bot.wait_for("message", check=check_, timeout=120.0)
                    except asyncio.TimeoutError:
                        await message_inter.edit(embed=e_err, components=[])
                        await msg.delete()
                    else:
                        channel_link = message.content
                        if channel_link != "skip" and channel_link != "create":
                            e.description = f"""Время ивента: {date}
Канал ивента: [Кликни!]({channel_link})
Ведущий: {user.mention}
Описание: {description}"""
                            await message_inter.edit(embed=e)
                            events.update_one({ 'uid': uid }, { "$set": { "channel_link": channel_link } })
                        elif channel_link == "create":
                            adv = message_inter.guild.get_role(767012156557623356)
                            overwrites = {
                                user: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True, manage_channels=True, manage_permissions=True, move_members=True, mute_members=True, deafen_members=True),
                                adv: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True)
                            }
                            channel_created = await message_inter.guild.create_voice_channel(name=f"{user.name}' event", category=message_inter.guild.get_channel(892292747816476732), overwrites=overwrites)
                            invite = await channel_created.create_invite()
                            url = invite.url
                            channel_link = url
                            e.description = f"""Время ивента: {date}
Канал ивента: [Кликни!]({channel_link})
Ведущий: {user.mention}
Описание: {description}"""
                            await message_inter.edit(embed=e)
                            events.update_one({ 'uid': uid }, { "$set": { "channel_link": channel_link } })
                        await msg.delete()
                        e_image = discord.Embed(color=0x2f3136)
                        e_image.set_footer(text=user.name, icon_url=user.avatar_url)
                        e_image.timestamp = datetime.datetime.utcnow()
                        e_image.description = "Напишите ссылку на картинку ивента. Для пропуска этого этапа напишите `skip`."
                        msg = await message_inter.channel.send(embed=e_image)
                        try:
                            def check_(m):
                                return m.author.id == user.id and m.channel == message_inter.channel and (is_url(m.content) or m.content == "skip")
                            message = await self.bot.wait_for("message", check=check_, timeout=120.0)
                        except asyncio.TimeoutError:
                            await message_inter.edit(embed=e_err, components=[])
                            await msg.delete()
                        else:
                            image = message.content
                            if image != "skip":
                                e.set_image(url=image)
                                await message_inter.edit(embed=e)
                                events.update_one({ 'uid': uid }, { "$set": { "image": image } })
                            await msg.delete()
                            e_description = discord.Embed(color=0x2f3136)
                            e_description.set_footer(text=user.name, icon_url=user.avatar_url)
                            e_description.timestamp = datetime.datetime.utcnow()
                            e_description.description = "Напишите описание. Для пропуска этого этапа напишите `skip`."
                            msg = await message_inter.channel.send(embed=e_description)
                            try:
                                message = await self.bot.wait_for("message", check=check, timeout=600.0)
                            except asyncio.TimeoutError:
                                await message_inter.edit(embed=e_err, components=[])
                                await msg.delete()
                            else:
                                description = message.content
                                if description != "skip":
                                    channel_link2 = channel_link if channel_link == "Не указан" else f'[Кликни!]({channel_link})'
                                    e.description = f"""Время ивента: {date}
Канал ивента: {channel_link2}
Ведущий: {user.mention}
Описание: {description}"""
                                    await message_inter.edit(embed=e)
                                    events.update_one({ 'uid': uid }, { "$set": { "description": description } })
                                await msg.delete()
                                e_success = discord.Embed(color=0x2f3136)
                                e_success.set_footer(text=user.name, icon_url=user.avatar_url)
                                e_success.timestamp = datetime.datetime.utcnow()
                                e_success.description = "Создание ивента завершено."
                                await message_inter.channel.send(embed=e_success, delete_after=10.0)
                                await inter.respond(type=7, embed=e, components=[
                                    Button(label="Главная", style=ButtonStyle.green, id="events_home")
                                ])

        
    @commands.command()
    @commands.check_any(commands.has_any_role(768141743942008882, 873997911111917598), commands.has_permissions(administrator=True))
    async def aevent(self, ctx):
        e = discord.Embed(color=0x2f3136)
        e.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        e.title = "МУИ"
        e.description = """**Добро пожаловать в МУИ (Мастер Управления Ивентами).
        

Выберете действие для продолжения:
1. Создание нового ивента
2. Удаление ивентов
3. Выбор существующего ивента
4. Изменение существующего ивента**"""
        await ctx.send(embed=e, components=[
            Button(label="Создание нового ивента", style=ButtonStyle.green, id="events_create-new-events"),
            Button(label="Удаление ивентов", style=ButtonStyle.red, id="events_delete-events"),
            Button(label="Выбор существующего ивента", style=ButtonStyle.blue, id="events_choose-events"),
            Button(label="Изменение существующего ивента", style=ButtonStyle.gray, id="events_edit-events")
        ])
        
        
        

def setup(bot):
    bot.add_cog(Events(bot))
        
        