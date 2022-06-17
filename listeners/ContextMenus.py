import discord
from discord.ext import commands
import datetime
import asyncio
import time
import random
import os
import re
import sys

from dislash.application_commands.slash_client import InteractionClient
sys.path.append("../../")
import config
from dislash import InteractionClient, Option, OptionType
from paimon import interClient

class ContextMenus(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        


def setup(bot):
    bot.add_cog(ContextMenus(bot))