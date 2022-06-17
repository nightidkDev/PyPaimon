import datetime
import pymongo
import os
import discord
import time
import random
import sys
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
mutes = db.mutes

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}дн. {h:d}ч. {m:d}м. {s:d}с."
    elif seconds >= 3600:
        return f"{h:d}ч. {m:d}м. {s:d}с."
    elif seconds >= 60:
        return f"{m:d}м. {s:d}с."
    else:
        return f"{s:d}с."

def init():
    return [
        ["timemute|tmute|tm", tmute, "flood", "all"]
    ]



