import datetime
import discord
from discord.utils import get
import random
from re import S
import time
import asyncio
import sys
import pymongo
import numpy
sys.path.append("../../")
from libs import DataBase
from discord_components import *
import os
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

async def sleeptime(time):
    await asyncio.sleep(int(time))

async def on_select(inter):
    message = inter.message
    userinter = inter.guild.get_member(inter.user.id)
    selectuser = selectdb.find_one({ "message_id": f'{message.id}' })
    if selectuser is None:
        return
    if selectuser["user_id"] != f'{userinter.id}':
        e2 = discord.Embed(title="", description=f"Данные настройки не принадлежат вам.", color=discord.Color(0x2F3136))
        return await interaction.respond(embed=e2)

    if sdb.count_documents({ "id": str(userinter.id), "guild": str(message.guild.id) }) == 0:
        sdb.insert_one({ "id": str(userinter.id), "guild": str(message.guild.id), "command_cheek_marry": 0, "command_kiss_marry": 1, "command_virt_marry": 1, "command_hand_marry": 1, "command_onhands_marry": 1, "command_sleep_marry": 1, "command_dance_marry": 1, "notify_lvl": 1, "notify_transfer": 1, "role_lvl": 1, "deny_all_marry": 1, "selfrooms_inter": 0 })

    userdb = users.find_one({ "disid": str(userinter.id), "guild": str(message.guild.id)  })
    valueinteractiont = inter.values[0]
    interid = get(inter.component.options, value=valueinteractiont)
    valueinteraction = inter.values[0][9:]

    user = sdb.find_one({ "id": str(userinter.id), "guild": str(message.guild.id) })
    e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))

    user[valueinteraction] = 1 if user[valueinteraction] == 0 else 0
    if valueinteraction == "role_lvl":
        ranks = config.ranks
        for rank in ranks:
            if userdb["lvl"] >= rank[0]:
                role_lvl = message.guild.get_role(int(rank[1]))
                member = message.guild.get_member(userinter.id)
                if user[valueinteraction] == 1:
                    if role_lvl not in member.roles:
                        await member.add_roles(role_lvl)
                else:
                    if role_lvl in member.roles:
                        await member.remove_roles(role_lvl)
                break
    sdb.update_one({ "id": str(userinter.id), "guild": str(message.guild.id) }, { "$set": { valueinteraction: user[valueinteraction] } })
    e2 = discord.Embed(title="", description=f"Параметр `{interid.label}. {interid.description}` изменен на `{check_settings(user[valueinteraction])}`", color=discord.Color(0x2F3136))
    try:
        await inter.respond(embed=e2)
    except:
        pass
    selectdb.update_one({ "message_id": selectuser["message_id"] }, { '$set': { "time": int(time.time()) + 20 } })
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
12. Запрет на добавление в личные комнаты: `{check_settings(user['selfrooms_inter'])}`"""

# Старая версия выбора: Для изменения параметра, пропишите: .settings [index]
    e.set_footer(text=f"{userinter.display_name}", icon_url=userinter.avatar_url)
    e.timestamp = datetime.datetime.utcnow()
    await message.edit(
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
