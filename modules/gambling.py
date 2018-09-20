# Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands
import traceback

#Misc. Modules
import datetime
import config as cfg


class GamblingCog:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(GamblingCog(bot))
