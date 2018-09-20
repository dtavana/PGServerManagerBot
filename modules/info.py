# Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands
import traceback

#Misc. Modules
import datetime
import config as cfg
import psutil


class InfoCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['statistics'])
    async def stats(self, ctx):
        """Shows the bot's stats"""
        online = (len(set([m for m in self.bot.get_all_members(
        ) if m.status == discord.Status.online and not m.bot])))
        away = (len(set([m for m in self.bot.get_all_members()
                         if m.status == discord.Status.idle and not m.bot])))
        dnd = (len(set([m for m in self.bot.get_all_members()
                        if m.status == discord.Status.dnd and not m.bot])))
        offline = (len(set([m for m in self.bot.get_all_members(
        ) if m.status == discord.Status.offline and not m.bot])))

        p = psutil.Process()

        pre = 'pg '

        memory_percent = psutil.virtual_memory()[2]

        e = discord.Embed(color=discord.Color.dark_blue())
        e.add_field(name="Bot Stats", value=f"**Coder:** <@112762841173368832>\n"
                                            f"**Commands:** {len(self.bot.commands)}\n"
                                            f"**Cogs:** {len(self.bot.cogs)}\n", inline=False)
        e.add_field(name="Discord Stats", value=f"**Prefix:** {pre}\n"
                                                f"**Ping:** {ctx.bot.latency * 1000:,.0f}ms\n"
                                                f"**Guilds:** {len(self.bot.guilds)}\n"
                                                f"**Users:** {len(self.bot.users)}\n"
                                                f"**Version:** 1", inline=False)
        e.add_field(name="PC Stats", value=f"**Memory:** {int(p.memory_info()[0]/1024/1024)}mb ({memory_percent}%)\n"
                    f"**CPU:** {psutil.cpu_percent()}%", inline=False)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(InfoCog(bot))
