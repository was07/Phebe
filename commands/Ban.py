from base import *


class Ban(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx: Context, member: Member, reason: str = ''):
        """Ban a User"""
        await member.ban(
            reason=(reason if reason else f"Banned by {ctx.author.display_name} (id={ctx.author.id})")
        )
        await ctx.reply(f"{member.name} got banned." + ('reason: ' + reason if reason else ''))

    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx: Context, *, member=0):
        """Unban a User"""
        class U(disnake.abc.Snowflake):
          def __init__(self,id):self.id=id 
        await ctx.guild.unban(U(int(member)), reason=f"Unbanned by {ctx.author.display_name} (id={ctx.author.id})")
        await ctx.reply(f"{member.name} got unbanned.")
