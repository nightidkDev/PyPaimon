import datetime
import pymongo
import os
import discord
import time
import re
import sys
import json
import requests
import io
import string
from PIL import Image, ImageFont, ImageSequence, ImageDraw, ImageOps
import textwrap
sys.path.append("../../")
import config 
from libs import Profile
from plugins import funcb
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

items_db = db.items

def cleanname(name):
    rus = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    for x in list(name):
        if x not in string.printable and x not in rus:
            name = name.replace(x, "?")

    return name

def toFixed(numObj, digits=0):
    return float(f"{numObj:.{digits}f}")

def prepare_mask(size, antialias = 2):
    mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)

def crop(im, s):
    w, h = im.size
    k = w / s[0] - h / s[1]
    if k > 0: im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
    elif k < 0: im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
    return im.resize(s, Image.ANTIALIAS)

def init():
    return [["profile|p|prof", profile().profile, "flood", "all", "help", "информация о пользователе"]]

class profile:
    def __init__(self):
        pass

    async def profile(self, client, message, command, messageArray, lang_u):
        users = db.prof_ec_users
        check = await Profile.Profile().check_member(message.guild, messageArray)
        check_name = await Profile.Profile().check_member_name(message, messageArray)
        temp_name = funcb.gen_promo(1, 9)
        week_stats = db.week_stats
        if week_stats.count_documents({ "id": f"{message.author.id}" }) == 0:
            week_stats.insert_one({ "id": f"{message.author.id}", "chat": 0, "voice": 0 })

        user = message.mentions[0] if len(message.mentions) != 0 else check if check is not None else check_name if check_name is not None else message.author

        if week_stats.count_documents({ "id": f"{user.id}" }) == 0:
            week_stats.insert_one({ "id": f"{user.id}", "chat": 0, "voice": 0 })

        prof = users.find_one({ "disid": str(user.id), "guild": f"{message.guild.id}" })
        exp = int(prof["exp"])
        nexp = int(prof["nexp"])
        level = str(prof["lvl"])
        avatar = str(user.avatar_url_as(format="png", size=1024))
        regex = r'((?:(https?|s?ftp):\/\/)?(?:www\.)?((?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)([A-Z]{2,6})|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(?::(\d{1,5}))?(?:(\/\S+)*))'
        find_urls_in_string = re.compile(regex, re.IGNORECASE)
        url_check = find_urls_in_string.search(avatar)
        if url_check.groups()[5].startswith('/embed'):
            avatar = Image.open('imgs/profile/no_image.png')
        else:
            resp = requests.get(avatar, stream=True)
            #resp.raw.decode_content = True
            try:
                avatar = Image.open(io.BytesIO(resp.content))
            except:
                avatar = Image.open('imgs/profile/no_image.png')


        bgused = prof["background"]

        bgs = db.backgrounds

        bg = bgs.find_one({ "id": bgused })

        imgt = None

        if bg["type"] == "cold":
            # print("cold")
            bgn = f"imgs/profile/background/cold/{bgused}.png"
            color = "#F6FFFF"
            imgt = "cold"
        else:
            # print("hot")
            bgn = f"imgs/profile/background/warm/{bgused}.png"
            color = "#F0ECE3"
            imgt = "hot"
        
        fon = Image.open(bgn)

        if prof["clan"] == "":
            clan_t = "«Отсутствует»"
            img = Image.open(f'imgs/profile/prof_noclan_{imgt}.png')
            clan = ImageFont.truetype('fonts/genshin.ttf', size=46)
        else:
            clans = db.clans
            clan_db = clans.find_one({ "id": int(prof["clan"]) })
            clan_t = clan_db["title"]
            img = Image.open(f'imgs/profile/prof_clan_{imgt}.png')
            if clan_db["id"] == 1:
                clan = ImageFont.truetype('fonts/20703.otf', size=46)
            else:
                clan = ImageFont.truetype('fonts/genshin.ttf', size=46)


        nickname = ImageFont.truetype('fonts/genshin.ttf', size=82)
        status = ImageFont.truetype('fonts/genshin.ttf', size=52)
        xp = ImageFont.truetype('fonts/genshin.ttf', size=32)

        draw_text = ImageDraw.Draw(img)

        name = cleanname(user.name)

        wn = 35
        if len(name) >= 20:
            nickname = ImageFont.truetype('fonts/genshin.ttf', size=45)
            wn = 50
        #if message.author.id == 252378040024301570:
        if user.guild_permissions.administrator and user.id != 554235984070574091:
            icon_A = Image.open('imgs/profile/icons/admin.png')
            fon.paste(icon_A, (498, 54), icon_A)
            draw_text.text(
                (570, wn),
                f'{name}',
                font=nickname,
                fill=color
            )
        else:
            draw_text.text(
                (498, wn),
                f'{name}',
                font=nickname,
                fill=color
            )
        #else:     
        #    draw_text.text(
        #        (498, wn),
        #        f'{name}',
        #        font=nickname,
        #        fill=color
        #    )

        ustatus = cleanname(prof["status"])

        astr = f'''{ustatus if ustatus else "Нет подписи"}'''

        draw_text.text(
            (498, 159),
            astr,
            font=status,
            fill=f"{color if ustatus != '' else '#a0b9d0'}"
        )


        level = prof["lvl"]

        wl, hl = draw_text.textsize(str(level), font=status)

        draw_text.text(
            (1440 - wl, 346),
            f'{level}',
            font=status,
            fill=color
        )



        exp = prof["exp"]
        nexp = prof["nexp"]

        percent = int(int(exp) / int(nexp) * 100)

        if percent > 0:

            len_level_draw = round(873 / 100 * percent) + 566

            draw = ImageDraw.Draw(img)
            draw.line((572, 478, len_level_draw, 478), fill="#5b8d52")
            for i in range(479, 494):
                draw.line((572, i, len_level_draw, i), fill="#c8df6f")
            draw.line((572, 493, len_level_draw, 493), fill="#5b8d52")
            draw.line((571, 478, 571, 493), fill="#5b8d52")
            if percent >= 100:
                draw.line((len_level_draw, 478, len_level_draw, 493), fill="#5b8d52")


        xp_t = f'{exp} / {nexp}'

        w, h = draw_text.textsize(xp_t, font=xp)

        draw_text.text(
            (1440 - w, 432),
            xp_t,
            font=xp,
            fill=color
        )

        week_stats = db.week_stats

        vtarr = [x for x in week_stats.find().sort("voice", -1).limit(100)]
        vtarrid = [x["id"] for x in vtarr]
        try:
            vt = vtarrid.index(f"{user.id}")

            if week_stats.count_documents({ "id": f"{user.id}" }) == 0:
                week_stats.insert_one({ "id": f"{user.id}", "chat": 0, "voice": 0 })
            if user.voice is not None:
                x = int(time.time())
                last = int(prof["last_time"])
                vctime = x - last
                vtarr[vt]["voice"] += vctime

            vtarr.sort(key = lambda x: x["voice"], reverse=True)
            vtarrid = [x["id"] for x in vtarr]
            vt = str(vtarrid.index(f"{user.id}") + 1)
        except:
            vt = "100+"
        
        ct = [x["id"] for x in week_stats.find().sort("chat", -1).limit(100)]
        try:
            ct = str(ct.index(f"{user.id}") + 1)
        except:
            ct = "100+"

        w, h = draw_text.textsize(vt, font=status)

        draw_text.text(
            (1440 - w, 528),
            vt,
            font=status,
            fill=color
        )

        w, h = draw_text.textsize(ct, font=status)

        draw_text.text(
            (1440 - w, 631),
            ct,
            font=status,
            fill=color
        )

        if prof["partner"] == "":
            married = "«Отсутствуют»"
        else:
            married = message.guild.get_member(int(prof["partner"])).name

        w, h = draw_text.textsize(married, font=status)

        draw_text.text( 
            (1440 - w, 729),
            married,
            font=status,
            fill=color
        )

        w, h = draw_text.textsize(clan_t, font=clan)

        draw_text.text(
            ((440+57-w)/2, 489),
            clan_t,
            font=clan,
            fill=color
        )

        size = avatar.size

        size = (256, 256)

        avatar = crop(avatar, size)
        avatar.putalpha(prepare_mask(size, 4))
        fon.paste(avatar, (121, 74), avatar)
        fon.paste(img, (0, 0), img)

        fon = fon.convert("RGB")

        fon.save(f"./profiles/{user.id}_{temp_name}.png")

        name_path = f"./profiles/{user.id}_{temp_name}.png"

        name_file = f"{user.id}_{temp_name}.png"

        file_img = discord.File(name_path, filename=name_file)

        e = discord.Embed(color=discord.Color(0x2F3136))

        e.set_author(name=f"Запрос от {message.author}", icon_url=message.author.avatar_url)
        e.set_footer(text=f"7* - ваше место в топе за 7 дней.")
        e.timestamp = datetime.datetime.utcnow()
        e.set_image(url=f"attachment://{name_file}")

        await message.channel.send(embed=e, file=file_img)

        os.remove(f"./profiles/{name_file}")