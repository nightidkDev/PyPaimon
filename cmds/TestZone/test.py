import datetime
import pymongo
import os
import discord
import time
import random
import sys
from discord_components import *
from discordTogether import DiscordTogether
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

sdb = db.u_settings
selectdb = db.select

def check_settings(value):
    if value == 0:
        return "❌"
    else:
        return "✅"

def init():
    return [
                ["buttons", test().buttons, "all", "owner"],
                ["select", test().select, "all", "owner"],
                ["troles", test().roles, "all", "owner"],
                ["ytplay", test().ytplay, "all", "owner"]
            ]

class test():

    def __init__(self):
        pass

    async def ytplay(self, client, message, command, messageArray, lang_u):
        togetherControl = DiscordTogether(client)
        link = await togetherControl.create_link(message.author.voice.channel.id, 'youtube')
        await message.channel.send(f"Click the blue link!\n{link}")

    async def buttons(self, client, message, command, messageArray, lang_u):
        one = client.get_emoji(826888313448562758)
        two = client.get_emoji(826888462116061234)
        three = client.get_emoji(826888462027194410)
        four = client.get_emoji(826888461994557519)
        five = client.get_emoji(826888461989445672)
        six = client.get_emoji(826888462011203594)
        e = discord.Embed(title=f"Магазин: Именные карточки (категории)", description="", color=discord.Color(0x2F3136))
        e.description = f"""**
1.  Боевой пропуск: 0 

2.  Достижения: 0

3.  Другое: 0

4.  Репутация: 0

5.  События: 0

6.  Персонажи: 0**
""" 
        await message.channel.send(embed=e,
                                  components=[
                                      [
                                        Button(label="", emoji=one, id="1", style=ButtonStyle.blue),
                                        Button(label="", emoji=two, id="2", style=ButtonStyle.red),
                                        Button(label="", emoji=three, id="3", style=ButtonStyle.green)
                                      ],
                                      [
                                        Button(label="", emoji=four, id="4"),
                                        Button(label="5", id="5"),
                                      ]
                                  ]   
                                  )
        #interation = await client.wait_for("button_click", check=lambda x: x.component.id == "click")
        #await interation.respond(content=f"You clicked!")
        

    async def select(self, client, message, command, messageArray, lang_u):
        if sdb.count_documents({ "id": str(message.author.id), "guild": str(message.guild.id) }) == 0:
            sdb.insert_one({ "id": str(message.author.id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

        user = sdb.find_one({ "id": str(message.author.id), "guild": str(message.guild.id) })
        e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
        settings_list = [
            "command_cheek_marry", 
            "command_kiss_marry", 
            "command_virt_marry", 
            "command_dance_marry",
            "command_hand_marry",
            "command_onhands_marry",
            "command_sleep_marry",
            "deny_all_marry", 
            "notify_lvl",
            "notify_transfer", 
            "role_lvl"
        ]
        e.title="Настройки пользователя"

        e.description = f"""**Запросы разрешения для пользователя в браке:**
        
1. `.cheek`: `{check_settings(user['command_cheek_marry'])}`
2. `.kiss`: `{check_settings(user['command_kiss_marry'])}`
3. `.virt`: `{check_settings(user['command_virt_marry'])}`
4. `.dance`: `{check_settings(user['command_dance_marry'])}`
5. `.hand`: `{check_settings(user['command_hand_marry'])}`
6. `.onhands`: `{check_settings(user['command_onhands_marry'])}`
7. `.sleep`: `{check_settings(user['command_sleep_marry'])}`

**Остальное:**

8. Запрет на все команды, кроме пользователя в браке: `{check_settings(user['deny_all_marry'])}`
9. Уведомлять в личные сообщения о повышении уровня: `{check_settings(user['notify_lvl'])}`
10. Уведомлять в личные сообщения выполненные переводы: `{check_settings(user['notify_transfer'])}`
11. Выдавать роли за уровни: `{check_settings(user['role_lvl'])}`

Старая версия выбора: Для изменения параметра, пропишите: .settings [index]"""
        # e.set_footer(text="Для изменения параметра, пропишите: .settings [index]")
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        mes = await message.channel.send(
                embed=e,
                components = [
                    Select(
                        placeholder = "Запросы разрешения для пользователя в браке",
                        options = [
                            SelectOption(label = "1", value = "command_cheek_marry", description=".cheek"),
                            SelectOption(label = "2", value = "command_kiss_marry", description=".kiss"),
                            SelectOption(label = "3", value = "command_virt_marry", description=".virt"),
                            SelectOption(label = "4", value = "command_dance_marry", description=".dance"),
                            SelectOption(label = "5", value = "command_hand_marry", description=".hand"),
                            SelectOption(label = "6", value = "command_onhands_marry", description=".onhands"),
                            SelectOption(label = "7", value = "command_sleep_marry", description=".sleep"),
                        ]
                    ),
                    Select(
                        placeholder = "Остальное",
                        options = [
                            SelectOption(label = "8", value = "deny_all_marry", description="Запрет на все команды, кроме пользователя в браке"),
                            SelectOption(label = "9", value = "notify_lvl", description="Уведомлять в личные сообщения о повышении уровня"),
                            SelectOption(label = "10", value = "notify_transfer", description="Уведомлять в личные сообщения выполненные переводы"),
                            SelectOption(label = "11", value = "role_lvl", description="Выдавать роли за уровни")
                        ]
                    )
                ]
            )
        selectdb.insert_one({ "message_id": f'{mes.id}', "guild_id": f'{mes.guild.id}', "channel_id": f'{mes.channel.id}', "user_id": f'{message.author.id}', "type": "settings_user", "time": int(time.time()) + 15 })

    async def roles(self, client, message, command, messageArray, lang_u):
        user = message.guild.get_member(252378040024301570)
        role1 = message.guild.get_role(789206084505960469)
        role2 = message.guild.get_role(810946599807090718)
        await user.add_roles(*[role1, role2])

