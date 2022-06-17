import sys
import time
import pymongo
sys.path.append("../../")

import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

class Builder():
    def __init__(self):
        pass
    async def build(self, client, type_a, add_time, message_s, message, lang_u, pages, c_len):
        arrow_right = client.get_emoji(826567984901390366)
        arrow_left = client.get_emoji(826568061854416946)
        coll = db.reactions
        if type_a == "pages_shop_r":
            await message_s.add_reaction(arrow_right)
            coll.insert_one({"message_id": str(message_s.id), "for_id": str(message.author.id), "time": int(time.time()) + add_time, "guild_id": str(message.guild.id), "channel_id": str(message.channel.id), "lang": str(lang_u), "type": type_a, "page": 1, "pages": pages, "atnowl": 0, "bfnowl": 8, "all_len": c_len })
        elif type_a == "pages_shop_c":
            await message_s.add_reaction(arrow_left)
            await message_s.add_reaction(arrow_right)
            coll.insert_one({"message_id": str(message_s.id), "for_id": str(message.id), "time": int(time.time()) + add_time, "guild_id": str(message.guild.id), "channel_id": str(message_s.channel.id), "lang": str(lang_u), "type": type_a, "page": 1, "pages": c_len, "category": pages })
        elif type_a == "pages_shop_category":
            one = client.get_emoji(826888313448562758)
            two = client.get_emoji(826888462116061234)
            three = client.get_emoji(826888462027194410)
            four = client.get_emoji(826888461994557519)
            five = client.get_emoji(826888461989445672)
            six = client.get_emoji(826888462011203594)
            await message_s.add_reaction(one)
            await message_s.add_reaction(two)
            await message_s.add_reaction(three)
            await message_s.add_reaction(four)
            await message_s.add_reaction(five)
            await message_s.add_reaction(six)
            coll.insert_one({"message_id": str(message_s.id), "for_id": str(message.author.id), "time": int(time.time()) + add_time, "guild_id": str(message.guild.id), "channel_id": str(message.channel.id), "lang": str(lang_u), "type": type_a, "category": 1})
        if type_a == "pages_shop_w":
            await message_s.add_reaction(arrow_right)
            coll.insert_one({"message_id": str(message_s.id), "for_id": str(message.author.id), "time": int(time.time()) + add_time, "guild_id": str(message.guild.id), "channel_id": str(message.channel.id), "lang": str(lang_u), "type": type_a, "page": 1, "pages": pages, "atnowl": 0, "bfnowl": 8, "all_len": c_len })