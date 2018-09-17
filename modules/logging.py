#Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands

#Misc. Modules
import datetime
import config as cfg

class LoggingCog:
    def __init__(self, bot):
        self.bot = bot
    
    async def on_amountlog(ctx, amount, user, admin, type):
        embed = discord.Embed(title=f"{type} Log \U00002705", colour=discord.Colour(0xf44b42))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name="Data:", value=f"{admin} gave {user.mention} {amount} {type}!")
        
        channel = self.bot.get_channel(488893718125084687)
        await channel.send(embed=embed)

    async def on_otherlog(ctx, user, steamid, admin, type):
        embed = discord.Embed(title=f"{type} Log \U00002705", colour=discord.Colour(0xf44b42))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name="Data:", value=f"{admin} registered {user.mention} to {steamid}!")
        
        channel = self.bot.get_channel(488893718125084687)
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(LoggingCog(bot))