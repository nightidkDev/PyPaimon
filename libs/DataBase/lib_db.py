import sys
import time
import pymongo
sys.path.append("../../")

import config
uri = config.uri
#mongoclient = pymongo.MongoClient(uri)
#db = mongoclient.aimi

class actions():
    def __init__(self):
        pass
    def find(self, db, users=None, count=None, **sort):
        to_return = []
        try:
            if sort:
                for name, pos in sort.items():
                    result = db.find().sort(name, pos)
                if count:
                    for i in range(count):
                        if i < result.count():
                            to_return.append(result[i])
            else:
                for user in users:
                    to_return.append(db.find_one(user))
            return to_return
        except:
            return "ERROR"
        

    def insert(self, db, type_insert="one", args={}):
        try:
            if type_insert == "one":
                db.insert_one(args)
                return "success"
            elif type_insert == "many":
                for arg in args:
                    db.insert_one(arg)
                return "success"
            else:
                return "error type"
        except:
            return "success"

    def update(self, db):
        pass


        
