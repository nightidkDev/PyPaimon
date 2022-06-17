import datetime
import discord
from discord.ext import commands
import pymongo
import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
clans = db.clans
users = db.prof_ec_users


class ClansCaptches(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user:
            return

        if message.author.bot and str(message.author.id) not in config.BOTS_REWARD:
            return

        x = clans.find_one({ "perks.chat.id": str(message.channel.id) })
        if x:
            perks = x['perks']
            captcha = perks["chat"]["captcha"]
            if captcha["expire"] == 1 or captcha["used"] == 1:
                return
            elif captcha["text"] != message.content:
                return
            elif captcha["count"] == 0:
                return
            else:
                if f"{message.author.id}" not in x["members"]:
                    return
                elif f"{message.author.id}" in captcha["members"] or f"{message.author.id}" in config.captches_def:
                    e = discord.Embed(title="", description=f"Вводить капчу группировки 1 человек может 1 раз.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.reply(embed=e, delete_after=5.0)
                else:
                    user_info = users.find_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" })
                    config.captches_def.append(f"{message.author.id}")
                    ms = user_info["moneystats"]
                    ms["1d"] += captcha["gift"]
                    ms["7d"] += captcha["gift"]
                    ms["14d"] += captcha["gift"]
                    ms["all"] += captcha["gift"]
                    if ms["history_1d"]["captcha"]["view"] == 0:
                        ms["history_1d"]["captcha"]["view"] = 1
                    ms["history_1d"]["captcha"]["count"] += captcha["gift"]
                    if ms["history"]["captcha"]["view"] == 0:
                        ms["history"]["captcha"]["view"] = 1
                    ms["history"]["captcha"]["count"] += captcha["gift"]
                    users.update_one({ "disid": f"{message.author.id}", "guild": f"{message.guild.id}" }, { "$set": { "money": user_info["money"] + captcha["gift"], "moneystats": ms } })
                    if captcha["count"] - 1 == 0:
                        try:
                            message_fetch = await message.channel.fetch_message(int(captcha["message_id"]))
                            await message_fetch.delete()
                        except:
                            pass
                        perks["chat"]["captcha"]["count"] = 0
                        perks["chat"]["captcha"]["members"].append(f"{message.author.id}")
                        perks["chat"]["captcha"]["used"] = 1
                        perks["chat"]["captcha"]["expire"] = 1
                        clans.update_one({ "id": x["id"] }, { "$set": { "perks": perks } })
                        config.captches_def.remove(f"{message.author.id}")
                    else:
                        perks["chat"]["captcha"]["count"] -= 1
                        perks["chat"]["captcha"]["members"].append(f"{message.author.id}")
                        clans.update_one({ "id": x["id"] }, { "$set": { "perks": perks } })
                        config.captches_def.remove(f"{message.author.id}")
                    emoji_gems = self.bot.get_emoji(config.MONEY_EMOJI)
                    e = discord.Embed(title="", description=f"Поздравляю, ты получил {captcha['gift']}{emoji_gems}.", color=discord.Color(0x2F3136))
                    e.set_footer(text=f"{message.author.display_name}", icon_url=message.author.avatar_url)
                    e.timestamp = datetime.datetime.utcnow()
                    await message.reply(embed=e)

def setup(bot):
    bot.add_cog(ClansCaptches(bot))