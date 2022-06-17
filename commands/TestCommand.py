import discord
from discord.ext import commands
from discord_components import *

class TestCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="test")
    async def test(self, ctx):
        emoji_light = self.bot.get_emoji(767842689923416074)
        emoji_dark = self.bot.get_emoji(767842689407778846)
        e1 = discord.Embed(color=0x2f3136)
        e1.set_image(url="https://cdn.discordapp.com/attachments/768175776506970112/781082217249636438/verification.png")
        e2 = discord.Embed(color=0x2f3136)
        e2.description = f"Для верификации прожмите реакцию на данном сообщении.\n\nЕсли вы нажмёте {emoji_light}, то вам откроется чат для лапового общения.\nЕсли вы нажмёте {emoji_dark}, то вам будет недоступен чат для лампового общения, вам будет выдан доступ в чат с умеренным контролем.\n\nБот выдаст вам роль, которая раскpоет основной контент данного сервера."
        await ctx.send(embed=e1)
        await ctx.send(embed=e2, components=[
            [
                Button(style=ButtonStyle.blue, emoji=emoji_light, id="verify_light"),
                Button(style=ButtonStyle.red, emoji=emoji_dark, id="verify_dark"),
                Button(label="45998 верифицированных", style=ButtonStyle.gray, id="count_verify", disabled=True)
            ]
        ])
        

def setup(bot):
    bot.add_cog(TestCommand(bot))
