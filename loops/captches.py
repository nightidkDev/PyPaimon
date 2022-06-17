import random
import time
import io
import glob
import string
import os
from PIL import Image, ImageDraw, ImageFont

import discord
import pymongo
import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
server_db = db.server
clans = db.clans
users = db.prof_ec_users

def declension(forms, val):
    cases = [ 2, 0, 1, 1, 1, 2 ]
    if val % 100 > 4 and val % 100 < 20:
        return forms[2]
    else:
        if val % 10 < 5:
            return forms[cases[val % 10]]
        else:
            return forms[cases[5]]

def gen_promo(count, len_letters=4):
    letters_and_digits = string.ascii_letters + string.digits
    parts = []
    for i in range(count):
        parts.append(''.join(random.sample(letters_and_digits, len_letters)))
    enter = "-".join(parts)
    return enter

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}д. {h:02d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{h:02d}:{m:02d}:{s:02d}"  

def image_to_byte_array(image:Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

async def captcha1f(bot):
    channel = bot.get_guild(604083589570625555).get_channel(766351044380721202)
    d = None
    
    server_info = server_db.find_one({ "server": "604083589570625555" })
    captcha = server_info["captcha"]
    if (captcha["time"] + 900 > int(time.time()) and captcha["used"] == 1) or (captcha["time"] + captcha["life_time"] < int(time.time()) and captcha["expire"] == 0):
        try:
            message_fetch = await channel.fetch_message(int(captcha["message_id"]))
        except:
            message_fetch = None
        captcha["expire"] = 1
        if message_fetch is not None:
            try:
                await message_fetch.delete()
            except:
                pass
        server_db.update_one({ "server": "604083589570625555" }, { "$set": { "captcha": captcha } })


    if captcha["time"] + 900 < int(time.time()) and captcha["expire"] == 1:
        gen_captcha = gen_promo(1, 6)
        captcha["text"] = gen_captcha
        captcha["time"] = int(time.time())
        captcha["gift"] = random.randint(40, 200)
        captcha["used"] = 0
        captcha["expire"] = 0
        primo = bot.get_emoji(config.MONEY_EMOJI)
        e = discord.Embed(title="", description=f"Введите код в чат.\nНаграда: от 40{primo} до 200{primo}", color=discord.Color(0x2F3136))
        e.set_footer(text="Код доступен в течение 1 минуты.\nКод вводится с учетом регистра.")
        images = glob.glob("codes/*.png")
        im = Image.open(random.choice(images))

        code = list(captcha["text"])
        code = " ".join(code)
        width, height = im.size

        font = ImageFont.truetype('codes/code.otf', size=120)
        draw_text = ImageDraw.Draw(im)

        draw_text.text(
            (265, 1120),
            f'{code}',
            font=font,
            fill='#000001')

        im.save('codes/result/result_code.png')
        file = discord.File("codes/result/result_code.png", filename="result_code.png")
        e.set_image(url="attachment://result_code.png")
        try:
            message_promo = await channel.send(embed=e, file=file)
            captcha["message_id"] = f"{message_promo.id}"
            server_db.update_one({ "server": "604083589570625555" }, { "$set": { "captcha": captcha } })
        except:
            pass

async def captcha2f(bot):
    channel = bot.get_guild(604083589570625555).get_channel(823506887395770368)
    d = None
    server_info = server_db.find_one({ "server": "604083589570625555" })
    captcha = server_info["captcha2"]
    if (captcha["time"] + 900 > int(time.time()) and captcha["used"] == 1) or (captcha["time"] + captcha["life_time"] < int(time.time()) and captcha["expire"] == 0):
        try:
            message_fetch = await channel.fetch_message(int(captcha["message_id"]))
        except:
            message_fetch = None
        captcha["expire"] = 1
        if message_fetch is not None:
            try:
                await message_fetch.delete()
            except:
                pass
        server_db.update_one({ "server": "604083589570625555" }, { "$set": { "captcha2": captcha } })


    if captcha["time"] + 900 < int(time.time()) and captcha["expire"] == 1:
        gen_captcha = gen_promo(1, 6)
        captcha["text"] = gen_captcha
        captcha["time"] = int(time.time())
        captcha["gift"] = random.randint(40, 200)
        captcha["used"] = 0
        captcha["expire"] = 0
        primo = bot.get_emoji(config.MONEY_EMOJI)
        e = discord.Embed(title="", description=f"Введите код в чат.\nНаграда: от 40{primo} до 200{primo}", color=discord.Color(0x2F3136))
        e.set_footer(text="Код доступен в течение 1 минуты.\nКод вводится с учетом регистра.")
        images = glob.glob("codes/*.png")
        im = Image.open(random.choice(images))

        code = list(captcha["text"])
        code = " ".join(code)
        width, height = im.size

        font = ImageFont.truetype('codes/code.otf', size=120)
        draw_text = ImageDraw.Draw(im)

        draw_text.text(
            (265, 1120),
            f'{code}',
            font=font,
            fill='#000001')

        im.save('codes/result/result_code2.png')
        file = discord.File("codes/result/result_code2.png", filename="result_code2.png")
        e.set_image(url="attachment://result_code2.png")
        try:
            message_promo = await channel.send(embed=e, file=file)
            captcha["message_id"] = f"{message_promo.id}"
            server_db.update_one({ "server": "604083589570625555" }, { "$set": { "captcha2": captcha } })
        except:
            pass

async def captcha3f(bot):
    channel = bot.get_guild(604083589570625555).get_channel(832567656254668800)
    d = None
    server_info = server_db.find_one({ "server": "604083589570625555" })
    captcha = server_info["captcha3"]
    if (captcha["time"] + 900 > int(time.time()) and captcha["used"] == 1) or (captcha["time"] + captcha["life_time"] < int(time.time()) and captcha["expire"] == 0):
        try:
            message_fetch = await channel.fetch_message(int(captcha["message_id"]))
        except:
            message_fetch = None
        captcha["expire"] = 1
        if message_fetch is not None:
            try:
                await message_fetch.delete()
            except:
                pass
        server_db.update_one({ "server": "604083589570625555" }, { "$set": { "captcha3": captcha } })


    if captcha["time"] + 900 < int(time.time()) and captcha["expire"] == 1:
        gen_captcha = gen_promo(1, 6)
        captcha["text"] = gen_captcha
        captcha["time"] = int(time.time())
        captcha["gift"] = random.randint(40, 200)
        captcha["used"] = 0
        captcha["expire"] = 0
        primo = bot.get_emoji(config.MONEY_EMOJI)
        e = discord.Embed(title="", description=f"Введите код в чат.\nНаграда: от 40{primo} до 200{primo}", color=discord.Color(0x2F3136))
        e.set_footer(text="Код доступен в течение 1 минуты.\nКод вводится с учетом регистра.")
        images = glob.glob("codes/*.png")
        im = Image.open(random.choice(images))

        code = list(captcha["text"])
        code = " ".join(code)
        width, height = im.size

        font = ImageFont.truetype('codes/code.otf', size=120)
        draw_text = ImageDraw.Draw(im)

        draw_text.text(
            (265, 1120),
            f'{code}',
            font=font,
            fill='#000001')

        im.save('codes/result/result_code3.png')
        file = discord.File("codes/result/result_code3.png", filename="result_code3.png")
        e.set_image(url="attachment://result_code3.png")
        try:
            message_promo = await channel.send(embed=e, file=file)
            captcha["message_id"] = f"{message_promo.id}"
            server_db.update_one({ "server": "604083589570625555" }, { "$set": { "captcha3": captcha } })
        except:
            pass

async def captchajail(bot):
    channel = bot.get_guild(604083589570625555).get_channel(794660897271578625)
    d = None
    server_info = server_db.find_one({ "server": "604083589570625555" })
    captcha = server_info["captcha_jail"]
    if (captcha["time"] + 3600 > int(time.time()) and captcha["used"] == 1) or (captcha["time"] + captcha["life_time"] < int(time.time()) and captcha["expire"] == 0):
        try:
            message_fetch = await channel.fetch_message(int(captcha["message_id"]))
        except:
            message_fetch = None
        captcha["expire"] = 1
        if message_fetch is not None:
            try:
                await message_fetch.delete()
            except:
                pass
        server_db.update_one({ "server": "604083589570625555" }, { "$set": { "captcha_jail": captcha } })


    if captcha["time"] + 3600 < int(time.time()) and captcha["expire"] == 1:
        gen_captcha = gen_promo(1, 7)
        captcha["text"] = gen_captcha
        captcha["time"] = int(time.time())
        captcha["used"] = 0
        captcha["expire"] = 0
        e = discord.Embed(title="", description=f"Введите код в чат.\nНаграда: -1 час от мута.", color=discord.Color(0x2F3136))
        e.set_footer(text="Код доступен в течение 10 секунд.\nКод вводится с учетом регистра.")
        images = glob.glob("codes/*.png")
        im = Image.open(random.choice(images))

        code = list(captcha["text"])
        code = " ".join(code)
        width, height = im.size

        font = ImageFont.truetype('codes/code.otf', size=120)
        draw_text = ImageDraw.Draw(im)

        draw_text.text(
            (230, 1120),
            f'{code}',
            font=font,
            fill='#000001')
        
        im.save('codes/result/result_code_jail.png')
        file = discord.File("codes/result/result_code_jail.png", filename="result_code_jail.png")
        e.set_image(url="attachment://result_code_jail.png")
        try:
            message_promo = await channel.send(embed=e, file=file)
            captcha["message_id"] = f"{message_promo.id}"
            server_db.update_one({ "server": "604083589570625555" }, { "$set": { "captcha_jail": captcha } })
        except:
            pass

async def clan_captcha(bot):
    clans_list = clans.find({})
    for x in clans_list:
        perks = x['perks']
        if perks["chat"]["buy"] == 0:
            continue
        elif perks["chat"]["captcha"]["status"] == 0:
            continue
        elif x["war_status"] == 2 or x["war_status"] == 1:
            continue
        else:
            channel = bot.get_channel(int(perks["chat"]["id"]))
            d = None
            captcha = perks["chat"]["captcha"]
            if (captcha["time"] + 3600 > int(time.time()) and captcha["used"] == 1) or (captcha["time"] + captcha["life_time"] < int(time.time()) and captcha["expire"] == 0):
                try:
                    message_fetch = await channel.fetch_message(int(captcha["message_id"]))
                except:
                    message_fetch = None
                captcha["expire"] = 1
                if message_fetch is not None:
                    try:
                        await message_fetch.delete()
                    except:
                        pass
                perks["chat"]["captcha"] = captcha
                clans.update_one({ "id": x["id"] }, { "$set": { "perks": perks } })


            if captcha["time"] + 3600 < int(time.time()) and captcha["expire"] == 1:
                count_cost = random.randint(500, 1000)
                gen_captcha = gen_promo(1, 6)
                captcha["text"] = gen_captcha
                captcha["time"] = int(time.time())
                captcha["gift"] = count_cost
                captcha["used"] = 0
                captcha["expire"] = 0
                count_members = random.randint(5, 12)
                captcha["count"] = len(x["members"]) if len(x["members"]) <= count_members else count_members
                captcha["members"] = []
                primo = bot.get_emoji(config.MONEY_EMOJI)
                e = discord.Embed(title="", description=f"Введите код в чат.\nНаграда: {count_cost}{primo}\nКоличество использований: {captcha['count']}", color=discord.Color(0x2F3136))
                e.set_footer(text="Код доступен в течение 2 минут.\nКод вводится с учетом регистра.")
                images = glob.glob("codes/*.png")
                im = Image.open(random.choice(images))

                code = list(captcha["text"])
                code = " ".join(code)
                width, height = im.size

                font = ImageFont.truetype('codes/code.otf', size=120)
                draw_text = ImageDraw.Draw(im)

                draw_text.text(
                    (265, 1120),
                    f'{code}',
                    font=font,
                    fill='#000001')

                im.save(f'codes/result/clans/result_code{x["id"]}.png')
                file = discord.File(f'codes/result/clans/result_code{x["id"]}.png', filename=f"result_code{x['id']}.png")
                e.set_image(url=f"attachment://result_code{x['id']}.png")
                try:
                    message_promo = await channel.send(embed=e, file=file)
                    captcha["message_id"] = f"{message_promo.id}"
                    perks["chat"]["captcha"] = captcha
                    clans.update_one({ "id": x["id"] }, { "$set": { "perks": perks } })
                    pass
                except:
                    pass
                os.remove(f'codes/result/clans/result_code{x["id"]}.png')

async def war_captcha_clan(bot):
    clans_list = clans.find({ "war_status": 1 })
    for x in clans_list:
        perks = x["perks"]
        wars = x["war"]
        war = wars["game"]
        turn = war["turn"]
        if turn == "defense":
            try:
                channel = bot.get_channel(int(perks["chat"]["id"]))
            except:
                channel = bot.get_channel(int(x["temp_chat"]))
            d = None
            captcha = war["captcha"]
            if captcha["posted"] == 1:
                if captcha['time'] + captcha["life_time"] < int(time.time()) and captcha["used"] == 0:
                    try:
                        message_fetch = await channel.fetch_message(int(captcha["message_id"]))
                        await message_fetch.delete()
                    except:
                        pass
                    xo = clans.find_one({ "war.id": war["opponent"] })
                    xow = xo["war"]
                    xowg = xow["game"]
                    xowg["result"] = "win"
                    war["result"] = "lose"
                    wars["games"].append(war)
                    xow["games"].append(xowg)
                    
                    # win

                    xow["lastwar"]["date"] = xowg["datetime"]
                    xow["lastwar"]["result"] = "win"
                    xow["lastwar"]["members"] = xowg["members"]
                    xow["lastwar"]["captches"] = xowg["captches"]
                    xow["lastwar"]["money"] = xowg["bet"]
                    xow["wins"] += 1
                    xow["captches"] += xowg["captches"]
                    xow["money"] += xowg["bet"]

                    # lose 

                    wars["lastwar"]["date"] = war["datetime"]
                    wars["lastwar"]["result"] = "lose"
                    wars["lastwar"]["members"] = war["members"]
                    wars["lastwar"]["captches"] = war["captches"]
                    wars["lastwar"]["money"] = -war["bet"]
                    wars["loses"] += 1
                    wars["captches"] += war["captches"]
                    wars["money"] -= war["bet"]

                    clans.update_one({ "id": x["id"] }, { "$set": { "war_status": 0, "war": wars } })
                    clans.update_one({ "war.id": war["opponent"] }, { "$set": { "war_status": 0, "war": xow } })
                    clans.update_one({ "war.id": war["opponent"] }, { "$inc": { "balance": war['bet'] * 2 } })
                    
                    primo = bot.get_emoji(config.MONEY_EMOJI)
                    e = discord.Embed(title="", description=f"Победил клан \"**{xo['title']}**\" и получил {war['bet']}{primo}", color=discord.Colour(0x2f3136))
                    e.set_author(name="Война группировок")
                    istemp1 = False
                    istemp2 = False
                    try:
                        channel1 = bot.get_channel(int(x["perks"]["chat"]["id"]))
                    except:
                        channel1 = bot.get_channel(int(x["temp_chat"]))
                        istemp1 = True
                    try:
                        channel2 = bot.get_channel(int(xo["perks"]["chat"]["id"]))
                    except:
                        channel2 = bot.get_channel(int(x["temp_chat"]))
                        istemp2 = True
                    await channel1.send(embed=e)
                    await channel2.send(embed=e)
                    if istemp1 is True:
                        await channel1.delete()
                    if istemp2 is True:
                        await channel2.delete()
            else:
                count_captcha = captcha["count_captcha"]
                if captcha["life_time"] > 60:
                    gen_captcha = gen_promo(1, count_captcha)
                    captcha["life_time"] = captcha["life_time"] // 2
                elif captcha["life_time"] <= 60 and count_captcha != 8:
                    captcha["count_captcha"] += 1
                    count_captcha = captcha["count_captcha"]
                    gen_captcha = gen_promo(1, count_captcha)
                else:
                    if captcha["life_time"] > 10:
                        captcha["life_time"] -= 10
                    else:
                        captcha["life_time"] -= 1
                    gen_captcha = gen_promo(1, count_captcha)
                
                captcha["text"] = gen_captcha
                captcha["time"] = int(time.time())
                
                captcha["used"] = 0
                e = discord.Embed(title="", description=f"Введите код в чат до того, как закончится время.", color=discord.Color(0x2F3136))
                lf = captcha['life_time']
                if lf >= 60:
                    decl = declension(["минуты", "минут", "минут"], lf // 60)
                    tdecl = f"{lf // 60} {decl}"
                else:
                    decl = declension(["секунды", "секунд", "секунд"], lf)
                    tdecl = f"{lf} {decl}"
                
                e.set_footer(text=f"Код доступен в течение {tdecl}.\nКод вводится с учетом регистра.")
                e.set_author(name="Война группировок")
                images = glob.glob("codes/*.png")
                im = Image.open(random.choice(images))

                code = list(captcha["text"])
                code = "".join(code)
                width, height = im.size

                font = ImageFont.truetype('codes/code.otf', size=80)
                draw_text = ImageDraw.Draw(im)

                img_fraction = 0.50
                fontsize = 1

                while font.getsize(f"{code}")[0] < img_fraction*im.size[0] + 50:
                    fontsize += 1
                    font = ImageFont.truetype('codes/code.otf', size=fontsize)

                draw_text.text(
                    (90, height - 55),
                    f'{code}',
                    font=font,
                    fill='#fce883')

                im.save(f'codes/result/clans/wars/result_code{x["id"]}.png')
                file = discord.File(f'codes/result/clans/wars/result_code{x["id"]}.png', filename=f"result_code{x['id']}.png")
                e.set_image(url=f"attachment://result_code{x['id']}.png")
                message_promo = await channel.send(embed=e, file=file)
                captcha["message_id"] = f"{message_promo.id}"
                captcha["posted"] = 1
                war["captcha"] = captcha
                clans.update_one({ "id": x["id"] }, { "$set": { "war": wars } })
                os.remove(f'codes/result/clans/wars/result_code{x["id"]}.png')