import datetime
import os
import discord
import json
import time
from PIL import Image
import requests
from io import StringIO
import os

"""
def image_to_byte_array(image:Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr
"""

def init():
    return [["say", say().say, "all", "admins"], ["edit", say().edit, "all", "admins"]]

class say:
    def __init__(self):
        pass

    async def say(self, client, message, command, messageArray, lang):
        if message.author.guild_permissions.administrator:
            msg = command[4:]
            try:
                msg22 = ""
                d = json.loads(msg)
                try:
                    msg22 = d["plainText"]
                except:
                    pass
                try:
                    im = d["image"]
                    try:
                        url_image = d["image"]["url"]
                    except:
                        d["image"] = { "url": d["image"] }
                except:
                    pass
                try:
                    thumb = d["thumbnail"]
                    try:
                        url_image = d["thumbnail"]["url"]
                    except:
                        d["thumbnail"] = { "url": d["thumbnail"] }
                except:
                    pass
                try:
                    color_emb = d["color"]
                except:
                    d["color"] = 3092790
                e = discord.Embed.from_dict(d)
                try:
                    attach = d["attachment"]
                    if attach != "":
                        img = Image.open(requests.get(attach, stream=True).raw)
                        img.load()
                        attach_type = img.format.lower()
                        if ((attach_type == "png" or attach_type == "webp") or (attach_type == "jpeg" or attach_type == "jpg")) or attach_type == "gif": 
                            name_file = f"attach_{time.time()}.{img.format.lower()}"
                            name_path = f"temp/attach_{time.time()}.{img.format.lower()}"
                            img.save(name_path)
                            file_img = discord.File(name_path, filename=name_file)
                            os.remove(name_path)
                            if msg22 == "":
                                return await message.channel.send(file=file_img, embed=e)
                            else:
                                return await message.channel.send(file=file_img, content=msg22, embed=e)
                        else:
                            return await message.channel.send("В качестве вложения можно использовать только ссылки на существующие вложения в discord, в формате webp, jpg, jpeg, png и GIF!")
                    else:
                        return await message.channel.send("В качестве вложения можно использовать только ссылки на существующие вложения в discord, в формате webp, jpg, jpeg, png и GIF!")
                except:
                    pass

                if msg22 == "":
                    await message.channel.send(embed=e)
                else:
                    await message.channel.send(content=msg22, embed=e)
            except:
                if lang == "ru":
                    e = discord.Embed(title="Ошибка", description=f":x: Неверный JSON формат!\nИспользуй [embed builder](https://embedbuilder.nadekobot.me/).", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    await message.channel.send(embed=e)
                elif lang == "en":
                    e = discord.Embed(title="Error", description=f":x: Wrong JSON!\nYou can just use [embed builder](https://embedbuilder.nadekobot.me/).", color=discord.Color(0x2F3136))
                    e.timestamp = datetime.datetime.utcnow()
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    await message.channel.send(embed=e)
                return
    async def edit(self, client, message, command, messageArray, lang_u):
        if message.author.guild_permissions.administrator == True:
            if len(messageArray) == 0:
                if lang_u == "ru":
                    return await message.channel.send("Упс.. Не найдены данные, по которым надо найти сообщение.")
                elif lang_u == "en":
                    return await message.channel.send("Oops.. no data was found for which to find the message.")
            if len(messageArray) == 1:
                if lang_u == "ru":
                    return await message.channel.send("Упс.. Не найдены данные, на которые надо изменить сообщение.")
                elif lang_u == "en":
                    return await message.channel.send("Oops.. no data was found to change the message to.")
            message2 = await message.channel.fetch_message(int(messageArray[0]))
            if message2 is None:
                if lang_u == "ru":
                    return await message.channel.send("Не удалось найти данное сообщение.")
                elif lang_u == "en":
                    return await message.channel.send("This message could not be found.")
            if message2.author.id == client.user.id:
                lenm = len(str(messageArray[0])) + 6
                msg = command[lenm:]
                try:
                    msg22 = ""
                    d = json.loads(msg)
                    try:
                        msg22 = d["plainText"]
                    except:
                        pass
                    e = discord.Embed.from_dict(d)
                    if msg22 == "":
                        await message2.edit(embed=e, suppress=False)
                    elif e.to_dict() == {'type': 'rich'}:
                        await message2.edit(content=msg22, suppress=True)
                    else:
                        await message2.edit(content=msg22, embed=e, suppress=False)
                    if lang_u == "ru":
                        await message.channel.send("Сообщение было изменено. (Это сообщение будет удалено через 5 секунд.)", delete_after=5)
                    elif lang_u == "en":
                        await message.channel.send("The message was changed. (This message will be deleted in 5 seconds.)", delete_after=5)
                except:
                    if lang_u == "ru":
                        e = discord.Embed(title="Ошибка", description=f":x: Неверный JSON формат!\nИспользуй [embed builder](https://embedbuilder.nadekobot.me/).", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        await message.channel.send(embed=e)
                    elif lang_u == "en":
                        e = discord.Embed(title="Error", description=f":x: Wrong JSON!\nYou can just use [embed builder](https://embedbuilder.nadekobot.me/).", color=discord.Color(0x2F3136))
                        e.timestamp = datetime.datetime.utcnow()
                        e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                        await message.channel.send(embed=e)
                    return
            else:
                if lang_u == "ru":
                    await message.channel.send("Данное сообщение не принадлежит боту.")
                elif lang_u == "en":
                    await message.channel.send("This message does not belong to the bot.")