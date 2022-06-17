import discord
from discord.ext import tasks, commands

class SeasonPass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
def setup(bot):
    bot.add_cog(SeasonPass(bot))