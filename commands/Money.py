from base import *


class Money(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def money(self, ctx):
        """It is indeed confirmed that you do have money."""
        await ctx.send("You have freaking money")
