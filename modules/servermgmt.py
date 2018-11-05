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
import subprocess


class ServerManagementCog:
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_any_role("Owner", "Developer", "Manager", "Head Admin", "Super Admin", "Admin")
    async def viewchernorpt(self, ctx):
        embed = discord.Embed(
            title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name=f"Current RPT:", value=f"It is below")
        await ctx.author.send(embed=embed)
        await ctx.author.send(file=discord.File("C:\\Cherno_Main\\DZE_Server_Config\\arma2oaserver.rpt"))
    
    @commands.command()
    @commands.has_any_role("Owner", "Developer", "Manager", "Head Admin", "Super Admin", "Admin")
    async def restartcherno(self, ctx):
        embed = discord.Embed(
            title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(
            name="Server:", value=f"Are you sure you would like to restart the `Chernarus` server?")
        message = await ctx.send(embed=embed)
        await message.add_reaction("\U0001f44d")
        await message.add_reaction("\U0001f44e")

        def reactioncheck(reaction, user):
            validreactions = ["\U0001f44d", "\U0001f44e"]
            return user.id == ctx.author.id and reaction.emoji in validreactions
        reaction, user = await self.bot.wait_for('reaction_add', check=reactioncheck)
        # Check if thumbs up
        if reaction.emoji != "\U0001f44d":
            await ctx.send("Command cancelled")
            return
        p = subprocess.Popen(
            ['cmd','/c','start C:\\Users\\TwiSt\\Desktop\\Files\\PGServerManagerBot\\forceclosecherno.lnk'])


def setup(bot):
    bot.add_cog(ServerManagementCog(bot))
