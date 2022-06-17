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
extended_sub = db2.extended_sub

def func_chunk(lst, n):
    for x in range(0, len(lst), n):
        e_c = lst[x : n + x]
        yield e_c

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

class Selects(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        if interaction.values[0].startswith("events"):
            return
        if interaction.values[0].startswith("settings"):
            return
        if reactions.count_documents({ "message_id": str(interaction.message.id) }) == 0:
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
        if react["type"] == "shop":
            if interaction.values[0].startswith("buy"):
                if "shop_4" in interaction.values[0]:
                    interList = interaction.values[0].split("_")
                    sub_type = interList[3]
                    if sub_type == "extended":
                        if 3500 > user["money"]:
                            e = discord.Embed(color=0x2f3136)
                            e.description = f"Недостаточно примогемов на балансе."
                            e.set_footer(name=member.name, icon_url=member.display_avatar)
                            e.timestamp = datetime.datetime.utcnow()
                            return await interaction.respond(embed=e)
                        else:

                            e = discord.Embed(description=f"Вы точно уверены, что хотите купить подписку <@&912064706414526544>?", color=0x2f3136)
                            e.timestamp = datetime.datetime.utcnow()
                            e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                            yes_emoji = self.bot.get_emoji(879083428836933712)
                            no_emoji = self.bot.get_emoji(879083439742152744)
                            await interaction.respond(type=7, embed=e, components=[
                                [
                                    Button(emoji=yes_emoji, id=f"extended_buy_yes", style=ButtonStyle.green),
                                    Button(emoji=no_emoji, id=f"extended_buy_no", style=ButtonStyle.red)
                                ]
                            ])
                            interaction_buy = await self.bot.wait_for("button_click", check=lambda i: i.component.id.startswith(f"extended") and i.user.id == int(react["user_id"]))
                            if interaction_buy.component.id == f"extended_buy_yes":
                                e2 = discord.Embed(color=0x2f3136)
                                e2.title = "Магазин Паймон"
                                e2.description = f"Покупка совершена! Подписка <@&912064706414526544> была добавлена в инвентарь."
                                e2.set_footer(text=member.name, icon_url=member.avatar_url)
                                e2.timestamp = datetime.datetime.utcnow()
                                await interaction_buy.respond(embed=e2)

                                #item_role = { 'type': 'role', 'id': role_id }
                                role_sub = member.guild.get_role(912064706414526544)
                                await member.add_roles(role_sub)

                                users.update_one({ "disid": f"{member.id}", "guild": f'{member.guild.id}' }, { "$inc": { "money": -3500 } })
                                extended_sub.insert_one({ 'id': f"{member.id}", 'sub_pay_time': int(time.time()) })
                                user = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                            else:
                                e2 = discord.Embed(color=0x2f3136)
                                e2.title = "Магазин Паймон"
                                e2.description = f"Вы отказались от покупкки <@&912064706414526544>"
                                e2.set_footer(text=member.name, icon_url=member.avatar_url)
                                e2.timestamp = datetime.datetime.utcnow()
                                await interaction_buy.respond(embed=e2)

                            e3 = discord.Embed(title=f"Магазин Паймон: Подписки", color=0x2f3136)
                            money_emoji = self.bot.get_emoji(config.MONEY_EMOJI)
                            e3.add_field(name="Подписка", value=f"<@&912064706414526544>")
                            e3.add_field(name="⠀", value=f"⠀")
                            e3.add_field(name="Цена", value=f"3.500{money_emoji}/месяц" if check_extended_sub(member) is False else "Подиска активирована.")
                            selects = []
                            e3.set_footer(text=member.name, icon_url=member.avatar_url)
                            e3.timestamp = datetime.datetime.utcnow()
                            id_role = 912064706414526544
                            name_role = member.guild.get_role(int(id_role)).name
                            if check_extended_sub(member) is False and 3500 < user['money']: #checkbuy_r_tf(id_role, user) is False and 3500 < user["money"]:
                                selects.append(SelectOption(label=f"{name_role}", value=f"buy_shop_4_extended"))
                            if len(selects) <= 0:
                                selects.append(SelectOption(label="Все подписки активированы.", value=f"None", default=True))
                            await message.edit(embed=e3, components=[
                                Select(placeholder="Выбери подписку, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                                [
                                    Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                                ]
                            ])
                if "shop_3" in interaction.values[0]:
                    interList = interaction.values[0].split("_")
                    page = int(interList[3])
                    role_id = interList[5]
                    role = shops.find_one({"type": "roles", "guild": f"{member.guild.id}", "id": role_id})
                    if role["cost"] > user["money"]:
                        e = discord.Embed(color=0x2f3136)
                        e.description = f"Недостаточно примогемов на балансе."
                        e.set_footer(name=member.name, icon_url=member.display_avatar)
                        e.timestamp = datetime.datetime.utcnow()
                        return await interaction.respond(embed=e)
                    else:

                        e = discord.Embed(description=f"Вы точно уверены, что хотите купить роль <@&{role_id}>?", color=0x2f3136)
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                        yes_emoji = self.bot.get_emoji(879083428836933712)
                        no_emoji = self.bot.get_emoji(879083439742152744)
                        await interaction.respond(type=7, embed=e, components=[
                            [
                                Button(emoji=yes_emoji, id=f"{role_id}_buy_yes", style=ButtonStyle.green),
                                Button(emoji=no_emoji, id=f"{role_id}_buy_no", style=ButtonStyle.red)
                            ]
                        ])
                        interaction_buy = await self.bot.wait_for("button_click", check=lambda i: i.component.id.startswith(f"{role_id}") and i.user.id == int(react["user_id"]))
                        if interaction_buy.component.id == f"{role_id}_buy_yes":
                            e2 = discord.Embed(color=0x2f3136)
                            e2.title = "Магазин Паймон"
                            e2.description = f"Покупка совершена! Роль <@&{role_id}> была добавлена в инвентарь."
                            e2.set_footer(text=member.name, icon_url=member.avatar_url)
                            e2.timestamp = datetime.datetime.utcnow()
                            await interaction_buy.respond(embed=e2)

                            item_role = { 'type': 'role', 'id': role_id }

                            users.update_one({ "disid": f"{member.id}", "guild": f'{member.guild.id}' }, { "$inc": { "money": -role["cost"] }, "$push": { "inv": item_role } })

                            user = users.find_one({ "disid": f"{member.id}", "guild": f"{member.guild.id}" })
                        else:
                            e2 = discord.Embed(color=0x2f3136)
                            e2.title = "Магазин Паймон"
                            e2.description = f"Вы отказались от покупкки <@&{role_id}>"
                            e2.set_footer(text=member.name, icon_url=member.avatar_url)
                            e2.timestamp = datetime.datetime.utcnow()
                            await interaction_buy.respond(embed=e2)

                        roles = list(shops.find({"type": "roles", "guild": f"{member.guild.id}"}).sort("cost", 1))
                        roles_chunk = list(func_chunk(roles, 8))
                        e = discord.Embed(title=f"Магазин Паймон: Роли ({page}/{len(roles_chunk)})", color=0x2f3136)
                        roles_page = roles_chunk[page-1]
                        money_emoji = self.bot.get_emoji(config.MONEY_EMOJI)
                        for x in range(len(roles_page)):
                            # e.add_field(name="Индекс", value=f"{x + 1}.")
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
                            await message.edit(embed=e, components=[
                                Select(placeholder="Выбери роль, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                                [
                                    Button(emoji=backpageemoji, id=f"shop_3_{page - 1}_backpage")
                                ],
                                [
                                    Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                                ]
                            ])
                        elif page - 1 < 1:
                            await message.edit(embed=e, components=[
                                Select(placeholder="Выбери роль, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                                [
                                    Button(emoji=nextpageemoji, id=f"shop_3_{page + 1}_nextpage")
                                ],
                                [
                                    Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                                ]
                            ])
                        else:
                            await message.edit(embed=e, components=[
                                Select(placeholder="Выбери роль, которую хочешь купить.", options=selects, disabled=True if selects[0].value == "None" else False),
                                [
                                    Button(emoji=backpageemoji, id=f"shop_3_{page - 1}_backpage"),
                                    Button(emoji=nextpageemoji, id=f"shop_3_{page + 1}_nextpage")
                                ],
                                [
                                    Button(emoji="🏠", id='shop_home', style=ButtonStyle.gray)
                                ]
                            ])
                        


def setup(bot):
    bot.add_cog(Selects(bot))