from base import Bot, commands, Context, Member, setup  # noqa: F401


class Ban(commands.Cog):
    """The cog for (un)banning people"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(
        self, ctx: Context, member: Member, *, reason="No reason provided."
    ) -> None:
        """Bans a member."""

        try:
            await member.send(
                f"You got banned from {ctx.guild.name} by {ctx.author} for reason: "
                + reason
            )
        except Exception:
            await ctx.send("Can't send DM to the user")
        finally:
            await member.ban(reason=reason)
            await ctx.send(f"**{member.name}** got banned successfully!")

    @commands.command()
    @commands.has_permissions(
        ban_members=True,
    )
    async def unban(
        self, ctx: Context, member_id: int = 0, *, reason="No reason provided."
    ) -> None:
        """Unbans a member."""
        banned_users = await ctx.guild.bans()

        for ban_entry in banned_users:
            if member_id == ban_entry.user.id:
                await ctx.guild.unban(ban_entry.user)
                await ctx.guild.unban(
                    member_id,
                    reason=(
                        f"Unbanned by {ctx.author.display_name}"
                        + f" (id={ctx.author.id})"
                    ),
                )

                return await ctx.send(
                    f"Member with ID **{member_id}** got unbanned successfully!"
                )
