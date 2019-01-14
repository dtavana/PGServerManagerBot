# Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import traceback

# Misc. Modules
import datetime
import config as cfg


class RegistrationCog:
    def __init__(self, bot):
        self.bot = bot

# --------------ID Checks--------------
    async def check_id(self, user: discord.Member):
        # Open Connection
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)

        # Check if ID exists
        await discur.execute('SELECT PlayerUID FROM users WHERE DiscordID = %s;', (user.id,))
        result = await asyncio.gather(discur.fetchone())
        # Close Connection
        disconn.close()
        # Check if anything was returned
        if result[0] == None:
            return False
        else:
            return True

    async def get_steamid(self, user: discord.Member):
        # Open Connection
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)
        await discur.execute('SELECT PlayerUID from users WHERE DiscordID = %s;', (user.id,))
        result = await asyncio.gather(discur.fetchone())
        realsteamid = result[0]
        realsteamid = realsteamid.get('PlayerUID')
        # Close Connection
        disconn.close()
        return realsteamid

    async def validsteamidcheck(self, ctx, steamid):
        if (steamid[:7] == "7656119" and len(steamid) == 17):
            return True
        else:
            return False

        # --------------Logging--------------
    async def otherlog(self, ctx, user, steamid, admin, type):
        if type == "adduser":
            embed = discord.Embed(
                title=f"{type} Log \U00002705", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(
                name="Data:", value=f"<@{ctx.author.id}> registered {user.mention} to {steamid}")
            channel = self.bot.get_channel(488893718125084687)
            await channel.send(embed=embed)
        if type == "edituser":
            embed = discord.Embed(
                title=f"{type} Log \U00002705", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(
                name="Data:", value=f"<@{ctx.author.id}> updated {user.mention}'s' STEAM64ID to {steamid}")
            channel = self.bot.get_channel(488893718125084687)
            await channel.send(embed=embed)

    # --------------Registration--------------
    '''
	@commands.command()
    async def fix(self, ctx):
        try:
            if(await RegistrationCog.check_id(self, ctx.author)):
                disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
                discur = await disconn.cursor(aiomysql.DictCursor)
                await discur.execute('SELECT DiscordID FROM users WHERE DiscordUser = %s;', (ctx.author.id,))
                result = await asyncio.gather(discur.fetchone())
                if result[0]['DiscordID'] == "0":
                    await discur.execute('UPDATE users SET DiscordID = %s WHERE DiscordUser = %s;', (str(ctx.author.id), ctx.author.id))
                    await ctx.send(f"{ctx.author.mention} the command was succesful")
                else:
                    await ctx.send(f"The DiscordUser: {ctx.author.mention} already ran the command!")
            else:
                await ctx.send(f"The DiscordUser: {ctx.author.mention} is not registered.")
        except:
            await ctx.send(f"{ctx.author.mention}, an error has occured")
        disconn.close()
    '''

    @commands.command()
    @commands.has_any_role("Owner", "Developer", "Manager", "Head Admin", "Super Admin")
    async def adduser(self, ctx, player: discord.Member):
        try:
            if(await RegistrationCog.check_id(self, player)):
                result = await RegistrationCog.get_steamid(self, player)
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The DiscordUser: {player.mention} is already registered to {result}!")
                await ctx.send(embed=embed)
            else:
                await ctx.send("Please enter the new **STEAM64ID**:")

                msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                if(await RegistrationCog.validsteamidcheck(self, ctx, msg.content) != True):
                    # To check if SteamID is valid
                    embed = discord.Embed(
                        title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Error:", value=f"Invalid STEAM64ID of: {msg.content}")
                    await ctx.send(embed=embed)
                    return
                steamid = msg.content

                embed = discord.Embed(
                    title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="**User:**", value=f"{player.mention}")
                embed.add_field(name="**New STEAM64ID:**",
                                value=f"`{steamid}`")
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
                # Open Connection
                disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
                discur = await disconn.cursor(aiomysql.DictCursor)
                await discur.execute('INSERT INTO users (DiscordUser, PlayerUID, DiscordID) VALUES (%s,%s,%s);', (str(player), steamid, player.id))
                disconn.close()
                if await RegistrationCog.check_id(self, player):
                    embed = discord.Embed(
                        title=f"**Success** \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Data:", value=f"{player.mention} succesfully bound to {steamid}")
                    await ctx.send(embed=embed)
                    admin = ctx.message.author
                    await RegistrationCog.otherlog(self, ctx, player, steamid, admin, "adduser")
                else:
                    await ctx.send("An error has occured!")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @commands.command()
    @commands.has_any_role("Owner", "Developer", "Manager", "Head Admin", "Super Admin")
    async def edituser(self, ctx, player: discord.Member):
        try:
            if(await RegistrationCog.check_id(self, player)):
                await ctx.send("Please enter the new **STEAM64ID**:")

                msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                steamid = msg.content
                if(await RegistrationCog.validsteamidcheck(self, ctx, steamid) != True):
                    # To check if SteamID is valid
                    embed = discord.Embed(
                        title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Error:", value=f"Invalid STEAM64ID of: {steamid}")
                    await ctx.send(embed=embed)
                    return

                embed = discord.Embed(
                    title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="**User:**", value=f"`{player.mention}`")
                embed.add_field(name="**New STEAM64ID:**",
                                value=f"`{steamid}`")
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
                # Open Connection
                disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
                discur = await disconn.cursor(aiomysql.DictCursor)
                await discur.execute('UPDATE users SET PlayerUID = %s WHERE DiscordID = %s;', (steamid, player.id))
                embed = discord.Embed(
                    title=f"**Success** \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Data:", value=f"{player.mention} STEAM64ID updated to {steamid}")
                await ctx.send(embed=embed)
                admin = ctx.message.author
                await RegistrationCog.otherlog(self, ctx, player, steamid, admin, "edituser")
            else:
                await ctx.send(f"The DiscordUser: {player.mention} is not registered.")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        # Close Connection
        disconn.close()

    @commands.command()
    @commands.cooldown(1, 300, BucketType.user)
    async def register(self, ctx):
        try:
            disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
            discur = await disconn.cursor(aiomysql.DictCursor)
            if not (await RegistrationCog.check_id(self, ctx.author)):
                await ctx.author.send("Please visit the following link to log in!")
                await ctx.author.send(f"http://144.217.10.151:3000/auth/steam?id={ctx.author.id}")
                await ctx.author.send("You have 5 minutes to visit this link.")
                await discur.execute(f"INSERT INTO authqueue (DiscordID, PlayerUID, Status) VALUES ({ctx.author.id}, 0, 0);")
                endTime = datetime.datetime.now() + datetime.timedelta(minutes=5)
                while datetime.datetime.now() < endTime:
                    await discur.execute(f"SELECT PlayerUID FROM authqueue WHERE DiscordID = {ctx.author.id} AND Status = 1;")
                    data = await asyncio.gather(discur.fetchone())
                    if data[0]:
                        await ctx.author.send("Thank you for registering! You may now use all bot commands.")
                        steamid = data[0]["PlayerUID"]
                        await discur.execute('INSERT INTO users (DiscordUser, PlayerUID, DiscordID) VALUES (%s,%s,%s);', (str(ctx.author), steamid, ctx.author.id))
                        await discur.execute(f"DELETE FROM authqueue WHERE DiscordID = {ctx.author.id};")
                        return
                    else:
                        await asyncio.sleep(1)
                await ctx.author.send("Could not receive any authentication. Please try again.")
                await discur.execute(f"DELETE FROM authqueue WHERE DiscordID = {ctx.author.id};")

            else:
                await ctx.author.send(f"You are already registered")
        except:
            print("geh")
        finally:
            disconn.close()

    @register.error
    async def registration_handler(self, ctx, error):
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"You are on cooldown! Please try again in **{seconds} seconds**")


def setup(bot):
    bot.add_cog(RegistrationCog(bot))
