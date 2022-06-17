import sys
import time
import pymongo
sys.path.append("../../")

import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

class Profile():
    def __init__(self):
        pass
    async def check_member(self, guild, text):
        try:
            member = guild.get_member(int(text[0]))
            return member
        except:
            return None

    async def check_member_name(self, message, text):
        name = " ".join(text)
        try:
            member = message.guild.get_member_named(name)
            return member
        except:
            return None

    async def rank(self, lvl):
        ranks = [#[150, "Древнее зло"],
                #[140, "Вершитель судеб"],
                #[130, "Легенда"],
                #[120, "VIP персона"],
                #[110, "Звездный Магистр"],
                [100, "miHoYo Staff"],
                [90, "Архонт"],
                [80, "Hypostasis"],
                [70, "Oceanid"],
                [60, "Кэ-Цин"],
                [50, "Paimon"],
                [40, "Storm Horror"],
                [30, "Agent Fatui"],
                [20, "Mondstadt Scout"],
                [10, "Hilichurl"],
                [5, "Slime"],
                [1, "Авантюрист"]
                ]
        for rank in ranks:
            if lvl >= rank[0]:
                return rank[1]

    async def bar(self, client, theme, exp, nexp):
        coll_bars = db.bars
        procents = int(int(exp) / int(nexp) * 100)
        bar = 0
        empty_bar = ["798078336344784896", "798078351691612160", "798078363973320724"]
        to_return = None
        selected = None
        if procents < 10:
            bar = 0
        elif procents < 20:
            bar = 1
        elif procents < 30:
            bar = 2
        elif procents < 40:
            bar = 3
        elif procents < 50:
            bar = 4
        elif procents < 60:
            bar = 5
        elif procents < 70:
            bar = 6
        elif procents < 80:
            bar = 7
        elif procents < 90:
            bar = 8
        elif procents < 95:
            bar = 9
        elif procents <= 99:
            bar = 10
        bar_db = coll_bars.find({"id": int(theme)})[0]
        selected = bar_db["bar"]
        for x in range(0, len(empty_bar)):
            empty_bar[x] = client.get_emoji(int(empty_bar[x]))
        for x in range(0, len(selected)):
            selected[x] = client.get_emoji(int(selected[x]))
        if bar_db["anim"] == "false":
            if bar == 0:
                to_return = f"{empty_bar[0]}"
                for x in range(0, 8):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 1:
                to_return = f"{selected[0]}"
                for x in range(0, 8):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 2:
                to_return = f"{selected[0]}"
                for i in range(0, 1):
                    to_return += f"{selected[1]}"
                for x in range(0, 7):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 3:
                to_return = f"{selected[0]}"
                for i in range(0, 2):
                    to_return += f"{selected[1]}"
                for x in range(0, 6):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 4:
                to_return = f"{selected[0]}"
                for i in range(0, 3):
                    to_return += f"{selected[1]}"
                for x in range(0, 5):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 5:
                to_return = f"{selected[0]}"
                for i in range(0, 4):
                    to_return += f"{selected[1]}"
                for x in range(0, 4):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 6:
                to_return = f"{selected[0]}"
                for i in range(0, 5):
                    to_return += f"{selected[1]}"
                for x in range(0, 3):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 7:
                to_return = f"{selected[0]}"
                for i in range(0, 6):
                    to_return += f"{selected[1]}"
                for x in range(0, 2):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 8:
                to_return = f"{selected[0]}"
                for i in range(0, 7):
                    to_return += f"{selected[1]}"
                for x in range(0, 1):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 9:
                to_return = f"{selected[0]}"
                for i in range(0, 8):
                    to_return += f"{selected[1]}"
                to_return += f"{empty_bar[2]}"
            else:
                to_return = f"{selected[0]}"
                for i in range(0, 8):
                    to_return += f"{selected[1]}"
                to_return += f"{selected[len(selected) - 1]}"
            return to_return
        else:
            if bar == 0:
                to_return = f"{empty_bar[0]}"
                for x in range(0, 8):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 1:
                to_return = f"{selected[0]}"
                for x in range(0, 8):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 2:
                to_return = f"{selected[0]}"
                for i in range(0, 1):
                    to_return += f"{selected[i + 1]}"
                for x in range(0, 7):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 3:
                to_return = f"{selected[0]}"
                for i in range(0, 2):
                    to_return += f"{selected[i + 1]}"
                for x in range(0, 6):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 4:
                to_return = f"{selected[0]}"
                for i in range(0, 3):
                    to_return += f"{selected[i + 1]}"
                for x in range(0, 5):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 5:
                to_return = f"{selected[0]}"
                for i in range(0, 4):
                    to_return += f"{selected[i + 1]}"
                for x in range(0, 4):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 6:
                to_return = f"{selected[0]}"
                for i in range(0, 5):
                    to_return += f"{selected[i + 1]}"
                for x in range(0, 3):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 7:
                to_return = f"{selected[0]}"
                for i in range(0, 6):
                    to_return += f"{selected[i + 1]}"
                for x in range(0, 2):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 8:
                to_return = f"{selected[0]}"
                for i in range(0, 7):
                    to_return += f"{selected[i + 1]}"
                for x in range(0, 1):
                    to_return += f"{empty_bar[1]}"
                to_return += f"{empty_bar[2]}"
            elif bar == 9:
                to_return = f"{selected[0]}"
                for i in range(0, 8):
                    to_return += f"{selected[i + 1]}"
                to_return += f"{empty_bar[2]}"
            else:
                to_return = f"{selected[0]}"
                for i in range(0, 8):
                    to_return += f"{selected[i + 1]}"
                to_return += f"{selected[len(selected) - 1]}"
            return to_return


