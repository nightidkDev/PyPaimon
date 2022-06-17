import asyncio
import sys
sys.path.append("../../")
import config
import string
import random

async def deltime(message, time):
    await asyncio.sleep(int(time))
    await message.delete()

async def sleeptime(time):
    await asyncio.sleep(int(time))

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

def declension(forms, val):
    cases = [ 2, 0, 1, 1, 1, 2 ]
    if val % 100 > 4 and val % 100 < 20:
        return forms[2]
    else:
        if val % 10 < 5:
            return forms[cases[val % 10]]
        else:
            return forms[cases[5]]

async def clear_commands():
    while len(config.commands) != 0:
        config.commands.clear()

def gen_promo(count, len_letters=4):
    letters_and_digits = string.ascii_letters + string.digits
    parts = []
    for i in range(count):
        parts.append(''.join(random.sample(letters_and_digits, len_letters)))
    enter = "-".join(parts)
    return enter

def expbarclan(client, exp, nexp):
    procents = int(int(exp) / int(nexp) * 100)
    empty_bar = ["835230563844751370", "835230598820790362", "835230617427378176"]
    selected = ["835230583453777980", "835230608149184534", "835230625517928510"]
    for x in range(0, len(empty_bar)):
        empty_bar[x] = client.get_emoji(int(empty_bar[x]))
    for x in range(0, len(selected)):
        selected[x] = client.get_emoji(int(selected[x]))
    to_return = ""
    if procents >= 99:
        bar = 20
    elif procents >= 95:
        bar = 19
    elif procents >= 90:
        bar = 18
    elif procents >= 85:
        bar = 17
    elif procents >= 80:
        bar = 16
    elif procents >= 75:
        bar = 15
    elif procents >= 70:
        bar = 14
    elif procents >= 65:
        bar = 13
    elif procents >= 60:
        bar = 12
    elif procents >= 55:
        bar = 11
    elif procents >= 50:
        bar = 10
    elif procents >= 45:
        bar = 9
    elif procents >= 40:
        bar = 8
    elif procents >= 35:
        bar = 7
    elif procents >= 30:
        bar = 6
    elif procents >= 25:
        bar = 5
    elif procents >= 20:
        bar = 4
    elif procents >= 15:
        bar = 3
    elif procents >= 10:
        bar = 2
    elif procents >= 5:
        bar = 1
    else:
        bar = 0
    if bar == 0:
        to_return = f"{empty_bar[0]}"
        for x in range(0, 18):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 1:
        to_return = f"{selected[0]}"
        for x in range(0, 18):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 2:
        to_return = f"{selected[0]}"
        for i in range(0, 1):
            to_return += f"{selected[1]}"
        for x in range(0, 17):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 3:
        to_return = f"{selected[0]}"
        for i in range(0, 2):
            to_return += f"{selected[1]}"
        for x in range(0, 16):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 4:
        to_return = f"{selected[0]}"
        for i in range(0, 3):
            to_return += f"{selected[1]}"
        for x in range(0, 15):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 5:
        to_return = f"{selected[0]}"
        for i in range(0, 4):
            to_return += f"{selected[1]}"
        for x in range(0, 14):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 6:
        to_return = f"{selected[0]}"
        for i in range(0, 5):
            to_return += f"{selected[1]}"
        for x in range(0, 13):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 7:
        to_return = f"{selected[0]}"
        for i in range(0, 6):
            to_return += f"{selected[1]}"
        for x in range(0, 12):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 8:
        to_return = f"{selected[0]}"
        for i in range(0, 7):
            to_return += f"{selected[1]}"
        for x in range(0, 11):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 9:
        to_return = f"{selected[0]}"
        for i in range(0, 8):
            to_return += f"{selected[1]}"
        for x in range(0, 10):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 10:
        to_return = f"{selected[0]}"
        for i in range(0, 9):
            to_return += f"{selected[1]}"
        for x in range(0, 9):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 11:
        to_return = f"{selected[0]}"
        for i in range(0, 10):
            to_return += f"{selected[1]}"
        for x in range(0, 8):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 12:
        to_return = f"{selected[0]}"
        for i in range(0, 11):
            to_return += f"{selected[1]}"
        for x in range(0, 7):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 13:
        to_return = f"{selected[0]}"
        for i in range(0, 12):
            to_return += f"{selected[1]}"
        for x in range(0, 6):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 14:
        to_return = f"{selected[0]}"
        for i in range(0, 13):
            to_return += f"{selected[1]}"
        for x in range(0, 5):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 15:
        to_return = f"{selected[0]}"
        for i in range(0, 14):
            to_return += f"{selected[1]}"
        for x in range(0, 4):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 16:
        to_return = f"{selected[0]}"
        for i in range(0, 15):
            to_return += f"{selected[1]}"
        for x in range(0, 3):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 17:
        to_return = f"{selected[0]}"
        for i in range(0, 16):
            to_return += f"{selected[1]}"
        for x in range(0, 2):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 18:
        to_return = f"{selected[0]}"
        for i in range(0, 17):
            to_return += f"{selected[1]}"
        for x in range(0, 1):
            to_return += f"{empty_bar[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 19:
        to_return = f"{selected[0]}"
        for i in range(0, 18):
            to_return += f"{selected[1]}"
        to_return += f"{empty_bar[2]}"
    elif bar == 20:
        to_return = f"{selected[0]}"
        for i in range(0, 18):
            to_return += f"{selected[1]}"
        to_return += f"{selected[2]}"
    return to_return

def declension(forms, val):
    cases = [ 2, 0, 1, 1, 1, 2 ]
    if val % 100 > 4 and val % 100 < 20:
        return forms[2]
    else:
        if val % 10 < 5:
            return forms[cases[val % 10]]
        else:
            return forms[cases[5]]