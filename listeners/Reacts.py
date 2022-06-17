import sqlite3

import discord
from discord.ext import commands
import pymongo
import config
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
server = db.server

from libs import ReactionsOnMessage
from cmds import Economy

class Reacts(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if server.count_documents({"server": f"{message.guild.id}"}) == 0:
            server.insert_one({"server": str(message.guild.id), "roleid_mute": "", "prefix": ".", "lang": "ru", "welcomeMessage": "", "welcomeChannelType": "", "welcomeChannel": "", "startRole": [], "ignoreChannels": [], "modRoles": [], "filter": [], "logsChannel": "", "ignoreCommands": [], "lvlMessage": "Ты получил {level} уровень на сервере {server}!", "lvlChannelType": "dm", "lvlChannel": "" })
        user = payload.member
        emoji = payload.emoji

        if user == self.bot.user:
            return

        if user.bot:
            return

        if message.channel.category is not None:
            if message.channel.category.id == 823234023593213952:
                if message.id == 834737853489217536:
                    con = sqlite3.connect('support.db', check_same_thread=False)
                    cur = con.cursor()
                    if str(emoji.id) == "767745437666115644":
                        create_help = self.bot.get_emoji(767745437666115644)
                        await message.remove_reaction(create_help, user)
                        info = cur.execute(f"SELECT * FROM support WHERE id='{user.id}'").fetchall()
                        if info:
                            return
                        text = await message.guild.create_text_channel(f"{user.name}", category=message.channel.category)
                        everyone = message.guild.get_role(604083589570625555)
                        support_role = message.guild.get_role(823234604550062102)
                        prime_role = message.guild.get_role(827278746205683802)
                        await text.set_permissions(everyone, view_channel=False,
                                                            send_messages=False,
                                                            add_reactions=False)
                        await text.set_permissions(support_role, view_channel=True,
                                                                read_message_history=True)
                        await text.set_permissions(prime_role, view_channel=True,
                                                                read_message_history=True)
                        await text.set_permissions(user, view_channel=True,
                                                        read_messages=True, 
                                                        send_messages=True,
                                                        add_reactions=False,
                                                        read_message_history=True)

                        await text.send(f"<@!{user.id}> <@&{support_role.id}> <@&{prime_role.id}>", delete_after=1.0)

                        e = discord.Embed(title="", description=f"Привет, <@!{user.id}>. Тут ты можешь задавать вопросы по игре, тебе ответят:\n<@&827278746205683802>\n<@&823234604550062102>", color=discord.Color(0x2F3136))
                        support_message = await text.send(embed=e)
                        check_mark = self.bot.get_emoji(824729799900659753)
                        cancel = self.bot.get_emoji(824729100572819537)
                        cur.execute(f"INSERT INTO support VALUES('{user.id}', '{support_message.id}', '{text.id}', NULL, NULL, 0)")
                        con.commit()
                        con.close()
                        #support_db.insert_one({ "id": f"{user.id}", "message_id": f"{support_message.id}", "channel_id": f"{text.id}", "vchannel_id": "", "mod_id": "", "check_close": 0 })
                        await support_message.add_reaction(check_mark)
                        await support_message.add_reaction(cancel)
                else:
                    await ReactionsOnMessage.support_react(self.bot, discord, user, message, emoji, config)


        try:
            await ReactionsOnMessage.react(self.bot, discord, user, message, db, emoji, Economy, config)
        except:
            pass

def setup(bot):
    bot.add_cog(Reacts(bot))