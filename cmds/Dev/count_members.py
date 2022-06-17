import datetime
import pymongo
import os
import discord
import time
import random
import sys
import os
sys.path.append("../../")
import config 
from plugins import funcb
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [["vmembers", vmem, "all", "owner"]]

async def vmem(client, message, command, messageArray, lang_u):

    if str(message.author.id) not in config.ADMINS:
        return

    temp_name = funcb.gen_promo(1, 12)

    f = open(file=f"./temp/{temp_name}.txt", mode='w', encoding="utf-8")

    members = ""

    i = 1

    vcm = message.guild.get_channel(int(messageArray[0])).members

    for x in vcm:
        members += f"""{i}. {x}  |  {x.id}
"""
        i += 1

    # with open(temp_name, "w") as f:
    f.write(members)
    f.close()

    file = discord.File(f"./temp/{temp_name}.txt", filename=f"{temp_name}.txt")

    await message.channel.send(content=f"Кол-во человек в войсе: {len(vcm)}", file=file)

    os.remove(f"./temp/{temp_name}.txt")

    
    


    

