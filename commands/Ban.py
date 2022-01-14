from base import *


class Ban(commands.Cog):
  def __init__(self, bot: Bot):
    super().__init__()
    self.bot = bot

  @commands.command()
  @commands.has_permissions(ban_members = True)
  async def ban(self, ctx: Context, member: Member):
    """Ban a User"""
    await member.ban(
        reson=f"Banned by {ctx.author.display_name} (id={ctx.author.id})"
    )
  
  @commands.command()
  @commands.has_permissions(ban_members = True)
  async def unban(self, ctx: Context, member: Member):
    """Unban a User"""
    await member.unban(
        reson=f"Unbanned by {ctx.author.display_name} (id={ctx.author.id})"
    )
