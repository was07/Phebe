from logging import getLogger

import disnake
from disnake.ext.commands.help import Paginator
from disnake.ext.commands.core import Command

from base import commands, Embed, Bot, setup  # noqa: F401
from init import Config

log = getLogger(__name__)


class PhebeHelpCommand(commands.DefaultHelpCommand):
    """The cog for the help command."""

    def __init__(self, **options) -> None:
        self.clean_prefix = options.pop("prefix")
        self.width = options.pop("width", 80)
        self.indent = options.pop("indent", 2)
        self.sort_commands = options.pop("sort_commands", False)
        self.commands_heading = options.pop("commands_heading", "Commands:")
        self.no_category = options.pop("no_category", "Python")
        self.paginator = options.pop("paginator", Paginator())

        super().__init__(**options)

        self.context.bot = bot  # noqa: F821

    def get_command_signature(self, command) -> None:
        return (
            f"{self.clean_prefix}" f"{command.qualified_name} " f"{command.signature}"
        )

    async def send_bot_help(self, mapping) -> None:
        embed = disnake.Embed(title="Help Panel")

        for cog, cmds in mapping.items():
            cmds = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in cmds]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                txt = ""
                for c in cmds:
                    txt += "\n`" + self.get_command_signature(c) + "`"
                embed.add_field(name=cog_name, value=txt)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog) -> None:
        commands: list[Command] = cog.get_commands()
        print(commands)
        return await super().send_cog_help(cog)

    async def send_command_help(self, command) -> None:
        embed = disnake.Embed(title=self.get_command_signature(command))
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group) -> None:
        commands: list[Command] = group.commands
        print(commands)

        embed = Embed(
            title=group,
        )
        channel = self.get_destination()
        await channel.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        log.info("loading %s cog", type(self).__name__)
        log.info("original help cmd: %s", bot.help_command)
        self._original_help_command = bot.help_command
        new_help_command = PhebeHelpCommand(prefix=Config.prefix)
        log.info("new help cmd: %s", new_help_command)
        bot.help_command = new_help_command
        bot.help_command.cog = self

    def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command
