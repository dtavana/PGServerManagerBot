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


class AdminCog:
    def __init__(self, bot):
        self.bot = bot

    # --------------Cogs Moderations--------------
    @commands.command(hidden=True)
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin", "Admin", "Moderator")
    async def load(self, ctx, *, module):
        """Loads a module"""
        try:
            self.bot.load_extension(f"modules.{module}")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'Loaded module: **{module}**')

    @commands.command(hidden=True)
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin", "Admin", "Moderator")
    async def unload(self, ctx, *, module):
        """Unloads a module"""
        try:
            self.bot.unload_extension(f"modules.{module}")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'Unloaded module: **{module}**')

    @commands.command(hidden=True)
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin", "Admin", "Moderator")
    async def reload(self, ctx, *, module):
        """Reloads a module"""
        try:
            self.bot.unload_extension(f"modules.{module}")
            self.bot.load_extension(f"modules.{module}")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'Reloaded module: **{module}**')


def setup(bot):
    bot.add_cog(AdminCog(bot))
