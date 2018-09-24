# Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands
import traceback

# Misc. Modules
import datetime
import config as cfg


class DBCommandsCog:
    def __init__(self, bot):
        self.bot = bot

    # Error handling
    '''
	async def on_command_error(self, ctx, error):

		# This prevents any commands with local handlers being handled here in on_command_error.
		if hasattr(ctx.command, 'on_error'):
			return
		embed = discord.Embed(title=f"**EXCEPTION** \U0000274c",
		                      colour=discord.Colour(0xf44b42))
		embed.set_footer(text="PGServerManager | TwiSt#2791")
		embed.add_field(name="There was the following exception!",
		                value=f"```{error}```")
		await ctx.send(embed=embed)
		channel = self.bot.get_channel(491104127573557268)
		await channel.send(embed=embed)
	'''

    # --------------Checks--------------
    async def check_id(self, user: discord.Member):

        # Open Connection
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)

        # Check if ID exists
        await discur.execute('SELECT PlayerUID FROM users WHERE DiscordUser = %s;', (str(user),))
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
        await discur.execute('SELECT PlayerUID from users WHERE DiscordUser = %s;', (str(user),))
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

    async def currentplayers(self, ctx):
        import requests
        endpoint = "https://api.battlemetrics.com/servers/2551316?include=identifier"
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6IjZmMzIxY2YwNGFmZmY0MjYiLCJpYXQiOjE1Mzc0MDQyNjQsIm5iZiI6MTUzNzQwNDI2NCwiaXNzIjoiaHR0cHM6Ly93d3cuYmF0dGxlbWV0cmljcy5jb20iLCJzdWIiOiJ1cm46dXNlcjozMzUwIn0.ouuNbm1SrD7YSGIxQf3XHSXvi5IoHgVRsc2PMBcqI2Q"}

        data = requests.get(endpoint, headers=headers).json()

        players = []
        for i in data['included']:
            if i['attributes']['type'] == "steamID":
                players.append(i['attributes']['identifier'])

        return players

    # --------------Logging--------------
    async def amountlog(self, ctx, amount, user, type):
        embed = discord.Embed(
            title=f"{type} Log \U00002705", colour=discord.Colour(0xFFA500))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(
            name="Data:", value=f"{ctx.author.mention} gave {user.mention} {amount} {type}!")

        channel = self.bot.get_channel(488893718125084687)
        await channel.send(embed=embed)

    # --------------Commands--------------
    @commands.command()
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin")
    async def coins(self, ctx, player: discord.Member, amount: int):
        '''
        Changes a player's BankCoins in the Database
        '''
        # Open Connection
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        # Checks to see if user is registered
        if await DBCommandsCog.check_id(self, player):
            steamid = await DBCommandsCog.get_steamid(self, player)
            curPlayers = await DBCommandsCog.currentplayers(self, ctx)
            if(steamid not in curPlayers):
                embed = discord.Embed(
                    title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="**Type:**", value=f"`Coins`")
                embed.add_field(name="**Amount:**", value=f"`{amount}`")
                embed.add_field(name="**STEAM64ID:**", value=f"`{steamid}`")
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
                    dzconn.close()
                    return

                # Get starting value
                await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                original = await asyncio.gather(dzcur.fetchone())

                # Perform the query
                await dzcur.execute('UPDATE player_data SET BankCoins = BankCoins + %s WHERE PlayerUID = %s;', (amount, steamid))

                # Check if it actually changed
                await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                new = await asyncio.gather(dzcur.fetchone())
                if(new == original):
                    await ctx.send("An error has occured! Nothing has been changed. Please fix your syntax")
                else:
                    embed = discord.Embed(
                        title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Data:", value=f"{player.mention} has received **{amount} Coins to Bank**!")
                    embed.add_field(
                        name="Original:", value=f"{player.mention} had **{original[0]['BankCoins']} Coins in Bank**!")
                    embed.add_field(
                        name="New:", value=f"{player.mention} now has **{new[0]['BankCoins']} Coins in Bank**!")
                    await ctx.send(embed=embed)
                    await DBCommandsCog.amountlog(self, ctx, amount, player, "Coins to Bank")
            else:
                # User was in game
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The STEAM64ID bound to {player.mention} ({steamid}) is currently in game")
                await ctx.send(embed=embed)
                dzconn.close()
                return
        else:
            await ctx.send(f"The DiscordUser: {player.mention} is not registered.")

        # Close Connection
        dzconn.close()

    @commands.command()
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin")
    async def xp(self, ctx, player: discord.Member, amount: int):
        # Open Connection
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        if await DBCommandsCog.check_id(self, player):
            steamid = await DBCommandsCog.get_steamid(self, player)
            curPlayers = await DBCommandsCog.currentplayers(self, ctx)
            if (steamid not in curPlayers):

                embed = discord.Embed(
                    title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="**Type:**", value=f"`XP`")
                embed.add_field(name="**Amount:**", value=f"`{amount}`")
                embed.add_field(name="STEAM64ID:", value=f"`{steamid}`")
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
                    dzconn.close()
                    return

                # Get starting value
                await dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
                original = await asyncio.gather(dzcur.fetchone())

                await dzcur.execute('UPDATE xpsystem SET XP = XP + %s WHERE PlayerUID = %s;', (amount, steamid))

                # Check if it actually changed
                await dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
                new = await asyncio.gather(dzcur.fetchone())

                if(new == original):
                    await ctx.send("An error has occured! Nothing has been changed. Please fix your syntax")
                else:
                    embed = discord.Embed(
                        title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Data:", value=f"{player.mention} has received **{amount} XP**!")
                    embed.add_field(
                        name="Original:", value=f"{player.mention} had **{original[0]['XP']} XP**!")
                    embed.add_field(
                        name="New:", value=f"{player.mention} now has **{new[0]['XP']} XP**!")
                    await ctx.send(embed=embed)
                    await DBCommandsCog.amountlog(self, ctx, amount, player, "XP")
            else:
                # User was in game
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The STEAM64ID bound to {player.mention} ({steamid}) is currently in game")
                await ctx.send(embed=embed)
                dzconn.close()
                return
        else:
            await ctx.send(f"The DiscordUser: {user.mention} is not registered. Please create a ticket with your SteamID in the subject!")

        # Close Connection
        dzconn.close()

    @commands.command()
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin")
    async def humanity(self, ctx, player: discord.Member, amount: int):
        # Open Connection
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        if await DBCommandsCog.check_id(self, player):
            steamid = await DBCommandsCog.get_steamid(self, player)
            curPlayers = await DBCommandsCog.currentplayers(self, ctx)
            if (steamid not in curPlayers):
                embed = discord.Embed(
                    title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="**Type:**", value=f"`Humanity`")
                embed.add_field(name="**Amount:**", value=f"`{amount}`")
                embed.add_field(name="**STEAM64ID:**", value=f"`{steamid}`")
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
                    dzconn.close()
                    return

                # Get starting value
                await dzcur.execute('SELECT Humanity FROM character_data WHERE PlayerUID = %s;', (steamid,))
                original = await asyncio.gather(dzcur.fetchone())

                await dzcur.execute('UPDATE character_data SET Humanity = Humanity + %s WHERE PlayerUID = %s;', (amount, steamid))

                # Check if it actually changed
                await dzcur.execute('SELECT Humanity FROM character_data WHERE PlayerUID = %s;', (steamid,))
                new = await asyncio.gather(dzcur.fetchone())

                if(new == original):
                    await ctx.send("An error has occured! Nothing has been changed. Please fix your syntax")
                else:
                    embed = discord.Embed(
                        title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Data:", value=f"{player.mention} has received **{amount} Humanity**!")
                    embed.add_field(
                        name="Original:", value=f"{player.mention} had **{original[0]['Humanity']} Humanity**!")
                    embed.add_field(
                        name="New:", value=f"{player.mention} now has **{new[0]['Humanity']} Humanity**!")
                    await ctx.send(embed=embed)
                    await DBCommandsCog.amountlog(self, ctx, amount, player, "Humanity")
            else:
                # User was in game
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The STEAM64ID bound to {player.mention} ({steamid}) is currently in game")
                await ctx.send(embed=embed)
                dzconn.close()
                return
        else:
            await ctx.send(f"The DiscordUser: {user.mention} is not registered. Please create a ticket with your SteamID in the subject!")

        # Close Connection
        dzconn.close()

    @commands.command()
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin", "Admin", "Moderator")
    async def playerdata(self, ctx, player: str):
        '''
        Gets all of a player's data
        '''
        # Open Connection
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)

        if(await DBCommandsCog.validsteamidcheck(self, ctx, player) != True):
            try:
                newuser = await commands.MemberConverter().convert(ctx, player)
            except:
                await ctx.send(f"Invalid value for user: `{player}` (Must be a **Discord User* or a Valid **STEAM64ID**)")
                dzconn.close()
                disconn.close()
                return

            # Checks to see if user is registered
            if await DBCommandsCog.check_id(self, newuser):
                steamid = await DBCommandsCog.get_steamid(self, newuser)
                # Get the data
                await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                bankData = await asyncio.gather(dzcur.fetchone())
                await dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
                xpData = await asyncio.gather(dzcur.fetchone())
                await dzcur.execute('SELECT Humanity FROM character_data WHERE PlayerUID = %s;', (steamid,))
                humData = await asyncio.gather(dzcur.fetchone())

                if bankData[0] == None and xpData[0] == None and humData[0] == None:
                    bankData = 0
                    xpData = 0
                    humData = 0
                else:
                    bankData = bankData[0]['BankCoins']
                    xpData = xpData[0]['XP']
                    humData = humData[0]['Humanity']

                embed = discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name=f"Player Data:", value=f"**BankCoins**: {bankData}\n"
                                                            f"**XP**: {xpData}\n"
                                                            f"**Humanity**: {humData}\n"
                                                            f"**STEAM64ID**: {steamid}", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"The DiscordUser: {newuser.mention} is not registered.")
        else:
            # User was a SteamID
            steamid = player
            if(await DBCommandsCog.validsteamidcheck(self, ctx, steamid) != True):
                    # To check if SteamID is valid
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"Invalid STEAM64ID of: {msg.steamid}")
                await ctx.send(embed=embed)
                dzconn.close()
                disconn.close()
                return
            await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
            bankData = await asyncio.gather(dzcur.fetchone())
            await dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
            xpData = await asyncio.gather(dzcur.fetchone())
            await dzcur.execute('SELECT Humanity FROM character_data WHERE PlayerUID = %s;', (steamid,))
            humData = await asyncio.gather(dzcur.fetchone())
            if bankData[0] == None and xpData[0] == None and humData[0] == None:
                # Check if there is Bank or XP data
                bankData = 0
                xpData = 0
                humData = 0
            else:
                bankData = bankData[0]['BankCoins']
                xpData = xpData[0]['XP']
                humData = humData[0]['Humanity']

            embed = discord.Embed(
                title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name=f"Player Data:", value=f"**BankCoins**: {bankData}\n"
                                                        f"**XP**: {xpData}\n"
                                                        f"**Humanity**: {humData}\n"
                                                        f"**STEAM64ID**: {steamid}", inline=False)
            await ctx.send(embed=embed)

        # Close Connection
        dzconn.close()

    @commands.command()
    @commands.has_any_role("Owner", "Developer")
    async def customquery(self, ctx, query: str, db: str):
        if db == "dz":
            # Open Connection
            dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
            dzcur = await dzconn.cursor(aiomysql.DictCursor)

            await ctx.send("Are you sure you would like to perform the following? If yes, react with a Thumbs Up. Otherwise, reacting with a Thumbs Down")
            embed = discord.Embed(
                title=f"CustomQueryInfo \U0000270d", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Query:", value=f"`{query}`")
            embed.add_field(name="Database:", value=f"`DayZ DB`")
            message = await ctx.send(embed=embed)
            await message.add_reaction("\U0001f44d")
            await message.add_reaction("\U0001f44e")

            def reactioncheck(reaction, user):
                validreactions = ["\U0001f44d", "\U0001f44e"]
                return user.id == ctx.author.id and reaction.emoji in validreactions
            reaction, user = await self.bot.wait_for('reaction_add', check=reactioncheck)
            # Check if thumbs up
            if reaction.emoji != "\U0001f44d":
                await ctx.send("Command Cancelled")
                dzconn.close()
                disconn.close()
                return
            await dzcur.execute(query)
            await dzconn.commit()
            result = await asyncio.gather(dzcur.fetchall())
            for x in result:
                embed = discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="Data:", value=f"`{x}`")
                await ctx.send(embed=embed)

            # Close Connection
            dzconn.close()

        elif db == "dis":
            await ctx.send("Are you sure you would like to perform the following? If yes, react with a Thumbs Up. Otherwise, reacting with a Thumbs Down")
            embed = discord.Embed(
                title=f"CustomQueryInfo \U0000270d", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Query:", value=f"`{query}`")
            embed.add_field(name="Database:", value=f"`Discord DB`")
            message = await ctx.send(embed=embed)
            await message.add_reaction("\U0001f44d")
            await message.add_reaction("\U0001f44e")

            def reactioncheck(reaction, user):
                validreactions = ["\U0001f44d", "\U0001f44e"]
                return user.id == ctx.author.id and reaction.emoji in validreactions
            reaction, user = await self.bot.wait_for('reaction_add', check=reactioncheck)
            # Check if thumbs up
            if reaction.emoji != "\U0001f44d":
                await ctx.send("Command Cancelled")
                dzconn.close()
                disconn.close()
                return
            # Open Connection
            disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
            discur = await disconn.cursor(aiomysql.DictCursor)
            await discur.execute(query)
            result = await asyncio.gather(discur.fetchall())
            for x in result:
                embed = discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="Data:", value=f"`{x}`")
                await ctx.send(embed=embed)
            # Close Connection
            disconn.close()

    @commands.command()
    async def mydata(self, ctx):
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        # Checks to see if user is registered
        if await DBCommandsCog.check_id(self, ctx.author):
            steamid = await DBCommandsCog.get_steamid(self, ctx.author)
            # Get the data
            await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
            bankData = await asyncio.gather(dzcur.fetchone())
            await dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
            xpData = await asyncio.gather(dzcur.fetchone())
            await dzcur.execute('SELECT Humanity FROM character_data WHERE PlayerUID = %s;', (steamid,))
            humData = await asyncio.gather(dzcur.fetchone())
            await discur.execute('SELECT Balance FROM users WHERE DiscordUser = %s;', (str(ctx.author),))
            balData = await asyncio.gather(discur.fetchone())
            bankData = bankData[0]['BankCoins']
            xpData = xpData[0]['XP']
            humData = humData[0]['Humanity']
            balData = balData[0]['Balance']

            embed = discord.Embed(
                title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name=f"Player Data:", value=f"**BankCoins**: {bankData}\n"
                                                        f"**XP**: {xpData}\n"
                                                        f"**Humanity**: {humData}\n"
                                                        f"**Balance**: {balData}\n"
                                                        f"**STEAM64ID**: {steamid}", inline=False)
            await ctx.author.send(embed=embed)
            dzconn.close()
            disconn.close()
    
    '''
    @commands.command()
    @commands.has_any_role("Owner","Developer")
    async def maintain(self, ctx):
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        yOffset = 153.60
        
        try:
            if await DBCommandsCog.check_id(self, ctx.author):
                steamid = await DBCommandsCog.get_steamid(self, ctx.author)
                #dzcur.execute("""SELECT Worldspace FROM object_data WHERE LOCATE(%s, Worldspace) > 0 AND Classname = 'Plastic_Pole_EP1_DZ';""", (steamid,))
                await dzcur.execute(
                    """SELECT Worldspace FROM object_data WHERE LOCATE(76561198269591338, Worldspace) > 0 AND Classname = 'Plastic_Pole_EP1_DZ';""")
                worldspace = await asyncio.gather(dzcur.fetchone())
                worldspace = worldspace[0]['Worldspace']
                #Get only the coordinates
                worldspace = worldspace.split('"')
                worldspace = worldspace[0]
                #Remove the trailing comma
                worldspace = worldspace[:-1]
                #Replace the brackets
                worldspace = worldspace.replace("[", "")
                worldspace = worldspace.replace("]", "")
                #Put the coordinates in an array
                worldspace = worldspace.split(',')
                xWorldspace = worldspace[1]
                yWorldspace = worldspace[2]
                zWorldspace = worldspace[3]
                #TODO: Convert
                #Find all objects nearby
                xTop = xWorldspace + 50
                xBot = xWorldspace - 50
                yTop = yWorldspace + 50
                yBot = yWorldspace - 50
                zTop = zWorldspace + 50
                zBot = zWorldspace - 50
                dzcur.execute('SELECT ObjectUID FROM object_data WHERE World')
                


                
                print(worldspace)
                print(type(worldspace))

            else:
                #User was not registered
                pass
        except Exception as e:
            dzconn.close()
            disconn.close()
            await ctx.send(f"{e}")
            print("closed")
'''           


def setup(bot):
    bot.add_cog(DBCommandsCog(bot))
