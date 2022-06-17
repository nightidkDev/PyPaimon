import datetime
import pymongo
import os
import discord
from discord_components import *
import time
import random
import sys
sys.path.append("../../")
import config 
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

sdb = db.u_settings
selectdb = db.select
users = db.prof_ec_users

def check_settings(value):
    if value == 0:
        return "❌"
    else:
        return "✅"

def init():
    return [["settings", settings, "flood", "all"]]

async def settings(client, message, command, messageArray, lang_u):
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
        "role_lvl",
        "selfrooms_inter"
        ]

    if len(messageArray) == 0 or messageArray[0] == "":
        if sdb.count_documents({ "id": str(message.author.id), "guild": str(message.guild.id) }) == 0:
            sdb.insert_one({ "id": str(message.author.id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

        user = sdb.find_one({ "id": str(message.author.id), "guild": str(message.guild.id) })
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
12. Запрет на добавление в личные комнаты: `{check_settings(user['selfrooms_inter'])}`""" #Старая версия выбора: Для изменения параметра, пропишите: .settings [index]
        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
        e.timestamp = datetime.datetime.utcnow()
        mes = await message.channel.send(
                embed=e,
                components = [
                    Select(
                        placeholder = "Запросы разрешения для пользователя в браке",
                        options = [
                            SelectOption(label = "1", value = "settings_command_cheek_marry", description=".cheek"),
                            SelectOption(label = "2", value = "settings_command_kiss_marry", description=".kiss"),
                            SelectOption(label = "3", value = "settings_command_virt_marry", description=".virt"),
                            SelectOption(label = "4", value = "settings_command_dance_marry", description=".dance"),
                            SelectOption(label = "5", value = "settings_command_hand_marry", description=".hand"),
                            SelectOption(label = "6", value = "settings_command_onhands_marry", description=".onhands"),
                            SelectOption(label = "7", value = "settings_command_sleep_marry", description=".sleep"),
                        ]
                    ),
                    Select(
                        placeholder = "Остальное",
                        options = [
                            SelectOption(label = "8", value = "settings_deny_all_marry", description="Запрет на все команды, кроме пользователя в браке"),
                            SelectOption(label = "9", value = "settings_notify_lvl", description="Уведомлять в личные сообщения о повышении уровня"),
                            SelectOption(label = "10", value = "settings_notify_transfer", description="Уведомлять в личные сообщения выполненные переводы"),
                            SelectOption(label = "11", value = "settings_role_lvl", description="Выдавать роли за уровни"),
                            SelectOption(label = "12", value = "settings_selfrooms_inter", description="Запрет на добавление в личные комнаты")
                        ]
                    )
                ]
            )
        selectdb.insert_one({ "message_id": f'{mes.id}', "guild_id": f'{mes.guild.id}', "channel_id": f'{mes.channel.id}', "user_id": f'{message.author.id}', "type": "settings_user", "time": int(time.time()) + 30 })
    else:
        try:
            s = int(messageArray[0])
            if s <= 0 or s > len(settings_list):
                e.title="Настройки пользователя"

                e.description = "Параметр не найден."
                e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                e.timestamp = datetime.datetime.utcnow()
            else:
                setting_list = settings_list[s - 1]
                userdb = users.find_one({ "disid": str(message.author.id), "guild": str(message.guild.id) })
                if user[setting_list] == 0:
                    sdb.update_one({ "id": str(message.author.id), "guild": str(message.guild.id) }, { "$set": { setting_list: 1 } })
                    if setting_list == "role_lvl":
                        ranks = config.ranks
                        for rank in ranks:
                            if userdb["lvl"] >= rank[0]:
                                role_lvl = message.author.guild.get_role(int(rank[1]))
                                if role_lvl not in message.author.roles:
                                    await message.author.add_roles(role_lvl)
                                break
                    e.description = f"Параметр изменен на: `✅`"
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                else: 
                    sdb.update_one({ "id": str(message.author.id), "guild": str(message.guild.id) }, { "$set": { setting_list: 0 } })
                    if setting_list == "role_lvl":
                        ranks = config.ranks
                        for rank in ranks:
                            if userdb["lvl"] >= rank[0]:
                                role_lvl = message.author.guild.get_role(int(rank[1]))
                                if role_lvl in message.author.roles:
                                    await message.author.remove_roles(role_lvl)
                                break
                    e.description = f"Параметр изменен на: `❌`"
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
        except:
            e.title="Настройки пользователя"

            e.description = "Параметр не найден."
            e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
            e.timestamp = datetime.datetime.utcnow()


        await message.channel.send(embed=e)