# Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands
import traceback

#Misc. Modules
import datetime
import config as cfg


class RegistrationCog:
    def __init__(self, bot):
        self.bot = bot

# --------------ID Checks--------------
    async def check_id(self, user: discord.Member):
                # Check if ID exists
        await self.bot.discur.execute('SELECT PlayerUID FROM users WHERE DiscordUser = %s;', (str(user),))
        result = await asyncio.gather(self.bot.discur.fetchone())
        # Check if anything was returned
        if result[0] == None:
            return False
        else:
            return True

    async def get_steamid(self, user: discord.Member):
        await self.bot.discur.execute('SELECT PlayerUID from users WHERE DiscordUser = %s;', (str(user),))
        result = await asyncio.gather(self.bot.discur.fetchone())
        realsteamid = result[0]
        realsteamid = realsteamid.get('PlayerUID')
        return realsteamid

        # --------------Logging--------------
    async def otherlog(self, ctx, user, steamid, admin, type):
        if type == "Registration":
            embed = discord.Embed(
                title=f"{type} Log \U00002705", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(
                name="Data:", value=f"{admin} registered {user.mention} to {steamid}!")
            channel = self.bot.get_channel(488893718125084687)
            await channel.send(embed=embed)

    # --------------Registration--------------
    @commands.command()
    @commands.has_any_role("Owner", "Developer", "Manager", "Head Admin", "Super Admin")
    async def adduser(self, ctx, user: discord.Member, steamid):
        try:
            if(await RegistrationCog.check_id(self, user)):
                result = await RegistrationCog.get_steamid(self, user)
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The DiscordUser: {user.mention} is already registered to {result}!")
                await ctx.send(embed=embed)
            else:
                await self.bot.discur.execute('INSERT INTO users (DiscordUser, PlayerUID) VALUES (%s,%s);', (str(user), steamid))
                if await RegistrationCog.check_id(self, user):
                    embed = discord.Embed(
                        title=f"**Success** \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Data:", value=f"{user.mention} succesfully bound to {steamid}!")
                    await ctx.send(embed=embed)
                    admin = ctx.message.author
                    await RegistrationCog.otherlog(self, ctx, user, steamid, admin, "Registration")
                else:
                    await ctx.send("An error has occured!")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @commands.command()
    @commands.has_any_role("Owner", "Developer", "Manager", "Head Admin", "Super Admin")
    async def edituser(self, ctx, user: discord.Member):
        try:
            if(await RegistrationCog.check_id(self, user)):
                await ctx.send("Please enter the new **STEAM64ID**:")
                message = discord.Message

                def valididcheck(m):
                    if(m.content[:8] == "76561198"):
                        return True
                msg = await self.bot.wait_for('message', check=valididcheck)
                await self.bot.discur.execute('UPDATE users SET PlayerUID = %s WHERE DiscordUser = %s;', (msg.content, str(user)))
                embed = discord.Embed(
                    title=f"**Success** \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Data:", value=f"{user.mention} STEAM64ID updated to {msg.content}!")
                await ctx.send(embed=embed)
                admin = ctx.message.author
                await RegistrationCog.otherlog(self, ctx, user, msg.content, admin, "Registration")
            else:
                await ctx.send(f"The DiscordUser: {user.mention} is not registered.")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')


def setup(bot):
    bot.add_cog(RegistrationCog(bot))
