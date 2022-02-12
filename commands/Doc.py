from base import *
import getdoc

class Doc(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
   
    @commands.command()
    async def d(self, ctx, symbol: str='', nparas: int=1):
        """Get the Documentation of a python object"""
        symbol = symbol.strip('`')
        if symbol == 'Creds':
            await ctx.send(embed=disnake.Embed(title='Credits',description="Made by `Greyblue92`, `Was'` and `Pancake`, `sz_skill`"))
        elif symbol:
            doc: Formatted
            item, doc, url = getdoc.getdoc(symbol, nparas)
            await ctx.send(embed=disnake.Embed(
                title = symbol,
                url=url,
                description = str(doc),
                color=disnake.Color.blue()
            ))
