import disnake
from contextlib import redirect_stderr, redirect_stdout
from disnake import Color
from disnake.ext import commands
from io import StringIO
from re import subn, DOTALL
from tempfile import NamedTemporaryFile
from traceback import print_exc 
from types import CodeType
from typing import Any


class Eval(commands.Cog):
    @commands.command()
    async def e(self, ctx, *, source: str=""):
        """Run and get output of a python code"""
        if ctx.author.id == 883987539961192508:  # 00001H
            await ctx.reply("Sorry, Eval is not available, **for you.**")
            return
        
        result: Any
        code: CodeType
        color: Color 
        source = source.strip()
        source = subn(
          r"(^|\n)``?`?(?:py|)", "\\1",
          source, DOTALL       )[0]
        source = source.strip()
        source = source.strip("`")
        import sandbox
        rs, stdout, stderr = sandbox.run(source)
        if rs is not None:
            color = disnake.Colour.green() if rs == 0 else disnake.Colour.red()
            output = []

            output_limit = 1950
            stdout_truncated = stdout[:output_limit] + ('' if len(stdout) < output_limit else '... (output truncated)')
            stderr_truncated = stderr[:output_limit] + ('' if len(stderr) < output_limit else '... (output truncated)')
          
            if stderr:
                output.append("\n".join((
                  "_Standard Error_ (" 
                  f"{len(stderr)} characters):",
                  f"```\n{stderr_truncated}\n```"
                )))
            if stdout:
                output.append("\n".join((
                  "_Standard Output_ (" 
                  f"{len(stdout)} characters):",
                  f"```\n{stdout_truncated}\n```"
                )))
            outcome = "successfully" if rs == 0 else "unsuccessfully" 
            if not stderr and not stdout:
                output.append(f"Program {outcome} completed with exit status {rs} and produced no output.")
            else:
                output.append(f"Program {outcome} completed with exit status {rs}.")
            description = "\n".join(output)
        await ctx.reply(embed=disnake.Embed(
            title = "Output",
            description=description,
            color=color,
        ))

def setup(bot: commands.Bot):
    bot.add_cog(Eval())