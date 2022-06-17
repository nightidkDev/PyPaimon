from sqlite3.dbapi2 import connect
import discord
from discord.ext import commands
from discord_components import *
import datetime
import asyncio
import time
import random
import os
import re
import sys
sys.path.append("../../")
import config

# DataBase
import pymongo
login_url = config.uri
login_url2 = config.uri2
mongoclient = pymongo.MongoClient(login_url)
mongoclient2 = pymongo.MongoClient(login_url2)
db = mongoclient.aimi
db2 = mongoclient2.aimi
users = db.prof_ec_users
shop = db.shop
shop2 = db2.shop
reactions = db2.reactions
bgs = db.backgrounds
shops = db.shops_list
roles_wishes = db2.roles_wishes
special_role = db2.special_wishes
chats_wishes = db2.chats_wishes
voices_wishes = db2.voices_wishes
extended_sub = db2.extended_sub
banners_wishes = db2.banners_wishes
packs_wishes = db2.packs_wishes


def checkbuy_c(custom, cost, money_emoji, user, role_id=None):
    items = list(user["inv"])
    items2 = list(filter(lambda x: x["type"] == "background", items))
    items3 = list(map(lambda x: list(x.items())[1][1], items2))
    if role_id is not None:
        items4 = list(filter(lambda x: x["type"] == "waifu", items))
        items5 = list(map(lambda x: list(x.items())[1][1], items4))
        if role_id not in items5:
            return ["Заблокировано", False]
        elif custom in items3:
            return ["Куплено!", True]
        else:
            return [f"{cost}{money_emoji}", None]
    else:
        if custom in items3:
            return ["Куплено!", True]
        else:
            return [f"{cost}{money_emoji}", None]

def checkbuy_r(role, cost, money_emoji, user):
    items = list(user["inv"])
    items = list(filter(lambda x: x["type"] == "role", items))
    items = list(map(lambda x: list(x.items())[1][1], items))
    if role in items:
        return "Куплено!"
    else:
        return f"{cost}{money_emoji}"

def check_extended_sub(user):
    is_subbed = extended_sub.find_one({ 'id': f"{user.id}" })
    if is_subbed is None:
        return False
    else:
        return True

def checkbuy_r_tf(role, user):
    items = list(user["inv"])
    items = list(filter(lambda x: x["type"] == "role", items))
    items = list(map(lambda x: list(x.items())[1][1], items))
    if role in items:
        return True
    else:
        return False

def seconds_to_hh_mm_ss(seconds):
    return datetime.datetime.utcfromtimestamp(seconds + 10800).strftime("%d.%m.%Y")

def func_chunk(lst, n):
    for x in range(0, len(lst), n):
        e_c = lst[x : n + x]
        yield e_c

def check_history(user, user_db, wish_type, wish):
    history_wishes = user_db["wishes"][wish_type]["history"]
    if len(history_wishes) + 1 >= 60:
        while len(history_wishes) != 59:
            history_wishes.pop(0)
        history_wishes.append(wish)
        users.update_one({ "disid": f"{user.id}", "guild": f"{user.guild.id}" }, { "$set": { f"wishes.{wish_type}.history": history_wishes } })
    else:
        users.update_one({ "disid": f"{user.id}", "guild": f"{user.guild.id}" }, { "$push": { f"wishes.{wish_type}.history": wish } })

def check_procent_wishes(member, user, wish, count, second=False):

    legendary_wish = False
    epic_wish = False

    chances_legendary = config.chances_legendary
    chances_epic = config.chances_epic

    if wish == "IacquaintFate":
        legendary = config.legendary_banner_1
        epic = config.epic_banner_1
    elif wish == "IntertwinedFate":
        if not second:
            legendary = config.legendary_banner_2
        else:
            legendary = config.legendary_banner_2_2
        epic = config.event_epic # config.epic_banner_1 +
    elif wish == "ServerFate":
        role_staff = member.guild.get_role(761771540181942273)
        if role_staff in member.roles:
            legendary = config.legendary_banner_3[:-1]
        else:
            legendary = config.legendary_banner_3
        epic = config.epic_banner_3

    fifty_fifty = config.fifty_fifty
    default_items = config.default_banner

    fifty_fifty_lose = None

    if count == 1:
        chance = user["wishes"][wish]["count_wishes_warranty_legendary"]
        chance_epic = user["wishes"][wish]["count_wishes_warranty_epic"]
        if chance + 1 == 90:
            legendary_wish = True
            if wish == "IntertwinedFate":
                if user["wishes"][wish]["fifty_fifty"] == 0:
                    legendary_item = random.choice(legendary)
                    fifty_fifty_lose = False
                else:
                    legendary_item = random.choice(legendary + fifty_fifty)
                    if legendary_item in fifty_fifty:
                        fifty_fifty_lose = True
                    else:
                        fifty_fifty_lose = False
            else:
                legendary_item = random.choice(legendary)
                fifty_fifty_lose = None

        else:
            number_wish = random.uniform(0.0, 100.0)
            legendary_wish = True if number_wish < chances_legendary[chance] else False
            if legendary_wish is True:
                if wish == "IntertwinedFate":
                    if user["wishes"][wish]["fifty_fifty"] == 0:
                        legendary_item = random.choice(legendary)
                        fifty_fifty_lose = False
                    else:
                        legendary_item = random.choice(legendary + fifty_fifty)
                        if legendary_item in fifty_fifty:
                            fifty_fifty_lose = True
                        else:
                            fifty_fifty_lose = False
                else:
                    legendary_item = random.choice(legendary)
        if legendary_wish is False and chance_epic + 1 >= 10:
            epic_wish = True
            number_wish_epic = 100
            epic_item = random.choice(epic)
        elif legendary_wish is False:
            number_wish_epic = random.uniform(0.0, 100.0)
            epic_wish = True if number_wish_epic < chances_epic[chance_epic] else False
            if epic_wish is True:
                epic_item = random.choice(epic)

        type_item = "legendary" if legendary_wish is True else "epic" if epic_wish is True else "default"
        if type_item == "default":
            item = random.choice(default_items)
        elif type_item == "epic":
            item = epic_item
        else:
            item = legendary_item


        return [type_item, item, fifty_fifty_lose]


def check_name_bgd(name):
    if name == "battlepass":
        return "Боевой пропуск"
    elif name == "achievements":
        return "Достижения"
    elif name == "another":
        return "Другое"
    elif name == "rep":
        return "Репутация"
    elif name == "events":
        return "Ивенты"
    elif name == "characters":
        return "Персонажи"
    elif name == "sevents":
        return "Серверная кастомизация"

def check_type_item(value):
    if value == "characters":
        return "Персонаж"
    elif value == "primogems":
        return "Примогемы"
    elif value == "level":
        return "Опыт"
    elif value == "null":
        return "/del"
    elif value == "wishes_primogems":
        return "Примогемы"
    elif value == "wishes_chat":
        return "Личный чат"
    elif value == "wishes_voice":
        return "Личный войс"
    elif value == "wishes_wish":
        return "Молитвы"
    elif value == "wishes_role":
        return "Личная роль"
    elif value == "wishes_special":
        return "Особая роль"
    else:
        return "Неизвестно"

def check_rare_item(value):
    if value == "legendary":
        return " (5★)"
    elif value == "epic":
        return " (4★)"
    else:
        return ""

class Buttons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        #print(interaction.raw_data)
        if interaction.responded:
            print("responded")
        if interaction.component.id.startswith('music'):
            return
        if interaction.component.id.startswith('events'):
            return
        if interaction.component.id.startswith('support'):
            return
        if interaction.component.id.startswith('reaction'):
            return
        if reactions.count({ "message_id": str(interaction.message.id) }) == 0:
            e = discord.Embed(title='', description='Данная реакция больше не действительна.', color = 0xff0000)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar_url)
            return await interaction.respond(embed=e)
        react = reactions.find_one({ "message_id": str(interaction.message.id) })
        if react["user_id"] != str(interaction.user.id):
            e = discord.Embed(title='', description='Данная реакция не принадлежит вам.', color = 0x2f3136)
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar_url)
            return await interaction.respond(embed=e)
        member = interaction.message.guild.get_member(int(react["user_id"]))
        message = interaction.message
        reactions.update_one({ "message_id": f"{message.id}" }, { "$set": { "time": int(time.time() + 20) } })
        user = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
        if react["type"] == "banners":
            if interaction.component.id == "banners_home":
                e = discord.Embed(color=0x2f3136)
                IacquaintFate_emoji = self.bot.get_emoji(772748673251016745)
                IntertwinedFate_emoji = self.bot.get_emoji(772748672999620629)
                e.description = f"""
{IacquaintFate_emoji} Молитва «Жажда странствий»
{IntertwinedFate_emoji} (I) Молитва «{config.banner_2_name}» {'- **завершён**' if config.banner_2_closed else ''}
{IntertwinedFate_emoji} (II) Молитва «{config.banner_2_2_name}» {'- **завершён**' if config.banner_2_2_closed else ''}
{IacquaintFate_emoji} Молитва «Благословение сервера» {'- **временно завершён**' if config.banner_3_closed else ''}
"""
                e.set_author(name="Баннеры")
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                msg = await interaction.respond(type=7, embed=e, components=[
                    [
                        Button(emoji=IacquaintFate_emoji, id="banner_1"),
                        Button(label="(I)", emoji=IntertwinedFate_emoji, id="banner_2", disabled=config.banner_2_closed),
                        Button(label="(II)", emoji=IntertwinedFate_emoji, id="banner_2_2", disabled=config.banner_2_2_closed),
                        Button(emoji=IacquaintFate_emoji, id="banner_3", disabled=config.banner_3_closed)
                    ]
                ])
            elif interaction.component.id.startswith("history_banner_1"):
                interList = interaction.component.id.split("_")
                if len(interList) <= 3:
                    history_banner_1 = user['wishes']['IacquaintFate']['history']
                    history_banner_1.reverse()
                    history_chunk = list(func_chunk(history_banner_1, 6))
                    e = discord.Embed(color=0x2f3136)
                    e.title = "История баннера «Жажда странствий»"
                    if len(history_banner_1) <= 0:
                        e.description = "Здесь ничего нет."
                    else:
                        e.description = f'Страница 1/{len(history_chunk)}'
                        for a in range(len(history_chunk[0])):
                            item = history_chunk[0][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    if len(history_chunk) > 1:
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(emoji=nextpageemoji, id=f"history_banner_1_nextpage_2")
                            ],
                            [
                                Button(emoji="🏠", id='banner_1', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(emoji="🏠", id='banner_1', style=ButtonStyle.gray)
                            ]
                        ])
                else:
                    if interList[3] == "nextpage":
                        page = int(interList[4])
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        history_banner_1 = user['wishes']['IacquaintFate']['history']
                        history_banner_1.reverse()
                        history_chunk = list(func_chunk(history_banner_1, 6))
                        e = discord.Embed(color=0x2f3136)
                        e.title = "История баннера «Жажда странствий»"
                        e.description = f'Страница {page}/{len(history_chunk)}'
                        for a in range(len(history_chunk[page-1])):
                            item = history_chunk[page-1][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                        e.set_footer(text=member.name, icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        if page + 1 > len(history_chunk):
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_1_backpage_{page - 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_1', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_1_backpage_{page - 1}"),
                                    Button(emoji=nextpageemoji, id=f"history_banner_1_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_1', style=ButtonStyle.gray)
                                ]
                            ])
                    elif interList[3] == "backpage":
                        page = int(interList[4])
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        history_banner_1 = user['wishes']['IacquaintFate']['history']
                        history_banner_1.reverse()
                        history_chunk = list(func_chunk(history_banner_1, 6))
                        e = discord.Embed(color=0x2f3136)
                        e.title = "История баннера «Жажда странствий»"
                        e.description = f'Страница {page}/{len(history_chunk)}'
                        for a in range(len(history_chunk[page-1])):
                            item = history_chunk[page-1][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                        e.set_footer(text=member.name, icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        if page - 1 == 0:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=nextpageemoji, id=f"history_banner_1_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_1', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_1_backpage_{page - 1}"),
                                    Button(emoji=nextpageemoji, id=f"history_banner_1_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_1', style=ButtonStyle.gray)
                                ]
                            ])
            elif interaction.component.id.startswith("history_banner_2") and '-2' not in interaction.component.id:
                interList = interaction.component.id.split("_")
                if len(interList) <= 3:
                    history_banner_2 = user['wishes']['IntertwinedFate']['history']
                    history_banner_2.reverse()
                    history_chunk = list(func_chunk(history_banner_2, 6))
                    e = discord.Embed(color=0x2f3136)
                    e.title = f"История баннера «{config.banner_2_name}»"
                    if len(history_banner_2) <= 0:
                        e.description = "Здесь ничего нет."
                    else:
                        e.description = f'Страница 1/{len(history_chunk)}'
                        for a in range(len(history_chunk[0])):
                            item = history_chunk[0][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    if len(history_chunk) > 1:
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(emoji=nextpageemoji, id=f"history_banner_2_nextpage_2")
                            ],
                            [
                                Button(emoji="🏠", id='banner_2', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(emoji="🏠", id='banner_2', style=ButtonStyle.gray)
                            ]
                        ])
                else:
                    if interList[3] == "nextpage":
                        page = int(interList[4])
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        history_banner_2 = user['wishes']['IntertwinedFate']['history']
                        history_banner_2.reverse()
                        history_chunk = list(func_chunk(history_banner_2, 6))
                        e = discord.Embed(color=0x2f3136)
                        e.title = f"История баннера «{config.banner_2_name}»"
                        e.description = f'Страница {page}/{len(history_chunk)}'
                        for a in range(len(history_chunk[page-1])):
                            item = history_chunk[page-1][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                        e.set_footer(text=member.name, icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        if page + 1 > len(history_chunk):
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_2_backpage_{page - 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_2', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_2_backpage_{page - 1}"),
                                    Button(emoji=nextpageemoji, id=f"history_banner_2_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_2', style=ButtonStyle.gray)
                                ]
                            ])
                    elif interList[3] == "backpage":
                        page = int(interList[4])
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        history_banner_2 = user['wishes']['IntertwinedFate']['history']
                        history_banner_2.reverse()
                        history_chunk = list(func_chunk(history_banner_2, 6))
                        e = discord.Embed(color=0x2f3136)
                        e.title = f"История баннера «{config.banner_2_name}»"
                        e.description = f'Страница {page}/{len(history_chunk)}'
                        for a in range(len(history_chunk[page-1])):
                            item = history_chunk[page-1][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                        e.set_footer(text=member.name, icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        if page - 1 == 0:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=nextpageemoji, id=f"history_banner_2_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_2', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_2_backpage_{page - 1}"),
                                    Button(emoji=nextpageemoji, id=f"history_banner_2_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_2', style=ButtonStyle.gray)
                                ]
                            ])
            elif interaction.component.id.startswith("history_banner_2-2"):
                interList = interaction.component.id.split("_")
                if len(interList) <= 3:
                    history_banner_2_2 = user['wishes']['IntertwinedFate']['history']
                    history_banner_2_2.reverse()
                    history_chunk = list(func_chunk(history_banner_2_2, 6))
                    e = discord.Embed(color=0x2f3136)
                    e.title = f"История баннера «{config.banner_2_2_name}»"
                    if len(history_banner_2_2) <= 0:
                        e.description = "Здесь ничего нет."
                    else:
                        e.description = f'Страница 1/{len(history_chunk)}'
                        for a in range(len(history_chunk[0])):
                            item = history_chunk[0][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    if len(history_chunk) > 1:
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(emoji=nextpageemoji, id=f"history_banner_2-2_nextpage_2")
                            ],
                            [
                                Button(emoji="🏠", id='banner_2_2', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(emoji="🏠", id='banner_2_2', style=ButtonStyle.gray)
                            ]
                        ])
                else:
                    if interList[3] == "nextpage":
                        page = int(interList[4])
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        history_banner_2_2 = user['wishes']['IntertwinedFate']['history']
                        history_banner_2_2.reverse()
                        history_chunk = list(func_chunk(history_banner_2_2, 6))
                        e = discord.Embed(color=0x2f3136)
                        e.title = f"История баннера «{config.banner_2_2_name}»"
                        e.description = f'Страница {page}/{len(history_chunk)}'
                        for a in range(len(history_chunk[page-1])):
                            item = history_chunk[page-1][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                        e.set_footer(text=member.name, icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        if page + 1 > len(history_chunk):
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_2-2_backpage_{page - 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_2_2', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_2-2_backpage_{page - 1}"),
                                    Button(emoji=nextpageemoji, id=f"history_banner_2-2_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_2_2', style=ButtonStyle.gray)
                                ]
                            ])
                    elif interList[3] == "backpage":
                        page = int(interList[4])
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        history_banner_2_2 = user['wishes']['IntertwinedFate']['history']
                        history_banner_2_2.reverse()
                        history_chunk = list(func_chunk(history_banner_2_2, 6))
                        e = discord.Embed(color=0x2f3136)
                        e.title = f"История баннера «{config.banner_2_2_name}»"
                        e.description = f'Страница {page}/{len(history_chunk)}'
                        for a in range(len(history_chunk[page-1])):
                            item = history_chunk[page-1][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                        e.set_footer(text=member.name, icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        if page - 1 == 0:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=nextpageemoji, id=f"history_banner_2-2_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_2_2', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_2-2_backpage_{page - 1}"),
                                    Button(emoji=nextpageemoji, id=f"history_banner_2-2_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_2_2', style=ButtonStyle.gray)
                                ]
                            ])
            elif interaction.component.id.startswith("history_banner_3"):
                interList = interaction.component.id.split("_")
                if len(interList) <= 3:
                    history_banner_3 = user['wishes']['ServerFate']['history']
                    history_banner_3.reverse()
                    history_chunk = list(func_chunk(history_banner_3, 6))
                    e = discord.Embed(color=0x2f3136)
                    e.title = "История баннера «Благословение сервера»"
                    if len(history_banner_3) <= 0:
                        e.description = "Здесь ничего нет."
                    else:
                        e.description = f'Страница 1/{len(history_chunk)}'
                        for a in range(len(history_chunk[0])):
                            item = history_chunk[0][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    if len(history_chunk) > 1:
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(emoji=nextpageemoji, id=f"history_banner_3_nextpage_2")
                            ],
                            [
                                Button(emoji="🏠", id='banner_3', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(emoji="🏠", id='banner_3', style=ButtonStyle.gray)
                            ]
                        ])
                else:
                    if interList[3] == "nextpage":
                        page = int(interList[4])
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        history_banner_3 = user['wishes']['ServerFate']['history']
                        history_banner_3.reverse()
                        history_chunk = list(func_chunk(history_banner_3, 6))
                        e = discord.Embed(color=0x2f3136)
                        e.title = "История баннера «Благословение сервера»"
                        e.description = f'Страница {page}/{len(history_chunk)}'
                        for a in range(len(history_chunk[page-1])):
                            item = history_chunk[page-1][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                        e.set_footer(text=member.name, icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        if page + 1 > len(history_chunk):
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_3_backpage_{page - 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_1', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_3_backpage_{page - 1}"),
                                    Button(emoji=nextpageemoji, id=f"history_banner_3_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="��", id='banner_3', style=ButtonStyle.gray)
                                ]
                            ])
                    elif interList[3] == "backpage":
                        page = int(interList[4])
                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        history_banner_3 = user['wishes']['ServerFate']['history']
                        history_banner_3.reverse()
                        history_chunk = list(func_chunk(history_banner_3, 6))
                        e = discord.Embed(color=0x2f3136)
                        e.title = "История баннера «Благословение сервера»"
                        e.description = f'Страница {page}/{len(history_chunk)}'
                        for a in range(len(history_chunk[page-1])):
                            item = history_chunk[page-1][a]
                            type_hitem = check_type_item(item["type"])
                            rare_hitem = check_rare_item(item["rare"])
                            e.add_field(name="```Тип```", value=f"```{type_hitem}```")
                            e.add_field(name="```Имя```", value=f"```{item['name']}{rare_hitem}```")
                            e.add_field(name="```Время молитвы```", value=f"```{datetime.datetime.utcfromtimestamp(int(item['date']) + 10800).strftime('%Y-%m-%d %H:%M:%S')}```")
                        e.set_footer(text=member.name, icon_url=member.avatar_url)
                        e.timestamp = datetime.datetime.utcnow()
                        if page - 1 == 0:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=nextpageemoji, id=f"history_banner_3_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_3', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=backpageemoji, id=f"history_banner_3_backpage_{page - 1}"),
                                    Button(emoji=nextpageemoji, id=f"history_banner_3_nextpage_{page + 1}")
                                ],
                                [
                                    Button(emoji="🏠", id='banner_3', style=ButtonStyle.gray)
                                ]
                            ])
            elif interaction.component.id == "banner_1":
                e = discord.Embed(color=0x2f3136)
                e.title = "`🧭          Молитва «Жажда странствий»            `"
                e.set_image(url=config.banner_1_image)
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                IacquaintFate_emoji = self.bot.get_emoji(772748673251016745)
                wishesCount = user["wishesCount"]["IacquaintFate"]
                #wishes_list = list(filter(lambda x: x["type"] == "wish" and x["name"] == "IacquaintFate", user['inv']))
                msg = await interaction.respond(type=7, embed=e, components=[
                    [
                        Button(emoji=IacquaintFate_emoji, label="x1",  id="banner_1_wish_x1", style=ButtonStyle.blue, disabled=True if wishesCount < 1 else False),
                        Button(emoji="⌛", id='history_banner_1', style=ButtonStyle.red),
                        Button(emoji="🏠", id='banners_home', style=ButtonStyle.gray)
                    ]
                ])
            elif interaction.component.id == "banner_2":
                e = discord.Embed(color=0x2f3136)
                e.title = f"`🧭               Молитва «{config.banner_2_name}»              `"
                e.set_image(url=config.banner_2_image)
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                IntertwinedFate_emoji = self.bot.get_emoji(772748672999620629)
                wishesCount = user["wishesCount"]["IntertwinedFate"]
                #wishes_list = list(filter(lambda x: x["type"] == "wish" and x["name"] == "IntertwinedFate", user['inv']))
                msg = await interaction.respond(type=7, embed=e, components=[
                    [
                        Button(emoji=IntertwinedFate_emoji, label="x1",  id="banner_2_wish_x1", style=ButtonStyle.blue, disabled=True if wishesCount < 1 else False),
                        Button(emoji="⌛", id='history_banner_2', style=ButtonStyle.red),
                        Button(emoji="🏠", id='banners_home', style=ButtonStyle.gray)
                    ]
                ])
            elif interaction.component.id == "banner_2_2":
                e = discord.Embed(color=0x2f3136)
                e.title = f"`🧭           Молитва «{config.banner_2_2_name}»          `"
                e.set_image(url=config.banner_2_2_image)
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                IntertwinedFate_emoji = self.bot.get_emoji(772748672999620629)
                wishesCount = user["wishesCount"]["IntertwinedFate"]
                #wishes_list = list(filter(lambda x: x["type"] == "wish" and x["name"] == "IntertwinedFate", user['inv']))
                msg = await interaction.respond(type=7, embed=e, components=[
                    [
                        Button(emoji=IntertwinedFate_emoji, label="x1",  id="banner_2_2_wish_x1", style=ButtonStyle.blue, disabled=True if wishesCount < 1 else False),
                        Button(emoji="⌛", id='history_banner_2-2', style=ButtonStyle.red),
                        Button(emoji="🏠", id='banners_home', style=ButtonStyle.gray)
                    ]
                ])
            elif interaction.component.id == "banner_3":
                e = discord.Embed(color=0x2f3136)
                e.title = "`🧭        Молитва «Благословение сервера»          `"
                e.set_image(url=config.banner_3_image)
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                IacquaintFate_emoji = self.bot.get_emoji(772748673251016745)
                wishesCount = user["wishesCount"]["IacquaintFate"]
                #wishes_list = list(filter(lambda x: x["type"] == "wish" and x["name"] == "IacquaintFate", user['inv']))
                msg = await interaction.respond(type=7, embed=e, components=[
                    [
                        Button(emoji=IacquaintFate_emoji, label="x1",  id="banner_3_wish_x1", style=ButtonStyle.blue, disabled=True if wishesCount < 1 else False),
                        Button(emoji="⌛", id='history_banner_3', style=ButtonStyle.red),
                        Button(emoji="🏠", id='banners_home', style=ButtonStyle.gray)
                    ]
                ])
            elif interaction.component.id.startswith("banner_1_"):
                if interaction.component.id == "banner_1_wish_x1":
                    #inv_user = user["inv"]
                    #items_wishes = {'type': 'wish', 'name': 'IacquaintFate'}
                    #inv_user.remove(items_wishes)
                    #users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IacquaintFate": -1 } })
                    type_item, item, fifty_fifty = check_procent_wishes(member, user, "IacquaintFate", 1)
                    if type_item == "legendary":
                        user_all = user["wishes"]["IacquaintFate"]["all_count_wishes"]
                        user_epic = user["wishes"]["IacquaintFate"]["count_wishes_warranty_epic"]
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$set": { "wishes.IacquaintFate.count_wishes_warranty_legendary": 0, "wishes.IacquaintFate.all_count_wishes": user_all + 1, "wishes.IacquaintFate.count_wishes_warranty_epic": user_epic + 1 } })
                    else:
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishes.IacquaintFate.count_wishes_warranty_legendary": 1, "wishes.IacquaintFate.all_count_wishes": 1, "wishes.IacquaintFate.count_wishes_warranty_epic": 1 } })
                    if type_item == "epic":
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$set": { "wishes.IacquaintFate.count_wishes_warranty_epic": 0 } })
                    e = discord.Embed(color=0x2f3136)
                    name_item = item[0]
                    id_item = item[2]
                    types_item = item[4]
                    descriptions_item = item[1].split("|")
                    description_item = descriptions_item[0]
                    if type_item == "legendary" or type_item == "epic":
                        subdescription_item = descriptions_item[1]
                    else:
                        description_item = random.choice(item[1].split("|"))
                    if type_item == "default":
                        image_item = random.choice(item[3])
                    else:
                        image_item = item[3]
                    loading = self.bot.get_emoji(794502101853798400)
                    e.description = f"{loading}"
                    e.title = "`🧭          Молитва «Жажда странствий»            `"
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    IacquaintFate_emoji = self.bot.get_emoji(772748673251016745)
                    wishesCount = user["wishesCount"]["IacquaintFate"]
                    #wishes_list = list(filter(lambda x: x["type"] == "wish" and x["name"] == "IacquaintFate", user['inv']))
                    if types_item == "level":
                        if user["lvl"] <= 40:
                            item_push = {
                                "name": "Уровень - 20к",
                                "description": description_item,
                                "id": "",
                                "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878780996684754985/20k.gif",
                                "type": "level",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878780996684754985/20k.gif"
                        elif user["lvl"] >= 41 and user["lvl"] <= 80:
                            item_push = {
                                "name": "Уровень - 35к",
                                "description": description_item,
                                "id": "",
                                "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878782822544973864/35.gif",
                                "type": "level",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878782822544973864/35.gif"
                        else:
                            item_push = {
                                "name": "Уровень - 50к",
                                "description": description_item,
                                "id": "",
                                "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878784429508669450/50.gif",
                                "type": "level",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878784429508669450/50.gif"
                    elif types_item == "primogems":

                        index_item_image = item[3].index(image_item)

                        if index_item_image == 0:
                            amount_primos = 500
                        elif index_item_image == 1:
                            amount_primos = 1000
                        elif index_item_image == 2:
                            amount_primos = 1500

                        item_push = {
                            "name": f"Примогемы - {amount_primos}",
                            "description": description_item,
                            "id": "",
                            "image_url": image_item,
                            "type": "primogems",
                            "date": int(time.time()),
                            "rare": "default"
                        }
                    e.set_image(url=image_item)
                    await interaction.respond(type=7, embed=e, components=[])
                    #time.sleep(1)
                    if type_item == "legendary":
                        if types_item == "characters":
                            item_push = {
                                "name": name_item,
                                "description": item[1],
                                "id": id_item,
                                "image_url": image_item,
                                "type": "characters",
                                "date": int(time.time()),
                                "rare": "legendary"
                            }
                            item_push_waifu = { "type": "waifu", "id": id_item, "equip": 0 }
                            if item_push_waifu in user["inv"]:
                                e.set_footer(text=f"{member.display_name} • Выдано 25.000 примогемов за дубликат.", icon_url=member.avatar_url)
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": 25000 } })
                            else:
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "inv": item_push_waifu } })
                            check_history(member, user, "IacquaintFate", item_push)
                        e.description = f"""
{subdescription_item}
"""
                    elif type_item == "epic":
                        if types_item == "characters":
                            item_push = {
                                "name": name_item,
                                "description": item[1],
                                "id": id_item,
                                "image_url": image_item,
                                "type": "characters",
                                "date": int(time.time()),
                                "rare": "epic"
                            }
                            item_push_waifu = { "type": "waifu", "id": id_item, "equip": 0 }
                            if item_push_waifu in user["inv"]:
                                e.set_footer(text=f"{member.display_name} • Выдано 2.500 примогемов за дубликат.", icon_url=member.avatar_url)
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": 2500 } })
                            else:
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "inv": item_push_waifu } })
                            check_history(member, user, "IacquaintFate", item_push)
                        e.description = f"""
{subdescription_item}
"""
                    else:
                        if types_item == "level":
                            if int(user["lvl"]) <= 40:
                                new_exp = 20000
                            elif int(user["lvl"]) >= 41 and int(user["lvl"]) <= 80:
                                new_exp = 35000
                            else:
                                new_exp = 50000
                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "exp": new_exp } })
                            check_history(member, user, "IacquaintFate", item_push)
                        elif types_item == "primogems":
                            index_item_image = item[3].index(image_item)

                            if index_item_image == 0:
                                amount_primos = 500
                            elif index_item_image == 1:
                                amount_primos = 1000
                            elif index_item_image == 2:
                                amount_primos = 1500

                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": amount_primos } })
                            check_history(member, user, "IacquaintFate", item_push)

                        else:
                            item_push = {
                                "name": f"Пустая крутка",
                                "description": description_item,
                                "id": "",
                                "image_url": image_item,
                                "type": "null",
                                "date": int(time.time()),
                                "rare": "default"

                            }
                            #users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "wishes.IacquaintFate.history": item_push } })
                            check_history(member, user, "IacquaintFate", item_push)
                        e.description = f"""
{description_item}
"""
                    await message.edit(embed=e, components=[
                        [
                            Button(emoji=IacquaintFate_emoji, label="x1",  id="banner_1_wish_x1", style=ButtonStyle.blue, disabled=True if wishesCount - 1 < 1 else False),
                            Button(emoji="⌛", id='history_banner_1', style=ButtonStyle.red),
                            Button(emoji="🏠", id='banners_home', style=ButtonStyle.gray)
                        ]
                    ])

                    users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IacquaintFate": -1 } })
            elif interaction.component.id.startswith("banner_2_"):
                if interaction.component.id == "banner_2_wish_x1":
                    #inv_user = user["inv"]
                    #items_wishes = {'type': 'wish', 'name': 'IntertwinedFate'}
                    #inv_user.remove(items_wishes)
                    #users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IntertwinedFate": -1 } })
                    type_item, item, fifty_fifty = check_procent_wishes(member, user, "IntertwinedFate", 1)
                    if type_item == "legendary":
                        user_all = user["wishes"]["IntertwinedFate"]["all_count_wishes"]
                        user_epic = user["wishes"]["IntertwinedFate"]["count_wishes_warranty_epic"]
                        fifty_fifty_number = 1 if fifty_fifty is False else 0
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$set": { "wishes.IntertwinedFate.count_wishes_warranty_legendary": 0, "wishes.IntertwinedFate.all_count_wishes": user_all + 1, "wishes.IntertwinedFate.count_wishes_warranty_epic": user_epic + 1, "wishes.IntertwinedFate.fifty_fifty": fifty_fifty_number } })
                    else:
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishes.IntertwinedFate.count_wishes_warranty_legendary": 1, "wishes.IntertwinedFate.all_count_wishes": 1, "wishes.IntertwinedFate.count_wishes_warranty_epic": 1 } })
                    if type_item == "epic":
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$set": { "wishes.IntertwinedFate.count_wishes_warranty_epic": 0 } })
                    e = discord.Embed(color=0x2f3136)
                    name_item = item[0]
                    id_item = item[2]
                    types_item = item[4]
                    descriptions_item = item[1].split("|")
                    description_item = descriptions_item[0]
                    if type_item == "legendary" or type_item == "epic":
                        subdescription_item = descriptions_item[1]
                    else:
                        description_item = random.choice(item[1].split("|"))
                    if type_item == "default":
                        image_item = random.choice(item[3])
                    else:
                        image_item = item[3]
                    loading = self.bot.get_emoji(794502101853798400)
                    e.description = f"{loading}"
                    e.title = f"`🧭             Молитва «{config.banner_2_name}»            `"
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    IntertwinedFate_emoji = self.bot.get_emoji(772748672999620629)
                    wishesCount = user["wishesCount"]["IntertwinedFate"]
                    #wishes_list = list(filter(lambda x: x["type"] == "wish" and x["name"] == "IntertwinedFate", user['inv']))
                    if types_item == "level":
                        if int(user["lvl"]) <= 40:
                            item_push = {
                                "name": "Уровень - 20к",
                                "description": description_item,
                                "id": "",
                                "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878780996684754985/20k.gif",
                                "type": "level",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878780996684754985/20k.gif"
                        elif int(user["lvl"]) >= 41 and int(user["lvl"]) <= 80:
                            item_push = {
                                "name": "Уровень - 35к",
                                "description": description_item,
                                "id": "",
                                "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878782822544973864/35.gif",
                                "type": "level",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878782822544973864/35.gif"
                        else:
                            item_push = {
                                "name": "Уровень - 50к",
                                "description": description_item,
                                "id": "",
                                "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878784429508669450/50.gif",
                                "type": "level",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878784429508669450/50.gif"
                    elif types_item == "primogems":

                        index_item_image = item[3].index(image_item)

                        if index_item_image == 0:
                            amount_primos = 500
                        elif index_item_image == 1:
                            amount_primos = 1000
                        elif index_item_image == 2:
                            amount_primos = 1500

                        item_push = {
                            "name": f"Примогемы - {amount_primos}",
                            "description": description_item,
                            "id": "",
                            "image_url": image_item,
                            "type": "primogems",
                            "date": int(time.time()),
                            "rare": "default"
                        }

                    e.set_image(url=image_item)
                    await interaction.respond(type=7, embed=e, components=[])
                    #time.sleep(1)
                    if type_item == "legendary":
                        if types_item == "characters":
                            item_push = {
                                "name": name_item,
                                "description": item[1],
                                "id": id_item,
                                "image_url": image_item,
                                "type": "characters",
                                "date": int(time.time()),
                                "rare": "legendary"
                            }
                            item_push_waifu = { "type": "waifu", "id": id_item, "equip": 0 }
                            if item_push_waifu in user["inv"]:
                                e.set_footer(text=f"{member.display_name} • Выдано 25.000 примогемов за дубликат.", icon_url=member.avatar_url)
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": 25000 } })
                            else:
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "inv": item_push_waifu } })
                            check_history(member, user, "IntertwinedFate", item_push)
                        e.description = f"""
{subdescription_item}
"""
                    elif type_item == "epic":
                        if types_item == "characters":
                            item_push = {
                                "name": name_item,
                                "description": item[1],
                                "id": id_item,
                                "image_url": image_item,
                                "type": "characters",
                                "date": int(time.time()),
                                "rare": "epic"
                            }
                            item_push_waifu = { "type": "waifu", "id": id_item, "equip": 0 }
                            if item_push_waifu in user["inv"]:
                                e.set_footer(text=f"{member.display_name} • Выдано 2.500 примогемов за дубликат.", icon_url=member.avatar_url)
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": 2500 } })
                            else:
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "inv": item_push_waifu } })
                            check_history(member, user, "IntertwinedFate", item_push)
                        e.description = f"""
{subdescription_item}
"""
                    else:
                        if types_item == "level":
                            if int(user["lvl"]) <= 40:
                                new_exp = 20000
                            elif int(user["lvl"]) >= 41 and int(user["lvl"]) <= 80:
                                new_exp = 35000
                            else:
                                new_exp = 50000
                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "exp": new_exp } })
                            check_history(member, user, "IntertwinedFate", item_push)
                        elif types_item == "primogems":
                            index_item_image = item[3].index(image_item)

                            if index_item_image == 0:
                                amount_primos = 500
                            elif index_item_image == 1:
                                amount_primos = 1000
                            elif index_item_image == 2:
                                amount_primos = 1500

                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": amount_primos } })
                            check_history(member, user, "IntertwinedFate", item_push)

                        else:
                            item_push = {
                                "name": f"Пустая крутка",
                                "description": description_item,
                                "id": "",
                                "image_url": image_item,
                                "type": "null",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            #users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "wishes.IntertwinedFate.history": item_push } })
                            check_history(member, user, "IntertwinedFate", item_push)
                        e.description = f"""
{description_item}
"""
                    await message.edit(embed=e, components=[
                        [
                            Button(emoji=IntertwinedFate_emoji, label="x1",  id="banner_2_wish_x1", style=ButtonStyle.blue, disabled=True if wishesCount - 1 < 1 else False),
                            Button(emoji="⌛", id='history_banner_2', style=ButtonStyle.red),
                            Button(emoji="🏠", id='banners_home', style=ButtonStyle.gray)
                        ]
                    ])

                    users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IntertwinedFate": -1 } })
                if interaction.component.id == "banner_2_2_wish_x1":
                    #inv_user = user["inv"]
                    #items_wishes = {'type': 'wish', 'name': 'IntertwinedFate'}
                    #inv_user.remove(items_wishes)
                    #users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IntertwinedFate": -1 } })
                    type_item, item, fifty_fifty = check_procent_wishes(member, user, "IntertwinedFate", 1, second=True)
                    if type_item == "legendary":
                        user_all = user["wishes"]["IntertwinedFate"]["all_count_wishes"]
                        user_epic = user["wishes"]["IntertwinedFate"]["count_wishes_warranty_epic"]
                        fifty_fifty_number = 1 if fifty_fifty is False else 0
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$set": { "wishes.IntertwinedFate.count_wishes_warranty_legendary": 0, "wishes.IntertwinedFate.all_count_wishes": user_all + 1, "wishes.IntertwinedFate.count_wishes_warranty_epic": user_epic + 1, "wishes.IntertwinedFate.fifty_fifty": fifty_fifty_number } })
                    else:
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishes.IntertwinedFate.count_wishes_warranty_legendary": 1, "wishes.IntertwinedFate.all_count_wishes": 1, "wishes.IntertwinedFate.count_wishes_warranty_epic": 1 } })
                    if type_item == "epic":
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$set": { "wishes.IntertwinedFate.count_wishes_warranty_epic": 0 } })
                    e = discord.Embed(color=0x2f3136)
                    name_item = item[0]
                    id_item = item[2]
                    types_item = item[4]
                    descriptions_item = item[1].split("|")
                    description_item = descriptions_item[0]
                    if type_item == "legendary" or type_item == "epic":
                        subdescription_item = descriptions_item[1]
                    else:
                        description_item = random.choice(item[1].split("|"))
                    if type_item == "default":
                        image_item = random.choice(item[3])
                    else:
                        image_item = item[3]
                    loading = self.bot.get_emoji(794502101853798400)
                    e.description = f"{loading}"
                    e.title = f"`🧭          Молитва «{config.banner_2_2_name}»         `"
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    IntertwinedFate_emoji = self.bot.get_emoji(772748672999620629)
                    wishesCount = user["wishesCount"]["IntertwinedFate"]
                    #wishes_list = list(filter(lambda x: x["type"] == "wish" and x["name"] == "IntertwinedFate", user['inv']))
                    if types_item == "level":
                        if int(user["lvl"]) <= 40:
                            item_push = {
                                "name": "Уровень - 20к",
                                "description": description_item,
                                "id": "",
                                "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878780996684754985/20k.gif",
                                "type": "level",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878780996684754985/20k.gif"
                        elif int(user["lvl"]) >= 41 and int(user["lvl"]) <= 80:
                            item_push = {
                                "name": "Уровень - 35к",
                                "description": description_item,
                                "id": "",
                                "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878782822544973864/35.gif",
                                "type": "level",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878782822544973864/35.gif"
                        else:
                            item_push = {
                                "name": "Уровень - 50к",
                                "description": description_item,
                                "id": "",
                                "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878784429508669450/50.gif",
                                "type": "level",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878784429508669450/50.gif"
                    elif types_item == "primogems":

                        index_item_image = item[3].index(image_item)

                        if index_item_image == 0:
                            amount_primos = 500
                        elif index_item_image == 1:
                            amount_primos = 1000
                        elif index_item_image == 2:
                            amount_primos = 1500

                        item_push = {
                            "name": f"Примогемы - {amount_primos}",
                            "description": description_item,
                            "id": "",
                            "image_url": image_item,
                            "type": "primogems",
                            "date": int(time.time()),
                            "rare": "default"
                        }

                    e.set_image(url=image_item)
                    await interaction.respond(type=7, embed=e, components=[])
                    #time.sleep(1)
                    if type_item == "legendary":
                        if types_item == "characters":
                            item_push = {
                                "name": name_item,
                                "description": item[1],
                                "id": id_item,
                                "image_url": image_item,
                                "type": "characters",
                                "date": int(time.time()),
                                "rare": "legendary"
                            }
                            item_push_waifu = { "type": "waifu", "id": id_item, "equip": 0 }
                            if item_push_waifu in user["inv"]:
                                e.set_footer(text=f"{member.display_name} • Выдано 25.000 примогемов за дубликат.", icon_url=member.avatar_url)
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": 25000 } })
                            else:
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "inv": item_push_waifu } })
                            check_history(member, user, "IntertwinedFate", item_push)
                        e.description = f"""
{subdescription_item}
"""
                    elif type_item == "epic":
                        if types_item == "characters":
                            item_push = {
                                "name": name_item,
                                "description": item[1],
                                "id": id_item,
                                "image_url": image_item,
                                "type": "characters",
                                "date": int(time.time()),
                                "rare": "epic"
                            }
                            item_push_waifu = { "type": "waifu", "id": id_item, "equip": 0 }
                            if item_push_waifu in user["inv"]:
                                e.set_footer(text=f"{member.display_name} • Выдано 2.500 примогемов за дубликат.", icon_url=member.avatar_url)
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": 2500 } })
                            else:
                                users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "inv": item_push_waifu } })
                            check_history(member, user, "IntertwinedFate", item_push)
                        e.description = f"""
{subdescription_item}
"""
                    else:
                        if types_item == "level":
                            if int(user["lvl"]) <= 40:
                                new_exp = 20000
                            elif int(user["lvl"]) >= 41 and int(user["lvl"]) <= 80:
                                new_exp = 35000
                            else:
                                new_exp = 50000
                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "exp": new_exp } })
                            check_history(member, user, "IntertwinedFate", item_push)
                        elif types_item == "primogems":
                            index_item_image = item[3].index(image_item)

                            if index_item_image == 0:
                                amount_primos = 500
                            elif index_item_image == 1:
                                amount_primos = 1000
                            elif index_item_image == 2:
                                amount_primos = 1500

                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": amount_primos } })
                            check_history(member, user, "IntertwinedFate", item_push)

                        else:
                            item_push = {
                                "name": f"Пустая крутка",
                                "description": description_item,
                                "id": "",
                                "image_url": image_item,
                                "type": "null",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                            #users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "wishes.IntertwinedFate.history": item_push } })
                            check_history(member, user, "IntertwinedFate", item_push)
                        e.description = f"""
{description_item}
"""
                    await message.edit(embed=e, components=[
                        [
                            Button(emoji=IntertwinedFate_emoji, label="x1",  id="banner_2_2_wish_x1", style=ButtonStyle.blue, disabled=True if wishesCount - 1 < 1 else False),
                            Button(emoji="⌛", id='history_banner_2-2', style=ButtonStyle.red),
                            Button(emoji="🏠", id='banners_home', style=ButtonStyle.gray)
                        ]
                    ])

                    users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IntertwinedFate": -1 } })
            elif interaction.component.id.startswith("banner_3_"):
                if interaction.component.id == "banner_3_wish_x1":
                    #inv_user = user["inv"]
                    #items_wishes = {'type': 'wish', 'name': 'IacquaintFate'}
                    #inv_user.remove(items_wishes)
                    #users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IacquaintFate": -1 } })
                    type_item, item, fifty_fifty = check_procent_wishes(member, user, "ServerFate", 1)
                    if type_item == "legendary":
                        user_all = user["wishes"]["ServerFate"]["all_count_wishes"]
                        user_epic = user["wishes"]["ServerFate"]["count_wishes_warranty_epic"]
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$set": { "wishes.ServerFate.count_wishes_warranty_legendary": 0, "wishes.ServerFate.all_count_wishes": user_all + 1, "wishes.ServerFate.count_wishes_warranty_epic": user_epic + 1 } })
                    else:
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishes.ServerFate.count_wishes_warranty_legendary": 1, "wishes.ServerFate.all_count_wishes": 1, "wishes.ServerFate.count_wishes_warranty_epic": 1 } })
                    if type_item == "epic":
                        users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$set": { "wishes.ServerFate.count_wishes_warranty_epic": 0 } })
                    e = discord.Embed(color=0x2f3136)
                    name_item = item[0]
                    id_item = item[2]
                    types_item = item[4]
                    description_item = random.choice(item[1].split("|"))
                    #description_item = descriptions_item[0]
                    #if type_item == "legendary" or type_item == "epic":
                    #    subdescription_item = descriptions_item[1]
                    if type_item == "default":
                        image_item = random.choice(item[3])
                    else:
                        image_item = item[3]
                    loading = self.bot.get_emoji(794502101853798400)
                    e.description = f"{loading}"
                    e.title = "`🧭        Молитва «Благословение сервера»          `"
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    IacquaintFate_emoji = self.bot.get_emoji(772748673251016745)
                    wishesCount = user["wishesCount"]["IacquaintFate"]
                    #wishes_list = list(filter(lambda x: x["type"] == "wish" and x["name"] == "IacquaintFate", user['inv']))
                    if type_item == "default":
                        if types_item == "level":
                            if user["lvl"] <= 40:
                                item_push = {
                                    "name": "Уровень - 20к",
                                    "description": description_item,
                                    "id": "",
                                    "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878780996684754985/20k.gif",
                                    "type": "level",
                                    "date": int(time.time()),
                                    "rare": "default"
                                }
                                image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878780996684754985/20k.gif"
                            elif user["lvl"] >= 41 and user["lvl"] <= 80:
                                item_push = {
                                    "name": "Уровень - 35к",
                                    "description": description_item,
                                    "id": "",
                                    "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878782822544973864/35.gif",
                                    "type": "level",
                                    "date": int(time.time()),
                                    "rare": "default"
                                }
                                image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878782822544973864/35.gif"
                            else:
                                item_push = {
                                    "name": "Уровень - 50к",
                                    "description": description_item,
                                    "id": "",
                                    "image_url": "https://cdn.discordapp.com/attachments/767015636354203659/878784429508669450/50.gif",
                                    "type": "level",
                                    "date": int(time.time()),
                                    "rare": "default"
                                }
                                image_item = "https://cdn.discordapp.com/attachments/767015636354203659/878784429508669450/50.gif"
                        elif types_item == "primogems":

                            index_item_image = item[3].index(image_item)

                            if index_item_image == 0:
                                amount_primos = 500
                            elif index_item_image == 1:
                                amount_primos = 1000
                            elif index_item_image == 2:
                                amount_primos = 1500

                            item_push = {
                                "name": f"Примогемы - {amount_primos}",
                                "description": description_item,
                                "id": "",
                                "image_url": image_item,
                                "type": "primogems",
                                "date": int(time.time()),
                                "rare": "default"
                            }
                    e.set_image(url=image_item)
                    await interaction.respond(type=7, embed=e, components=[])
                    #time.sleep(1)
                    if type_item == "legendary":
                        if types_item == "wishes_role":
                            item_push = {
                                "name": "Личная роль - 5 дней",
                                "description": f"{description_item}",
                                "id": "",
                                "image_url": image_item,
                                "type": "wishes_role",
                                "date": int(time.time()),
                                "rare": "legendary"
                            }
                            e.description = f"{description_item}"
                            check_history(member, user, "ServerFate", item_push)
                            if roles_wishes.count({ "owner": f"{member.id}" }) == 0:
                                position_role = member.guild.get_role(838484866130772020).position + 1
                                rolew = await member.guild.create_role(name=f"{member.name}")
                                while rolew.position != position_role:
                                    await rolew.edit(position=position_role)
                                roles_wishes.insert_one({ "owner": f'{member.id}', 'roleID': f"{rolew.id}", "timeout": int(time.time()) + 432000 })
                            else:
                                roles_wishes.update_one({ "owner": f"{member.id}" }, { "$inc": { 'timeout': 432000 } })
                        elif types_item == "wishes_wish":
                            item_push = {
                                "name": "Молитвы",
                                "description": f"{description_item}",
                                "id": "",
                                "image_url": image_item,
                                "type": "wishes_wish",
                                "date": int(time.time()),
                                "rare": "legendary"
                            }
                            #itemsw = {
                            #    "type": "wish",
                            #    "name": "IntertwinedFate"
                            #}

                            e.description = f"{description_item}"
                            #push_items = [itemsw for a in range(30)]
                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IntertwinedFate": 30 } })
                            check_history(member, user, "ServerFate", item_push)
                        elif types_item == "wishes_pack":
                            item_push = {
                                "name": "Кастомный пак реакций - 5 дней",
                                "description": f"{description_item}",
                                "id": "",
                                "image_url": image_item,
                                "type": types_item,
                                "date": int(time.time()),
                                "rare": "legendary"
                            }
                            e.description = f"{description_item}"
                            check_history(member, user, "ServerFate", item_push)
                            if packs_wishes.count({ "id": f"{member.id}" }) == 0:
                                packs_wishes.insert_one({ "id": f'{member.id}', "time": int(time.time()) + 432000, "timestamp_coin": 0, "skin": "off" })
                            else:
                                packs_wishes.update_one({ "id": f"{member.id}" }, { "$inc": { 'time': 432000 } })
                        elif types_item == "wishes_banner":
                            item_push = {
                                "name": "Кастомный баннер - 5 дней",
                                "description": f"{description_item}",
                                "id": "",
                                "image_url": image_item,
                                "type": "",
                                "date": int(time.time()),
                                "rare": "legendary"
                            }
                            e.description = f"{description_item}"
                            check_history(member, user, "ServerFate", item_push)
                            if banners_wishes.count({ "id": f"{member.id}" }) == 0:
                                banners_wishes.insert_one({ "id": f'{member.id}', "time": int(time.time()) + 432000, "info": { 'url': '', 'mod': { 'uid': '', 'status': -1, 'reason': '', 'time': 0, 'message_id': '' } } })
                            else:
                                banners_wishes.update_one({ "id": f"{member.id}" }, { "$inc": { 'time': 432000 } })
                        elif types_item == "wishes_special":
                            item_push = {
                                "name": "Особая роль - 5 дней",
                                "description": f"{description_item}",
                                "id": "",
                                "image_url": image_item,
                                "type": types_item,
                                "date": int(time.time()),
                                "rare": "legendary"
                            }
                            e.description = f"{description_item}"
                            if special_role.count({ "id": f"{member.id}" }) == 0:
                                role = member.guild.get_role(config.specialRoleID)
                                await member.add_roles(role)
                                special_role.insert_one({ "id": f'{member.id}', "timeout": int(time.time()) + 432000 })
                            else:
                                special_role.update_one({ "id": f"{member.id}" }, { "$inc": { 'timeout': 432000 } })
                            check_history(member, user, "ServerFate", item_push)
                    elif type_item == "epic":
                        if types_item == "wishes_role":
                            item_push = {
                                "name": "Личная роль - 3 дня",
                                "description": f"{description_item}",
                                "id": "",
                                "image_url": image_item,
                                "type": "wishes_role",
                                "date": int(time.time()),
                                "rare": "epic"
                            }
                            e.description = f"{description_item}"
                            check_history(member, user, "ServerFate", item_push)
                            if roles_wishes.count({ "owner": f"{member.id}" }) == 0:
                                position_role = member.guild.get_role(838484866130772020).position + 1
                                rolew = await member.guild.create_role(name=f"{member.name}")
                                while rolew.position != position_role:
                                    await rolew.edit(position=position_role)
                                roles_wishes.insert_one({ "owner": f'{member.id}', 'roleID': f"{rolew.id}", "timeout": int(time.time()) + 259200 })
                            else:
                                roles_wishes.update_one({ "owner": f"{member.id}" }, { "$inc": { 'timeout': 259200 } })
                        elif types_item == "wishes_wish":
                            item_push = {
                                "name": "Молитвы",
                                "description": f"{description_item}",
                                "id": "",
                                "image_url": image_item,
                                "type": types_item,
                                "date": int(time.time()),
                                "rare": "epic"
                            }
                            #itemsw = {
                            #    "type": "wish",
                            #    "name": "IntertwinedFate"
                            #}

                            e.description = f"{description_item}"
                            #push_items = [itemsw for a in range(5)]
                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IntertwinedFate": 5 } })
                            check_history(member, user, "ServerFate", item_push)
                        elif types_item == "wishes_pack":
                            item_push = {
                                "name": "Кастомный пак реакций - 3 дня",
                                "description": f"{description_item}",
                                "id": "",
                                "image_url": image_item,
                                "type": types_item,
                                "date": int(time.time()),
                                "rare": "epic"
                            }
                            e.description = f"{description_item}"
                            if packs_wishes.count({ "id": f"{member.id}" }) == 0:
                                packs_wishes.insert_one({ "id": f'{member.id}', "time": int(time.time()) + 259200, "timestamp_coin": 0, "skin": "off" })
                            else:
                                packs_wishes.update_one({ "id": f"{member.id}" }, { "$inc": { 'time': 259200 } })
                            check_history(member, user, "ServerFate", item_push)
                        elif types_item == "wishes_banner":
                            item_push = {
                                "name": "Кастомный баннер - 3 дня",
                                "description": f"{description_item}",
                                "id": "",
                                "image_url": image_item,
                                "type": types_item,
                                "date": int(time.time()),
                                "rare": "epic"
                            }
                            e.description = f"{description_item}"
                            if banners_wishes.count({ "id": f"{member.id}" }) == 0:
                                banners_wishes.insert_one({ "id": f'{member.id}', "time": int(time.time()) + 259200, "info": { 'url': '', 'mod': { 'uid': '', 'status': -1, 'reason': '', 'time': 0, 'message_id': '' } } })
                            else:
                                banners_wishes.update_one({ "id": f"{member.id}" }, { "$inc": { 'time': 259200 } })
                            check_history(member, user, "ServerFate", item_push)
                        elif types_item == "wishes_primogems":
                            item_push = {
                                "name": f"Примогемы - 5000",
                                "description": description_item,
                                "id": "",
                                "image_url": image_item,
                                "type": "primogems",
                                "date": int(time.time()),
                                "rare": "epic"
                            }
                            e.description = f"{description_item}"
                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { '$inc': { "money": 5000 } })
                            check_history(member, user, "ServerFate", item_push)
                    else:
                        if types_item == "level":
                            if int(user["lvl"]) <= 40:
                                new_exp = 20000
                            elif int(user["lvl"]) >= 41 and int(user["lvl"]) <= 80:
                                new_exp = 35000
                            else:
                                new_exp = 50000
                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "exp": new_exp } })
                            check_history(member, user, "ServerFate", item_push)
                        elif types_item == "primogems":
                            index_item_image = item[3].index(image_item)

                            if index_item_image == 0:
                                amount_primos = 500
                            elif index_item_image == 1:
                                amount_primos = 1000
                            elif index_item_image == 2:
                                amount_primos = 1500

                            users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "money": amount_primos } })
                            check_history(member, user, "ServerFate", item_push)
                        else:
                            item_push = {
                                "name": f"Пустая крутка",
                                "description": description_item,
                                "id": "",
                                "image_url": image_item,
                                "type": "null",
                                "date": int(time.time()),
                                "rare": "default"

                            }
                            #users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$push": { "wishes.IacquaintFate.history": item_push } })
                            check_history(member, user, "ServerFate", item_push)
                        e.description = f"""
{description_item}
"""
                    await message.edit(embed=e, components=[
                        [
                            Button(emoji=IacquaintFate_emoji, label="x1",  id="banner_3_wish_x1", style=ButtonStyle.blue, disabled=True if wishesCount - 1 < 1 else False),
                            Button(emoji="⌛", id='history_banner_3', style=ButtonStyle.red),
                            Button(emoji="🏠", id='banners_home', style=ButtonStyle.gray)
                        ]
                    ])

                    users.update_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" }, { "$inc": { "wishesCount.IacquaintFate": -1 } })
        elif react["type"] == "shop":
            if interaction.component.id == "shop_home":
                custom = bgs.count({ "id": { "$gte": 1 } })
                roles = shops.count({"type": "roles", "guild": f"{member.guild.id}"})
                e = discord.Embed(title="Магазин Паймон", description="Для выбора магазина используйте кнопки", color=discord.Color(0x2F3136))
                e.add_field(name="```Индекс```", value="```1```", inline=True)
                e.add_field(name="```Категория```", value="```Молитвы```", inline=True)
                e.add_field(name="```Предметов```", value=f"```2```", inline=True)
                e.add_field(name="```Индекс```", value="```2```", inline=True)
                e.add_field(name="```Категория```", value="```Кастомизация```", inline=True)
                e.add_field(name="```Предметов```", value=f"```{custom}```", inline=True)
                e.add_field(name="```Индекс```", value="```3```", inline=True)
                e.add_field(name="```Категория```", value="```Роли```", inline=True)
                e.add_field(name="```Предметов```", value=f"```{roles}```", inline=True)
                e.add_field(name="```Индекс```", value="```4```", inline=True)
                e.add_field(name="```Категория```", value="```Подписки```", inline=True)
                e.add_field(name="```Предметов```", value=f"```1```", inline=True)
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                one = self.bot.get_emoji(826888313448562758)
                two = self.bot.get_emoji(826888462116061234)
                three = self.bot.get_emoji(826888462027194410)
                four = self.bot.get_emoji(826888461994557519)
                await interaction.respond(type=7, embed=e, components=[
                    [
                        Button(emoji=one, id='shop_1', style=ButtonStyle.gray),
                        Button(emoji=two, id='shop_2', style=ButtonStyle.gray),
                        Button(emoji=three, id='shop_3', style=ButtonStyle.gray),
                        Button(emoji=four, id='shop_4', style=ButtonStyle.gray,)
                    ]
                ])
            elif interaction.component.id == "shop_1":
                IacquaintFate = self.bot.get_emoji(772748673251016745)
                IntertwinedFate = self.bot.get_emoji(772748672999620629)
                primogems = self.bot.get_emoji(config.MONEY_EMOJI)
                e = discord.Embed(title="Магазин Паймон", description="Для выбора товара используйте кнопки", color=discord.Color(0x2F3136))
                e.add_field(name="`Молитва`", value=f"{IacquaintFate} Судьбоносные встречи", inline=True)
                e.add_field(name="⠀", value="⠀", inline=True)
                e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                e.add_field(name="`Молитва`", value=f"{IntertwinedFate} Переплетающиеся судьбы", inline=True)
                e.add_field(name="⠀", value="⠀", inline=True)
                e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                one = self.bot.get_emoji(826888313448562758)
                two = self.bot.get_emoji(826888462116061234)
                await interaction.respond(type=7, embed=e, components=[
                    [
                        Button(emoji=IacquaintFate, id='buy_shop_IacquaintFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False),
                        Button(emoji=IntertwinedFate, id='buy_shop_IntertwinedFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False)
                    ],
                    [
                        Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                    ]
                ])
            elif interaction.component.id == "shop_2":
                custom = bgs.find({ "id": { "$gte": 1 } }).sort("id", 1)
                custom = list(custom)
                e = discord.Embed(title=f"Магазин: Именные карточки (категории)", description="", color=discord.Color(0x2F3136))
                battlepass = list(filter(lambda x: x["category"] == "battlepass", custom))
                achievements = list(filter(lambda x: x["category"] == "achievements", custom))
                another = list(filter(lambda x: x["category"] == "another", custom))
                rep = list(filter(lambda x: x["category"] == "rep", custom))
                events = list(filter(lambda x: x["category"] == "events", custom))
                characters = list(filter(lambda x: x["category"] == "characters", custom))
                sevents = list(filter(lambda x: x["category"] == "sevents", custom))
                one = self.bot.get_emoji(826888313448562758)
                two = self.bot.get_emoji(826888462116061234)
                three = self.bot.get_emoji(826888462027194410)
                four = self.bot.get_emoji(826888461994557519)
                five = self.bot.get_emoji(826888461989445672)
                six = self.bot.get_emoji(826888462011203594)
                seven = self.bot.get_emoji(959449156022312960)
                e.description = f"""**
    1.  Боевой пропуск: {len(battlepass)}

    2.  Достижения: {len(achievements)}

    3.  Другое: {len(another)}

    4.  Репутация: {len(rep)}

    5.  События: {len(events)}

    6.  Персонажи: {len(characters)}

    7. Серверная кастомизация: {len(sevents)}**
    """
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                await interaction.respond(type=7, embed=e, components=[
                    [
                        Button(emoji=one, id='shop_2_battlepass', style=ButtonStyle.gray),
                        Button(emoji=two, id='shop_2_achievements', style=ButtonStyle.gray),
                        Button(emoji=three, id='shop_2_another', style=ButtonStyle.gray)
                    ],
                    [
                        Button(emoji=four, id='shop_2_rep', style=ButtonStyle.gray),
                        Button(emoji=five, id='shop_2_events', style=ButtonStyle.gray),
                        Button(emoji=six, id='shop_2_characters', style=ButtonStyle.gray)
                    ],
                    [
                        Button(emoji=seven, id='shop_2_sevents', style=ButtonStyle.gray)
                    ],
                    [
                        Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                    ]
                ])
            elif interaction.component.id == "shop_3":
                roles = list(shops.find({"type": "roles"}).sort("cost", 1))
                roles_chunk = list(func_chunk(roles, 8))
                e = discord.Embed(title=f"Магазин Паймон: Роли (1/{len(roles_chunk)})", color=0x2f3136)
                money_emoji = self.bot.get_emoji(config.MONEY_EMOJI)
                roles_page = roles_chunk[0]
                for x in range(8):
                    e.add_field(name="Роль", value=f"<@&{roles_chunk[0][x]['id']}>")
                    e.add_field(name="⠀", value=f"⠀")
                    e.add_field(name="Цена", value=f"{checkbuy_r(roles_chunk[0][x]['id'], roles_chunk[0][x]['cost'], money_emoji, user)}")

                e.set_footer(text=member.name, icon_url=member.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                nextpageemoji = self.bot.get_emoji(826567984901390366)
                backpageemoji = self.bot.get_emoji(826568061854416946)
                selects = []
                for x in range(8):
                    id_role = roles_chunk[0][x]['id']
                    name_role = member.guild.get_role(int(id_role)).name
                    if checkbuy_r_tf(id_role, user) is False and roles_chunk[0][x]["cost"] < user["money"]:
                        selects.append(SelectOption(label=f"{name_role}", value=f"buy_shop_3_1_role_{id_role}"))
                if len(selects) <= 0:
                    selects.append(SelectOption(label="Увы, здесь пусто.", value=f"None", default=True))
                await interaction.respond(type=7, embed=e, components=[
                    Select(placeholder="Выбери роль, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                    [
                        Button(emoji=nextpageemoji, id=f"shop_3_2_nextpage")
                    ],
                    [
                        Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                    ]
                ])

            elif interaction.component.id == "shop_4":
                e = discord.Embed(title=f"Магазин Паймон: Подписки", color=0x2f3136)
                money_emoji = self.bot.get_emoji(config.MONEY_EMOJI)
                e.add_field(name="Подписка", value=f"<@&912064706414526544>")
                e.add_field(name="⠀", value=f"⠀")
                e.add_field(name="Цена", value=f"3.500{money_emoji}/30 дней" if check_extended_sub(member) is False else "Подиска активирована.")
                selects = []
                e.set_footer(text=member.name, icon_url=member.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
                id_role = 912064706414526544
                name_role = member.guild.get_role(int(id_role)).name
                if check_extended_sub(member) is False and 3500 < user['money']: #checkbuy_r_tf(id_role, user) is False and 3500 < user["money"]:
                    selects.append(SelectOption(label=f"{name_role}", value=f"buy_shop_4_extended"))
                if len(selects) <= 0:
                    selects.append(SelectOption(label="Все подписки активированы.", value=f"None", default=True))
                await interaction.respond(type=7, embed=e, components=[
                    Select(placeholder="Выбери подписку, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                    [
                        Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                    ]
                ])

            elif interaction.component.id.startswith("shop_3_"):

                roles = list(shops.find({"type": "roles", "guild": f"{member.guild.id}"}).sort("cost", 1))
                roles_chunk = list(func_chunk(roles, 8))
                money_emoji = self.bot.get_emoji(config.MONEY_EMOJI)
                user_b = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })

                nextpageemoji = self.bot.get_emoji(826567984901390366)
                backpageemoji = self.bot.get_emoji(826568061854416946)
                interList = interaction.component.id.split("_")

                if interaction.component.id.endswith("nextpage"):
                    page = int(interList[2])
                    e = discord.Embed(title=f"Магазин Паймон: Роли ({page}/{len(roles_chunk)})", color=0x2f3136)
                    roles_page = roles_chunk[page-1]
                    for x in range(len(roles_page)):
                        e.add_field(name="Роль", value=f"<@&{roles_chunk[page - 1][x]['id']}>")
                        e.add_field(name="⠀", value=f"⠀")
                        e.add_field(name="Цена", value=f"{checkbuy_r(roles_chunk[page - 1][x]['id'], roles_chunk[page - 1][x]['cost'], money_emoji, user)}")
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    nextpageemoji = self.bot.get_emoji(826567984901390366)
                    backpageemoji = self.bot.get_emoji(826568061854416946)
                    selects = []
                    for x in range(len(roles_page)):
                        id_role = roles_chunk[page-1][x]['id']
                        name_role = member.guild.get_role(int(id_role)).name
                        if checkbuy_r_tf(id_role, user) is False and roles_chunk[page-1][x]["cost"] < user["money"]:
                            selects.append(SelectOption(label=f"{name_role}", value=f"buy_shop_3_{page}_role_{id_role}"))
                    if len(selects) <= 0:
                        selects.append(SelectOption(label="Увы, здесь пусто.", value=f"None", default=True))
                    if page + 1 > len(roles_chunk):
                        await interaction.respond(type=7, embed=e, components=[
                            Select(placeholder="Выбери роль, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                            [
                                Button(emoji=backpageemoji, id=f"shop_3_{page - 1}_backpage")
                            ],
                            [
                                Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        await interaction.respond(type=7, embed=e, components=[
                            Select(placeholder="Выбери роль, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                            [
                                Button(emoji=backpageemoji, id=f"shop_3_{page - 1}_backpage"),
                                Button(emoji=nextpageemoji, id=f"shop_3_{page + 1}_nextpage")
                            ],
                            [
                                Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                            ]
                        ])
                elif interaction.component.id.endswith("backpage"):
                    page = int(interList[2])
                    e = discord.Embed(title=f"Магазин Паймон: Роли ({page}/{len(roles_chunk)})", color=0x2f3136)
                    roles_page = roles_chunk[page-1]
                    for x in range(len(roles_page)):
                        e.add_field(name="Роль", value=f"<@&{roles_chunk[page - 1][x]['id']}>")
                        e.add_field(name="⠀", value=f"⠀")
                        e.add_field(name="Цена", value=f"{checkbuy_r(roles_chunk[page - 1][x]['id'], roles_chunk[page - 1][x]['cost'], money_emoji, user)}")
                    e.set_footer(text=member.name, icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    nextpageemoji = self.bot.get_emoji(826567984901390366)
                    backpageemoji = self.bot.get_emoji(826568061854416946)
                    selects = []
                    for x in range(len(roles_page)):
                        id_role = roles_chunk[page-1][x]['id']
                        name_role = member.guild.get_role(int(id_role)).name
                        if checkbuy_r_tf(id_role, user) is False and roles_chunk[page-1][x]["cost"] < user["money"]:
                            selects.append(SelectOption(label=f"{name_role}", value=f"buy_shop_3_{page}_role_{id_role}"))
                    if len(selects) <= 0:
                        selects.append(SelectOption(label="Увы, здесь пусто.", value=f"None", default=True))
                    if page - 1 <= 1:
                        await interaction.respond(type=7, embed=e, components=[
                            Select(placeholder="Выбери роль, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                            [
                                Button(emoji=nextpageemoji, id=f"shop_3_{page + 1}_nextpage")
                            ],
                            [
                                Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        await interaction.respond(type=7, embed=e, components=[
                            Select(placeholder="Выбери роль, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                            [
                                Button(emoji=backpageemoji, id=f"shop_3_{page - 1}_backpage"),
                                Button(emoji=nextpageemoji, id=f"shop_3_{page + 1}_nextpage")
                            ],
                            [
                                Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                            ]
                        ])

            elif interaction.component.id.startswith("shop_2_"):
                custom = bgs.find({ "id": { "$gte": 1 } }).sort("id", 1)
                money_emoji = self.bot.get_emoji(config.MONEY_EMOJI)
                user_b = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })

                nextpageemoji = self.bot.get_emoji(826567984901390366)
                backpageemoji = self.bot.get_emoji(826568061854416946)
                firstpageemoji = self.bot.get_emoji(944534104421068811)
                lastpageemoji = self.bot.get_emoji(944534083407593513)

                custom = list(custom)
                interList = interaction.component.id.split("_")
                if interaction.component.id.endswith("nextpage"):
                    category_page = list(filter(lambda x: x["category"] == interList[2], custom))
                    pages_len = len(category_page)
                    index_page = int(interList[3]) - 1
                    cost_custom = category_page[index_page]["cost"]
                    e = discord.Embed(title=f"Магазин Паймон: Именные карточки - {check_name_bgd(interList[2])} ({int(interList[3])}/{pages_len})", description="", color=discord.Color(0x2F3136))
                    segiven = ""
                    if interList[2] == "characters":
                        custom_id = category_page[index_page]["id"]
                        custom_role = category_page[index_page]["role_id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b, custom_role)
                        time_lock = None
                    elif interList[2] == "sevents":
                        custom_id = category_page[index_page]["id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                        if category_page[index_page]['date'] <= int(time.time()):
                            time_lock = True
                        else:
                            time_lock = False
                        segiven = f'\nКарточку получили: {category_page[index_page]["count_buy"]}'
                    else:
                        custom_id = category_page[index_page]["id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                        time_lock = None
                    e.description = f"Название: {cname}\nЦена: {cost[0]}{segiven}"
                    e.set_image(url=f"http://f0604178.xsph.ru/images/profile/preview/{custom_id}.png")
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    if int(interList[3]) + 1 > pages_len:
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[2]}_{int(interList[3])}",
                                        style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                Button(emoji=firstpageemoji, id=f'shop_2_{interList[2]}_firstpage'),
                                Button(emoji=backpageemoji, id=f"shop_2_{interList[2]}_{int(interList[3]) - 1}_backpage")
                            ],
                            [
                                Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[2]}_{int(interList[3])}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                Button(emoji=firstpageemoji, id=f'shop_2_{interList[2]}_firstpage'),
                                Button(emoji=backpageemoji, id=f"shop_2_{interList[2]}_{int(interList[3]) - 1}_backpage"),
                                Button(emoji=nextpageemoji, id=f"shop_2_{interList[2]}_{int(interList[3]) + 1}_nextpage"),
                                Button(emoji=lastpageemoji, id=f'shop_2_{interList[2]}_lastpage')
                            ],

                            [
                                Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                            ]
                        ])
                elif interaction.component.id.endswith("backpage"):
                    category_page = list(filter(lambda x: x["category"] == interList[2], custom))
                    pages_len = len(category_page)
                    index_page = int(interList[3]) - 1
                    cost_custom = category_page[index_page]["cost"]
                    e = discord.Embed(title=f"Магазин Паймон: Именные карточки - {check_name_bgd(interList[2])} ({int(interList[3])}/{pages_len})", description="", color=discord.Color(0x2F3136))
                    segiven = ""
                    if interList[2] == "characters":
                        custom_id = category_page[index_page]["id"]
                        custom_role = category_page[index_page]["role_id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b, custom_role)
                        time_lock = None
                    elif interList[2] == "sevents":
                        custom_id = category_page[index_page]["id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                        if category_page[index_page]['date'] <= int(time.time()):
                            time_lock = True
                        else:
                            time_lock = False
                        segiven = f'\nКарточку получили: {category_page[index_page]["count_buy"]}'
                    else:
                        custom_id = category_page[index_page]["id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                        time_lock = None
                    e.description = f"Название: {cname}\nЦена: {cost[0]}{segiven}"
                    e.set_image(url=f"http://f0604178.xsph.ru/images/profile/preview/{custom_id}.png")
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    if int(interList[3]) - 1 < 1:
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[2]}_{int(interList[3])}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                Button(emoji=nextpageemoji, id=f"shop_2_{interList[2]}_{int(interList[3]) + 1}_nextpage"),
                                Button(emoji=lastpageemoji, id=f'shop_2_{interList[2]}_lastpage')
                            ],
                            [
                                Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[2]}_{int(interList[3])}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                Button(emoji=firstpageemoji, id=f'shop_2_{interList[2]}_firstpage'),
                                Button(emoji=backpageemoji, id=f"shop_2_{interList[2]}_{int(interList[3]) - 1}_backpage"),
                                Button(emoji=nextpageemoji, id=f"shop_2_{interList[2]}_{int(interList[3]) + 1}_nextpage"),
                                Button(emoji=lastpageemoji, id=f'shop_2_{interList[2]}_lastpage')
                            ],

                            [
                                Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                            ]
                        ])
                elif interaction.component.id.endswith("firstpage"):
                    category_page = list(filter(lambda x: x["category"] == interList[2], custom))
                    pages_len = len(category_page)
                    index_page = 0
                    cost_custom = category_page[index_page]["cost"]
                    e = discord.Embed(title=f"Магазин Паймон: Именные карточки - {check_name_bgd(interList[2])} (1/{pages_len})", description="", color=discord.Color(0x2F3136))
                    segiven = ""
                    if interList[2] == "characters":
                        custom_id = category_page[index_page]["id"]
                        custom_role = category_page[index_page]["role_id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b, custom_role)
                        time_lock = None
                    elif interList[2] == "sevents":
                        custom_id = category_page[index_page]["id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                        if category_page[index_page]['date'] <= int(time.time()):
                            time_lock = True
                        else:
                            time_lock = False
                        segiven = f'\nКарточку получили: {category_page[index_page]["count_buy"]}'
                    else:
                        custom_id = category_page[index_page]["id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                        time_lock = None
                    e.description = f"Название: {cname}\nЦена: {cost[0]}{segiven}"
                    e.set_image(url=f"http://f0604178.xsph.ru/images/profile/preview/{custom_id}.png")
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)

                    await interaction.respond(type=7, embed=e, components=[
                        [
                            Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[2]}_1", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                            Button(emoji=nextpageemoji, id=f"shop_2_{interList[2]}_2_nextpage"),
                            Button(emoji=lastpageemoji, id=f'shop_2_{interList[2]}_lastpage')
                        ],
                        [
                            Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                        ]
                    ])
                elif interaction.component.id.endswith("lastpage"):
                    category_page = list(filter(lambda x: x["category"] == interList[2], custom))
                    pages_len = len(category_page)
                    index_page = pages_len-1
                    cost_custom = category_page[index_page]["cost"]
                    e = discord.Embed(title=f"Магазин Паймон: Именные карточки - {check_name_bgd(interList[2])} ({pages_len}/{pages_len})", description="", color=discord.Color(0x2F3136))
                    segiven = ""
                    if interList[2] == "characters":
                        custom_id = category_page[index_page]["id"]
                        custom_role = category_page[index_page]["role_id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b, custom_role)
                        time_lock = None
                    elif interList[2] == "sevents":
                        custom_id = category_page[index_page]["id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                        if category_page[index_page]['date'] <= int(time.time()):
                            time_lock = True
                        else:
                            time_lock = False
                        segiven = f'\nКарточку получили: {category_page[index_page]["count_buy"]}'
                    else:
                        custom_id = category_page[index_page]["id"]
                        cname = category_page[index_page]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                        time_lock = None
                    e.description = f"Название: {cname}\nЦена: {cost[0]}{segiven}"
                    e.set_image(url=f"http://f0604178.xsph.ru/images/profile/preview/{custom_id}.png")
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)

                    await interaction.respond(type=7, embed=e, components=[
                        [
                            Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[2]}_{pages_len}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                            Button(emoji=firstpageemoji, id=f'shop_2_{interList[2]}_firstpage'),
                            Button(emoji=backpageemoji, id=f"shop_2_{interList[2]}_{index_page}_backpage")
                        ],
                        [
                            Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                        ]
                    ])
                else:

                    category_page = list(filter(lambda x: x["category"] == interList[2], custom))
                    pages_len = len(category_page)
                    cost_custom = category_page[0]["cost"]
                    e = discord.Embed(title=f"Магазин Паймон: Именные карточки - {check_name_bgd(interList[2])} (1/{pages_len})", description="", color=discord.Color(0x2F3136))
                    segiven = ""
                    if interList[2] == "characters":
                        custom_id = category_page[0]["id"]
                        custom_role = category_page[0]["role_id"]
                        cname = category_page[0]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[0]["cost"]), money_emoji, user_b, custom_role)
                        time_lock = None
                    elif interList[2] == "sevents":
                        custom_id = category_page[0]["id"]
                        cname = category_page[0]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[0]["cost"]), money_emoji, user_b)
                        if category_page[0]['date'] <= int(time.time()):
                            time_lock = True
                        else:
                            time_lock = False
                        segiven = f'\nКарточку получили: {category_page[0]["count_buy"]}'
                    else:
                        custom_id = category_page[0]["id"]
                        cname = category_page[0]["name"]
                        cost = checkbuy_c(custom_id, str(category_page[0]["cost"]), money_emoji, user_b)
                        time_lock = None
                    e.description = f"Название: {cname}\nЦена: {cost[0]}{segiven}"
                    e.set_image(url=f"http://f0604178.xsph.ru/images/profile/preview/{custom_id}.png")
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    if pages_len == 1:

                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(label=f"{seconds_to_hh_mm_ss(category_page[0]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[2]}_1", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(label=f"{seconds_to_hh_mm_ss(category_page[0]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[2]}_1", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                Button(emoji=nextpageemoji, id=f"shop_2_{interList[2]}_2_nextpage"),
                                Button(emoji=lastpageemoji, id=f'shop_2_{interList[2]}_lastpage')
                            ],
                            [
                                Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                            ]
                        ])


            elif interaction.component.id.startswith("buy_shop"):
                if interaction.component.id.startswith("buy_shop_custom"):
                    interList = interaction.component.id.split("_")
                    custom_buy = bgs.find_one({ "id": int(interList[3]) })
                    custom_emoji = self.bot.get_emoji(int(custom_buy['emoji']))
                    custom_name = custom_buy["name"]
                    custom_cost = custom_buy["cost"]
                    e = discord.Embed(description=f"Вы точно уверены, что хотите купить **{custom_emoji} {custom_name}**?", color=0x2f3136)
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    yes_emoji = self.bot.get_emoji(879083428836933712)
                    no_emoji = self.bot.get_emoji(879083439742152744)
                    await interaction.respond(type=7, embed=e, components=[
                        [
                            Button(emoji=yes_emoji, id=f"{interList[3]}_buy_yes", style=ButtonStyle.green),
                            Button(emoji=no_emoji, id=f"{interList[3]}_buy_no", style=ButtonStyle.red)
                        ]
                    ])
                    interaction_buy = await self.bot.wait_for("button_click", check=lambda i: i.component.id.startswith(f"{interList[3]}") and i.user.id == int(react["user_id"]))
                    if interaction_buy.component.id == f"{interList[3]}_buy_yes":
                        if user["money"] < custom_cost:
                            e = discord.Embed(description=f"Недостаточно примогемов на балансе.", color=0x2f3136)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await interaction_buy.respond(embed=e, components=[])
                        else:
                            e = discord.Embed(description=f"Вы успешно купили **{custom_emoji} {custom_name}**", color=0x2f3136)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await interaction_buy.respond(embed=e, components=[])
                            item = { "type": "background", "id": custom_buy["id"] }
                            users.update_one({ "disid": f'{member.id}', "guild": f'{member.guild.id}' }, { "$push": { "inv": item }, "$inc": { "money": -(custom_cost) } })
                            if interList[4] == 'sevents':
                                bgs.update_one({ "id": int(interList[3]) }, { "$inc": { "count_buy": 1 } })
                        custom = bgs.find({ "id": { "$gte": 1 } }).sort("id", 1)
                        money_emoji = self.bot.get_emoji(config.MONEY_EMOJI)
                        user_b = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })

                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        firstpageemoji = self.bot.get_emoji(944534104421068811)
                        lastpageemoji = self.bot.get_emoji(944534083407593513)
                        category_page = list(filter(lambda x: x["category"] == interList[4], custom))
                        pages_len = len(category_page)
                        index_page = int(interList[5]) - 1
                        cost_custom = category_page[index_page]["cost"]
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки - {check_name_bgd(interList[4])} ({int(interList[5])}/{pages_len})", description="", color=discord.Color(0x2F3136))
                        segiven = ""
                        if interList[4] == "characters":
                            custom_id = category_page[index_page]["id"]
                            custom_role = category_page[index_page]["role_id"]
                            cname = category_page[index_page]["name"]
                            cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b, custom_role)
                            time_lock = None
                        elif interList[4] == "sevents":
                            custom_id = category_page[index_page]["id"]
                            cname = category_page[index_page]["name"]
                            cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                            if category_page[index_page]['date'] <= int(time.time()):
                                time_lock = True
                            else:
                                time_lock = False
                            segiven = f'\nКарточку получили: {category_page[index_page]["count_buy"]}'
                        else:
                            custom_id = category_page[index_page]["id"]
                            cname = category_page[index_page]["name"]
                            cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                            time_lock = None
                        e.description = f"Название: {cname}\nЦена: {cost[0]}{segiven}"
                        e.set_image(url=f"http://f0604178.xsph.ru/images/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        if int(interList[5]) + 1 > pages_len:
                            await message.edit(embed=e, components=[
                                [
                                    Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[4]}_{int(interList[5])}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                    Button(emoji=firstpageemoji, id=f'shop_2_{interList[4]}_firstpage'),
                                    Button(emoji=backpageemoji, id=f"shop_2_{interList[4]}_{int(interList[5]) - 1}_backpage")
                                ],
                                [
                                    Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                                ]
                            ])
                        elif int(interList[5]) - 1 < 1:
                            await message.edit(embed=e, components=[
                                [
                                    Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[4]}_{int(interList[5])}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                    Button(emoji=nextpageemoji, id=f"shop_2_{interList[4]}_{int(interList[5]) + 1}_nextpage"),
                                    Button(emoji=lastpageemoji, id=f'shop_2_{interList[4]}_lastpage')
                                ],
                                [
                                    Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await message.edit(embed=e, components=[
                                [
                                    Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[4]}_{int(interList[5])}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                    Button(emoji=firstpageemoji, id=f'shop_2_{interList[4]}_firstpage'),
                                    Button(emoji=backpageemoji, id=f"shop_2_{interList[4]}_{int(interList[5]) - 1}_backpage"),
                                    Button(emoji=nextpageemoji, id=f"shop_2_{interList[4]}_{int(interList[5]) + 1}_nextpage"),
                                    Button(emoji=lastpageemoji, id=f'shop_2_{interList[4]}_lastpage')
                                ],

                                [
                                    Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                                ]
                            ])
                    else:
                        e = discord.Embed(description=f"Вы отказались от покупки **{custom_emoji} {custom_name}**", color=0x2f3136)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await interaction_buy.respond(embed=e, components=[])
                        custom = bgs.find({ "id": { "$gte": 1 } }).sort("id", 1)
                        money_emoji = self.bot.get_emoji(config.MONEY_EMOJI)
                        user_b = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })

                        nextpageemoji = self.bot.get_emoji(826567984901390366)
                        backpageemoji = self.bot.get_emoji(826568061854416946)
                        firstpageemoji = self.bot.get_emoji(944534104421068811)
                        lastpageemoji = self.bot.get_emoji(944534083407593513)
                        category_page = list(filter(lambda x: x["category"] == interList[4], custom))
                        pages_len = len(category_page)
                        index_page = int(interList[5]) - 1
                        cost_custom = category_page[index_page]["cost"]
                        e = discord.Embed(title=f"Магазин Паймон: Именные карточки - {check_name_bgd(interList[4])} ({int(interList[5])}/{pages_len})", description="", color=discord.Color(0x2F3136))
                        segiven = ""
                        if interList[4] == "characters":
                            custom_id = category_page[index_page]["id"]
                            custom_role = category_page[index_page]["role_id"]
                            cname = category_page[index_page]["name"]
                            cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b, custom_role)
                            time_lock = None
                        elif interList[4] == "sevents":
                            custom_id = category_page[index_page]["id"]
                            cname = category_page[index_page]["name"]
                            cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                            if category_page[index_page]['date'] <= int(time.time()):
                                time_lock = True
                            else:
                                time_lock = False
                            segiven = f'\nКарточку получили: {category_page[index_page]["count_buy"]}'
                        else:
                            custom_id = category_page[index_page]["id"]
                            cname = category_page[index_page]["name"]
                            cost = checkbuy_c(custom_id, str(category_page[index_page]["cost"]), money_emoji, user_b)
                            time_lock = None
                        e.description = f"Название: {cname}\nЦена: {cost[0]}{segiven}"
                        e.set_image(url=f"http://f0604178.xsph.ru/images/profile/preview/{custom_id}.png")
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        if int(interList[5]) + 1 > pages_len:
                            await message.edit(embed=e, components=[
                                [
                                    Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[4]}_{int(interList[5])}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                    Button(emoji=firstpageemoji, id=f'shop_2_{interList[4]}_firstpage'),
                                    Button(emoji=backpageemoji, id=f"shop_2_{interList[4]}_{int(interList[5]) - 1}_backpage")
                                ],
                                [
                                    Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                                ]
                            ])
                        elif int(interList[5]) - 1 < 1:
                            await message.edit(embed=e, components=[
                                [
                                    Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[4]}_{int(interList[5])}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                    Button(emoji=nextpageemoji, id=f"shop_2_{interList[4]}_{int(interList[5]) + 1}_nextpage"),
                                    Button(emoji=lastpageemoji, id=f'shop_2_{interList[4]}_lastpage')
                                ],
                                [
                                    Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await message.edit(embed=e, components=[
                                [
                                    Button(label=f"{seconds_to_hh_mm_ss(category_page[index_page]['date'])}", style=ButtonStyle.gray, disabled=True) if time_lock is True else Button(label="Заблокировано", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.gray, disabled=True) if cost[1] is False else Button(label="Куплено", id=f"buy_shop_custom_{custom_id}", style=ButtonStyle.red, disabled=True) if cost[1] is True else Button(label="Купить", id=f"buy_shop_custom_{custom_id}_{interList[4]}_{int(interList[5])}", style=ButtonStyle.green, disabled=True if user_b["money"] < cost_custom else False),
                                    Button(emoji=firstpageemoji, id=f'shop_2_{interList[4]}_firstpage'),
                                    Button(emoji=backpageemoji, id=f"shop_2_{interList[4]}_{int(interList[5]) - 1}_backpage"),
                                    Button(emoji=nextpageemoji, id=f"shop_2_{interList[4]}_{int(interList[5]) + 1}_nextpage"),
                                    Button(emoji=lastpageemoji, id=f'shop_2_{interList[4]}_lastpage')
                                ],

                                [
                                    Button(emoji="🏠", id='shop_2', style=ButtonStyle.gray)
                                ]
                            ])

                elif interaction.component.id == "buy_shop_IacquaintFate":
                    IacquaintFate = self.bot.get_emoji(772748673251016745)
                    e = discord.Embed(description=f"Выберете количество покупаемого товара \"**{IacquaintFate} Судьбоносные встречи**\"", color=0x2f3136)
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    items_buy_wishes = 0
                    bal_user = user["money"]
                    while bal_user - 1600 >= 0:
                        items_buy_wishes += 1
                        bal_user -= 1600
                        if items_buy_wishes >= 25:
                            break

                    arr_buy_wishes = []

                    for a in range(items_buy_wishes):
                        arr_buy_wishes.append(SelectOption(label=f"{a + 1}", value=f"buy_wishes_IacquaintFate_{a + 1}"))

                    if len(arr_buy_wishes) <= 0:
                        arr_buy_wishes.append(SelectOption(label="Увы, здесь пусто.", value=f"None", default=True))

                    await interaction.respond(type=7, embed=e, components=[
                        Select(placeholder="Выберете количество покупаемых молитв", options=arr_buy_wishes, disabled=True if arr_buy_wishes[0].value == "None" else False),
                        [
                            Button(emoji="🏠", id='shop_1', style=ButtonStyle.gray)
                        ]
                    ])

                    interaction_buy_1 = await self.bot.wait_for("select_option", check=lambda i: i.values[0].startswith(f"buy_wishes_IacquaintFate") and i.user.id == int(react["user_id"]))

                    count_wishes_buy = int(interaction_buy_1.values[0].split("_")[3])

                    e = discord.Embed(description=f"Вы точно уверены, что хотите купить **{IacquaintFate} Судьбоносные встречи** x{count_wishes_buy}?", color=0x2f3136)
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    yes_emoji = self.bot.get_emoji(879083428836933712)
                    no_emoji = self.bot.get_emoji(879083439742152744)
                    await interaction_buy_1.respond(type=7, embed=e, components=[
                        [
                            Button(emoji=yes_emoji, id="IacquaintFate_buy_yes", style=ButtonStyle.green),
                            Button(emoji=no_emoji, id="IacquaintFate_buy_no", style=ButtonStyle.red)
                        ]
                    ])
                    interaction_buy = await self.bot.wait_for("button_click", check=lambda i: i.component.id.startswith("IacquaintFate") and i.user.id == int(react["user_id"]))
                    if interaction_buy.component.id == "IacquaintFate_buy_yes":
                        if user["money"] < 1600 * count_wishes_buy:
                            e = discord.Embed(description=f"Недостаточно примогемов на балансе.", color=0x2f3136)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await interaction_buy.respond(embed=e, components=[])
                        else:
                            e = discord.Embed(description=f"Вы успешно купили **{IacquaintFate} Судьбоносные встречи** x{count_wishes_buy}", color=0x2f3136)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await interaction_buy.respond(embed=e, components=[])
                            #item = [{ "type": "wish", "name": "IacquaintFate" } for x in range(count_wishes_buy)]
                            users.update_one({ "disid": f'{member.id}', "guild": f'{member.guild.id}' }, { "$inc": { "money": -1600 * count_wishes_buy, "wishesCount.IacquaintFate": count_wishes_buy } })
                            users.update_one({ "disid": "665667955220021250", "guild": "604083589570625555" }, { "$inc": { "money": 1600 * count_wishes_buy } })
                        IacquaintFate = self.bot.get_emoji(772748673251016745)
                        IntertwinedFate = self.bot.get_emoji(772748672999620629)
                        primogems = self.bot.get_emoji(config.MONEY_EMOJI)
                        e = discord.Embed(title="Магазин Паймон", description="Для выбора товара используйте кнопки", color=discord.Color(0x2F3136))
                        e.add_field(name="`Молитва`", value=f"{IacquaintFate} Судьбоносные встречи", inline=True)
                        e.add_field(name="⠀", value="⠀", inline=True)
                        e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                        e.add_field(name="`Молитва`", value=f"{IntertwinedFate} Переплетающиеся судьбы", inline=True)
                        e.add_field(name="⠀", value="⠀", inline=True)
                        e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        one = self.bot.get_emoji(826888313448562758)
                        two = self.bot.get_emoji(826888462116061234)
                        await message.edit(embed=e, components=[
                            [
                                Button(emoji=IacquaintFate, id='buy_shop_IacquaintFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False),
                                Button(emoji=IntertwinedFate, id='buy_shop_IntertwinedFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False)
                            ],
                            [
                                Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        e = discord.Embed(description=f"Вы отказались от покупки **{IacquaintFate} Судьбоносные встречи**", color=0x2f3136)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await interaction_buy.respond(embed=e, components=[])
                        IacquaintFate = self.bot.get_emoji(772748673251016745)
                        IntertwinedFate = self.bot.get_emoji(772748672999620629)
                        primogems = self.bot.get_emoji(config.MONEY_EMOJI)
                        e = discord.Embed(title="Магазин Паймон", description="Для выбора товара используйте кнопки", color=discord.Color(0x2F3136))
                        e.add_field(name="`Молитва`", value=f"{IacquaintFate} Судьбоносные встречи", inline=True)
                        e.add_field(name="⠀", value="⠀", inline=True)
                        e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                        e.add_field(name="`Молитва`", value=f"{IntertwinedFate} Переплетающиеся судьбы", inline=True)
                        e.add_field(name="⠀", value="⠀", inline=True)
                        e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        one = self.bot.get_emoji(826888313448562758)
                        two = self.bot.get_emoji(826888462116061234)
                        await message.edit(embed=e, components=[
                            [
                                Button(emoji=IacquaintFate, id='buy_shop_IacquaintFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False),
                                Button(emoji=IntertwinedFate, id='buy_shop_IntertwinedFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False)
                            ],
                            [
                                Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                            ]
                        ])
                elif interaction.component.id == "buy_shop_IntertwinedFate":
                    IntertwinedFate = self.bot.get_emoji(772748672999620629)
                    e = discord.Embed(description=f"Выберете количество покупаемого товара \"**{IntertwinedFate} Переплетающиеся судьбы**\"", color=0x2f3136)
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    items_buy_wishes = 0
                    bal_user = user["money"]
                    while bal_user - 1600 >= 0:
                        items_buy_wishes += 1
                        bal_user -= 1600
                        if items_buy_wishes >= 25:
                            break

                    arr_buy_wishes = []

                    for a in range(items_buy_wishes):
                        arr_buy_wishes.append(SelectOption(label=f"{a + 1}", value=f"buy_wishes_IntertwinedFate_{a + 1}"))

                    if len(arr_buy_wishes) <= 0:
                        arr_buy_wishes.append(SelectOption(label="Увы, здесь пусто.", value=f"None", default=True))

                    await interaction.respond(type=7, embed=e, components=[
                        Select(placeholder="Выберете количество покупаемых молитв", options=arr_buy_wishes, disabled=True if arr_buy_wishes[0].value == "None" else False),
                        [
                            Button(emoji="🏠", id='shop_1', style=ButtonStyle.gray)
                        ]
                    ])

                    interaction_buy_1 = await self.bot.wait_for("select_option", check=lambda i: i.values[0].startswith(f"buy_wishes_IntertwinedFate") and i.user.id == int(react["user_id"]))

                    count_wishes_buy = int(interaction_buy_1.values[0].split("_")[3])
                    e = discord.Embed(description=f"Вы точно уверены, что хотите купить **{IntertwinedFate} Переплетающиеся судьбы** x{count_wishes_buy}?", color=0x2f3136)
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    yes_emoji = self.bot.get_emoji(879083428836933712)
                    no_emoji = self.bot.get_emoji(879083439742152744)
                    await interaction_buy_1.respond(type=7, embed=e, components=[
                        [
                            Button(emoji=yes_emoji, id="IntertwinedFate_buy_yes", style=ButtonStyle.green),
                            Button(emoji=no_emoji, id="IntertwinedFate_buy_no", style=ButtonStyle.red)
                        ]
                    ])
                    interaction_buy = await self.bot.wait_for("button_click", check=lambda i: i.component.id.startswith("IntertwinedFate") and i.user.id == int(react["user_id"]))
                    if interaction_buy.component.id == "IntertwinedFate_buy_yes":
                        if user["money"] < 1600 * count_wishes_buy:
                            e = discord.Embed(description=f"Недостаточно примогемов на балансе.", color=0x2f3136)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await interaction_buy.respond(embed=e, components=[])
                        else:
                            e = discord.Embed(description=f"Вы успешно купили **{IntertwinedFate} Переплетающиеся судьбы** x{count_wishes_buy}", color=0x2f3136)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            await interaction_buy.respond(embed=e, components=[])
                            #item = [{ "type": "wish", "name": "IntertwinedFate" } for a in range(count_wishes_buy)]
                            users.update_one({ "disid": f'{member.id}', "guild": f'{member.guild.id}' }, { "$inc": { "money": -1600 * count_wishes_buy, "wishesCount.IntertwinedFate": count_wishes_buy } })
                            users.update_one({ "disid": "665667955220021250", "guild": "604083589570625555" }, { "$inc": { "money": 1600 * count_wishes_buy } })
                        IacquaintFate = self.bot.get_emoji(772748673251016745)
                        IntertwinedFate = self.bot.get_emoji(772748672999620629)
                        primogems = self.bot.get_emoji(config.MONEY_EMOJI)
                        e = discord.Embed(title="Магазин Паймон", description="Для выбора товара используйте кнопки", color=discord.Color(0x2F3136))
                        e.add_field(name="`Молитва`", value=f"{IacquaintFate} Судьбоносные встречи", inline=True)
                        e.add_field(name="⠀", value="⠀", inline=True)
                        e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                        e.add_field(name="`Молитва`", value=f"{IntertwinedFate} Переплетающиеся судьбы", inline=True)
                        e.add_field(name="⠀", value="⠀", inline=True)
                        e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        one = self.bot.get_emoji(826888313448562758)
                        two = self.bot.get_emoji(826888462116061234)
                        await message.edit(embed=e, components=[
                            [
                                Button(emoji=IacquaintFate, id='buy_shop_IacquaintFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False),
                                Button(emoji=IntertwinedFate, id='buy_shop_IntertwinedFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False)
                            ],
                            [
                                Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                            ]
                        ])
                    else:
                        e = discord.Embed(description=f"Вы отказались от покупки **{IntertwinedFate} Переплетающиеся судьбы**", color=0x2f3136)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        await interaction_buy.respond(embed=e, components=[])
                        IacquaintFate = self.bot.get_emoji(772748673251016745)
                        IntertwinedFate = self.bot.get_emoji(772748672999620629)
                        primogems = self.bot.get_emoji(config.MONEY_EMOJI)
                        e = discord.Embed(title="Магазин Паймон", description="Для выбора товара используйте кнопки", color=discord.Color(0x2F3136))
                        e.add_field(name="`Молитва`", value=f"{IacquaintFate} Судьбоносные встречи", inline=True)
                        e.add_field(name="⠀", value="⠀", inline=True)
                        e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                        e.add_field(name="`Молитва`", value=f"{IntertwinedFate} Переплетающиеся судьбы", inline=True)
                        e.add_field(name="⠀", value="⠀", inline=True)
                        e.add_field(name="`Цена`", value=f"1600 {primogems}", inline=True)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        one = self.bot.get_emoji(826888313448562758)
                        two = self.bot.get_emoji(826888462116061234)
                        await message.edit(embed=e, components=[
                            [
                                Button(emoji=IacquaintFate, id='buy_shop_IacquaintFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False),
                                Button(emoji=IntertwinedFate, id='buy_shop_IntertwinedFate', style=ButtonStyle.blue, disabled=True if user["money"] < 1600 else False)
                            ],
                            [
                                Button(emoji="  ", id='shop_home', style=ButtonStyle.gray)
                            ]
                        ])


def setup(bot):
    bot.add_cog(Buttons(bot))
