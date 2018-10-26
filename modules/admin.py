# Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands
import traceback

# Misc. Modules
import datetime
import config as cfg
import os
import git
import io
import textwrap
from contextlib import redirect_stdout


class AdminCog:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    # --------------Cogs Moderations--------------
    @commands.command(hidden=True)
    @commands.has_any_role("Owner", "Developer")
    async def load(self, ctx, *, module):
        """Loads a module"""
        try:
            self.bot.load_extension(f"modules.{module}")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'Loaded module: **{module}**')

    @commands.command(hidden=True)
    @commands.has_any_role("Owner", "Developer")
    async def unload(self, ctx, *, module):
        """Unloads a module"""
        try:
            self.bot.unload_extension(f"modules.{module}")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'Unloaded module: **{module}**')

    @commands.command(hidden=True)
    @commands.has_any_role("Owner", "Developer")
    async def reload(self, ctx, *, module):
        """Reloads a module"""
        try:
            self.bot.unload_extension(f"modules.{module}")
            self.bot.load_extension(f"modules.{module}")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'Reloaded module: **{module}**')

    @commands.command(hidden=True)
    @commands.has_any_role("Owner", "Developer")
    async def gitpull(self, ctx):
        """Pulls Git Repo"""
        repo = git.Repo("C:\\Users\\TwiSt\\Desktop\\Files\\PGServerManagerBot")
        remotes = repo.remotes.origin
        remotes.pull()
        await ctx.send("Success")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']

        await ctx.send("In \U0001f5d2")
        await ctx.send(f'```py\n{body}\n```')

        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send("Out \U0000274c")
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            await ctx.send("Out \u2705")
            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(AdminCog(bot))
