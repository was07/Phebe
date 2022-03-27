from base import *


class Money(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def money(self, ctx):
        await ctx.send("You have freaking money")
