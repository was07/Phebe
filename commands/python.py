import re
from re import DOTALL, subn

import requests
import disnake
from disnake import Color

import getdoc
from base import Bot, commands, setup  # noqa: F401
from init import Formatted


class Python(commands.Cog):
    """The cog for Python code."""

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
        type(self).__cog_name__ = "Python"

    @commands.command(aliases=["eval"])
    async def e(self, ctx, *, source: str = "") -> None:
        """Runs/evaluates Python code."""

        if ctx.author.id == 883987539961192508:  # 00001H
            await ctx.reply("Sorry, eval is not available **for you.**")
            return

        color: Color
        source = source.strip()
        source = subn(r"(^|\n)``?`?(?:py|)", "\\1", source, DOTALL)[0]
        source = source.strip()
        source = source.strip("`")
        import sandbox

        rs, stdout, stderr = sandbox.run(source)
        if rs is not None:
            color = disnake.Colour.green() if rs == 0 else disnake.Colour.red()
            output = []

            output_limit = 1950
            stdout_truncated = stdout[:output_limit] + (
                "" if len(stdout) < output_limit else "... (output truncated)"
            )
            stderr_truncated = stderr[:output_limit] + (
                "" if len(stderr) < output_limit else "... (output truncated)"
            )

            if stderr:
                output.append(
                    "\n".join(
                        (
                            "_Standard Error_ (" f"{len(stderr)} characters):",
                            f"```\n{stderr_truncated}\n```",
                        )
                    )
                )
            if stdout:
                output.append(
                    "\n".join(
                        (
                            "_Standard Output_ (" f"{len(stdout)} characters):",
                            f"```\n{stdout_truncated}\n```",
                        )
                    )
                )
            outcome = "successfully" if rs == 0 else "unsuccessfully"
            if not stderr and not stdout:
                output.append(
                    f"Program {outcome} completed with exit status {rs} and produced no"
                    + " output."
                )
            else:
                output.append(f"Program {outcome} completed with exit status {rs}.")
            description = "\n".join(output)
        await ctx.reply(
            embed=disnake.Embed(
                title="Output",
                description=description,
                color=color,
            )
        )

    @commands.command(aliases=["doc"])
    async def d(self, ctx, symbol: str = "", nparas: int = 1) -> None:
        """Gets the documentation of a Python object."""

        symbol = symbol.strip("`")
        if symbol == "Creds":
            await ctx.send(
                embed=disnake.Embed(
                    title="Credits",
                    description=(
                        "Made by `Greyblue92`, `Was'` and `Pancake`, `sz_skill`"
                    ),
                )
            )
        elif symbol:
            doc: Formatted
            item, doc, url = getdoc.getdoc(symbol, nparas)
            await ctx.send(
                embed=disnake.Embed(
                    title=symbol,
                    url=url,
                    description=str(doc),
                    color=disnake.Color.blue(),
                )
            )

    @commands.command()
    async def pypi(self, ctx, name=None) -> None:
        """Retrieves information about a PyPI package."""

        if name is None:
            await ctx.send("Package name required.")
            return

        resp = requests.get(f"https://pypi.org/pypi/{name}/json")
        if resp.status_code == 404:
            await ctx.send(embed=disnake.Embed(title=f"Could not find {name}"))
            return

        data = resp.json()
        info = data["info"]
        url = info["project_url"]

        rawdescr = info["description"]
        text = format(rawdescr)
        await ctx.send(
            embed=disnake.Embed(
                title=name,
                url=url,
                description=text,
                color=disnake.Color.blue(),
            )
        )


def format(text, lines=6) -> str:
    """What does this do? I'm not even gonna bother writing a proper docstring for
    this."""

    res = ""
    text = re.compile(r"\s*</?(?:(?!\n[\n\r#]).)*>\s*", re.DOTALL).subn("\n\n", text)[0]
    text = text.replace("```python", "__start_py")
    for line_no, line in enumerate(text.splitlines()):
        line = line.strip()
        if line.startswith("##"):
            res += f"*{line.lstrip('##').strip()}*"
        elif line.startswith("#"):
            res += f"**{line.lstrip('#').strip()}**"
        elif line.startswith(":"):
            res += f"**{line.lstrip(':').strip()}**"
        elif line.startswith("*"):
            res += f'__{line.strip("*").strip()}__'
        elif line.startswith("|"):
            res += f"**{line.lstrip('|').strip()}**"
        elif line.startswith("||"):
            res += f"**{line.lstrip('||').strip()}**"
        elif line.startswith(". ..."):
            res += f"**{line.lstrip('. ...').strip()}**"
        else:
            res += line
        res += "\n"
        if line_no >= lines and "__start_py" in res and "```" not in res:
            res += "```"
            break

    res = res.replace("__start_py", "```py")
    return res.rstrip() + " ..."
