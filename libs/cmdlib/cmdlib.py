import sys
import time
import pymongo
sys.path.append("../../")

import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
users = db.prof_ec_users

class cooldown():
    @staticmethod
    def setcd(user, name, timeset):
        users.update_one({ "disid": str(user.id), "guild": str(user.guild.id) }, { "$push": { "cooldown": [name, int(time.time()) + timeset] } })

    @staticmethod
    def checkcd(user, name):
        userdb = users.find_one({"disid": f"{user.id}", "guild": f"{user.guild.id}" })
        if len(userdb["cooldown"]) != 0:
            checkcd = False
            timecd = 0
            for x in userdb["cooldown"]:
                namecd, timec = x
                if namecd == name:
                    checkcd = True
                    timecd = timec
                    break
            return { "result": checkcd, "time": timec }
        else:
            return { "result": False, "time": 0 }
        