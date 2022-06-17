import io
import json
import time
from PIL import Image, ImageDraw, ImageFont

import pymongo
import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
banner_info = db.banner

def declension(forms, val):
    cases = [ 2, 0, 1, 1, 1, 2 ]
    if val % 100 > 4 and val % 100 < 20:
        return forms[2]
    else:
        if val % 10 < 5:
            return forms[cases[val % 10]]
        else:
            return forms[cases[5]]

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

def counter_ny(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    #st = declension([ 'секунда', 'секунды', 'секунд' ], s)
    #mt = declension([ 'минута', 'минуты', 'минут' ], m)
    #ht = declension([ 'час', 'часа', 'часов' ], h)
    #dt = declension([ 'день', 'дня', 'дней' ], d + 1)

    if seconds >= 86400:
        return f"{d:d}дн. {h:d}ч."
    elif seconds >= 3600:
        return f"{h:0}ч. {m:d}м."
    else:
        return f"{m:d}м."

def image_to_byte_array(image:Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

async def banner_counter(bot):
    with open("./banner_info.json") as f:
        config2 = json.load(f)
    guild = bot.get_guild(604083589570625555)
    info = banner_info.find_one({"id": f"{guild.id}"})
    if info["time"] <= int(time.time()):
        config2["banner_counter_messages"] = 0
        banner_info.update_one({ "id": f"{guild.id}" }, { "$inc": { "time": 86400 }, "$set": { "count_m": 0 } })
    else:
        banner_info.update_one({ "id": f"{guild.id}" }, { "$inc": { "count_m": config2["banner_counter_messages"] } })
        config2["banner_counter_messages"] = 0

    with open("./banner_info.json", "w") as f:
        json.dump(config2, f)

async def banner(bot):
    guild = bot.get_guild(604083589570625555)
    members = list(filter(lambda a: a.bot == False, guild.members))
    voice = list(filter(lambda a: a.voice != None, members))
    info = banner_info.find_one({"id": f"{guild.id}"})
    count_m = info["count_m"]
    im = Image.open('imgs/Banner_genshin_ny.jpg')

    font = ImageFont.truetype('fonts/BalsamiqSans-Bold.ttf', size=55)
    draw_text = ImageDraw.Draw(im)
    draw_text = ImageDraw.Draw(im)
    draw_text.text(
        (150, 480),
        f'{len(members)}',
        font=font,
        fill='#fff')
    draw_text.text(
        (150, 545),
        f'{len(voice)}',
        font=font,
        fill='#fff')
    draw_text.text(
        (150, 610),
        f'{count_m}',
        font=font,
        fill='#fff')        

    im.save('imgs/result.png')
    bytes_im = image_to_byte_array(im)
    await guild.edit(banner=bytes_im)


async def new_year_counter(bot):
    guild = bot.get_guild(604083589570625555)
    channel = guild.get_channel(917715790290116649)
    time_ny = 1640984400
    remaining = time_ny - int(time.time())
    if remaining > 0:
        ny_name = f"До Нового Года: {counter_ny(remaining)}"
    else:
        ny_name = "С Новым Годом!"
    await channel.edit(name=ny_name)
