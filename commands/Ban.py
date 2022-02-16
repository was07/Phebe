from base import *


class Ban(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: Context, member: Member, *, reason="No reason provided."):
        """Ban a User"""
        try:
            await member.send(f"You got banned from {ctx.guild.name} by {ctx.author} for reason: {reason}")
        except:
            await ctx.send("Can't send DM to the user")
        finally:
            await member.ban(reason=reason)
            await ctx.send(f"**{member.name}** got banned successfully!")

    @commands.command()
    @commands.has_permissions(ban_members=True, )
    async def unban(self, ctx: Context, member: int = 0, *, reason="No reason provided."):
        """Unban a User"""
        banned_users = await ctx.guild.bans()

        for ban_entry in banned_users:
            if member == ban_entry.user.id:
                ctx.guild.unban(ban_entry.user)
                await ctx.guild.unban(int(member), reason=f"Unbanned by {ctx.author.display_name} (id={ctx.author.id})")
                await ctx.send(f"**{member.name}** got unbanned successfully!")
                return
