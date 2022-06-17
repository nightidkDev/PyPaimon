from threading import Condition
import discord
import time
import datetime
import sys
import time
from discord_components import component
import pymongo
import sqlite3
sys.path.append("../../")
import config
from libs import Builders
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

async def checkselect(client):
    coll = db.select
    datas = coll.find({})
    for data in datas:
        if data["time"] <= int(time.time()):
            try:
                if data["type"] == "settings_user":
                    guild = client.get_guild(int(data["guild_id"]))
                    channel = guild.get_channel(int(data["channel_id"]))
                    message = await channel.fetch_message(int(data["message_id"]))
                    member = guild.get_member(int(data["user_id"]))
                    user = sdb.find_one({ "id": str(member.id), "guild": str(member.guild.id) })
                    e = discord.Embed(title="", description="", color=discord.Color(0x2F3136))
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
                    e.set_footer(text=f"{member.display_name}", icon_url=member.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.edit(embed=e, components=[])
                    selectdb.delete_one({ "message_id": data["message_id"] })
            except:
                pass