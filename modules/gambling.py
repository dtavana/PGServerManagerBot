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
        self.openpot = True

    # --------------Logging--------------
    async def gamblelog(self, ctx, amount, type):
        if type == "Jackpot":  
            embed = discord.Embed(
                title=f"{type} Log \U00002705", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(
                name="Data:", value=f"{ctx.author.mention} bet {amount} Coins!")

            channel = self.bot.get_channel(488893718125084687)
            await channel.send(embed=embed)

        if type == "Withdraw":
            embed = discord.Embed(
                title=f"{type} Log \U00002705", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(
                name="Data:", value=f"{ctx.author.mention} withdrew {amount} Coins!")

            channel = self.bot.get_channel(488893718125084687)
            await channel.send(embed=embed)
    
    # ---------Checks--------
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
        realsteamid = realsteamid['PlayerUID']
        # Close Connection
        disconn.close()
        return realsteamid

    # ---------Misc--------
    async def startcountdown(self, ctx):
        import random
        
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)
        await ctx.send("Countdown for the jackpot has started!")
        await asyncio.sleep(15)
        await ctx.send("45 seconds left to join the pot!")
        await asyncio.sleep(15)
        await ctx.send("30 seconds left to join the pot!")
        await asyncio.sleep(15)
        await ctx.send("15 seconds left to join the pot!")
        await asyncio.sleep(10)
        await ctx.send("5 seconds left to join the pot!")
        await asyncio.sleep(5)
        self.openpot = False
        await ctx.send("Jackpot has closed! Picking a winner...")
        await discur.execute('SELECT * FROM jackpot')
        curPot = await asyncio.gather(discur.fetchall())
        tickets = []
        total = 0
        for x in curPot[0]:
            tickets.append(x['TicketEnd'])
            total += x['Amount']              
        winningTicket = random.randint(0, max(tickets))
        await discur.execute('SELECT DiscordUser from jackpot WHERE TicketStart <= %s and TicketEnd >= %s;', (winningTicket, winningTicket))
        winner = await asyncio.gather(discur.fetchone())
        winnerUser = winner[0]['DiscordUser']
        #member = discord.utils.find(lambda m: m.name == winnerUser, channel.guild.members)
        await ctx.send(f"{winnerUser} won {total} coins. Ticket# {winningTicket}")
        await ctx.send(f"Use `pg claim` to claim your rewards!")
        await discur.execute('UPDATE users SET Balance = %s WHERE DiscordUser = %s;', (total, winnerUser))
        await discur.execute('DELETE FROM jackpot')
        self.openpot = True
        disconn.close()

    @commands.command()
    async def claim(self, ctx):
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)
        
        curPlayers = await GamblingCog.currentplayers(self, ctx)
        if await GamblingCog.check_id(self, ctx.author):
            steamid = await GamblingCog.get_steamid(self, ctx.author)
            if (steamid not in curPlayers):
                if await GamblingCog.get_steamid(self, ctx.author):
                    await discur.execute('SELECT Balance FROM users WHERE DiscordUser = %s;', (str(ctx.author),))
                    curBal = await asyncio.gather(discur.fetchone())
                    curBal = curBal[0]['Balance']
                    
                    # Get starting value
                    await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                    original = await asyncio.gather(dzcur.fetchone())

                    # Perform the query
                    await dzcur.execute('UPDATE player_data SET BankCoins = BankCoins + %s WHERE PlayerUID = %s;', (curBal, steamid))

                    # Check if it actually changed
                    await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                    new = await asyncio.gather(dzcur.fetchone())

                    if (new == original):
                        await ctx.send("An error has occured and you have not lost any coins")
                    else:
                        # Perform the query
                        await discur.execute('UPDATE users SET Balance = Balance + %s WHERE DiscordUser = %s;', (curBal, str(ctx.author)))
                        await discur.execute('SELECT Balance FROM users WHERE DiscordUser = %s;', (str(ctx.author),))
                        newBal = await asyncio.gather(discur.fetchone())
                        newBal = newBal[0]['Balance']
                        if (newBal == curBal):
                            await ctx.send("An error has occured and you have not lost any coins")
                        else:
                            embed = discord.Embed(
                                title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                            embed.set_footer(text="PGServerManager | TwiSt#2791")
                            embed.add_field(
                                name="Data:", value=f"{ctx.author.mention} has withdrawn his balance of **{newBal} Coins**!")
                            await ctx.send(embed=embed)
                            await GamblingCog.gamblelog(self, ctx, newBal, "Withdraw")
            else:
                #User was in game
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The STEAM64ID bound to {ctx.author.mention} ({steamid}) is currently in game")
                await ctx.send(embed=embed)
        else:
            #User is not registered
            await ctx.send(f"The DiscordUser: {ctx.author.mention} is not registered. Please create a ticket with your SteamID in the subject!")
        disconn.close()
        dzconn.close()

    @commands.command(aliases=['bet'])
    async def jackpot(self, ctx, amount: int):
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)

        if await GamblingCog.check_id(self, ctx.author):
            steamid = await GamblingCog.get_steamid(self, ctx.author)
            curPlayers = await GamblingCog.currentplayers(self, ctx)
            if (steamid not in curPlayers):
                # Get starting value
                await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                curCoins = await asyncio.gather(dzcur.fetchone())
                curCoins = curCoins[0]['BankCoins']
                # Check if they have enough
                if(curCoins and (curCoins >= amount)):
                    #Check if another user has gone in before going in again
                    await discur.execute('SELECT * FROM jackpot')
                    curPot = await asyncio.gather(discur.fetchall())
                    if self.openpot == False:
                        await ctx.send("The pot currently is not open try again in a minute!")
                        return
                    if(len(curPot[0]) == 1 and (curPot[0][0]['DiscordUser'] == str(ctx.author))):
                        await ctx.send("Wait until another user goes in before going in again")
                        return
                    # Add to pot
                    await discur.execute('INSERT INTO jackpot (DiscordUser, Amount) VALUES (%s,%s);', (str(ctx.author), amount))
                    # Remove coins
                    await dzcur.execute('UPDATE player_data SET BankCoins = BankCoins - %s WHERE PlayerUID = %s;', (amount, steamid))
                    await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                    newCoins = await asyncio.gather(dzcur.fetchone())
                    newCoins = newCoins[0]['BankCoins']
                    if newCoins != curCoins:
                        await discur.execute('SELECT * FROM jackpot')
                        curPot = await asyncio.gather(discur.fetchall())
                        trueTotal = 0
                        curTotal = 0
                        curTicket = 0
                        tickets = []
                        for x in curPot[0]:
                            #Get the players true total
                            if (x['DiscordUser'] == str(ctx.author)):
                                trueTotal += x['Amount']
                            #Get all tickets
                            if(x['TicketEnd']):
                                tickets.append(x['TicketEnd'])
                            else:
                                tickets.append(0)
                            #Get total of all bets
                            curTotal += x['Amount']
                        #Calculate chance of winning
                        chance = (100 * (float(trueTotal) / float(curTotal)))
                        chance = "{0:.2f}".format(chance)
                            
                        #Find the current ticket
                        if (max(tickets) == 0):
                                curTicket = 0
                        else:
                            curTicket += max(tickets)
                            curTicket+=1

                        await discur.execute('UPDATE jackpot SET TicketStart = %s, TicketEnd = %s WHERE DiscordUser = %s;', (curTicket, curTicket + amount, str(ctx.author)))
                        #Start the countdown with 2 players
                        embed = discord.Embed(
                            title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                        embed.set_footer(text="PGServerManager | TwiSt#2791")
                        embed.add_field(
                            name="Data:", value=f"{ctx.author.mention} has entered the jackpot with **{amount} Coins**!")
                        embed.add_field(
                            name="Current Chance:", value=f"{ctx.author.mention} current chance of winning is {chance}%")
                        embed.add_field(
                            name="Tickets:", value=f"Your tickets for this bet are {curTicket} - {curTicket + amount}")
                        await ctx.send(embed=embed)
                        await GamblingCog.gamblelog(self, ctx, amount, "Jackpot")
                        if(len(curPot[0]) == 2):
                            await GamblingCog.startcountdown(self, ctx)
                        else:
                            #Coins didn't change
                            embed = discord.Embed(
                                title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                            embed.set_footer(text="PGServerManager | TwiSt#2791")
                            embed.add_field(
                                name="Error:", value=f"An error has occured and your coins haven't changed!")
                            await ctx.send(embed=embed)
                            #Close the connections
                            dzconn.close()
                            disconn.close()
                            return
                    else:
                        #Not enough Coins
                        embed = discord.Embed(
                            title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                        embed.set_footer(text="PGServerManager | TwiSt#2791")
                        embed.add_field(
                        name="Error:", value=f"You do not have enough BankCoins for this bet!")
                        await ctx.send(embed=embed)
                        #Close the connections
                        dzconn.close()
                        disconn.close()
                        return
            else:
                #User was in game
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The STEAM64ID bound to {ctx.author.mention} ({steamid}) is currently in game")
                await ctx.send(embed=embed)
                #Close the connections
                dzconn.close()
                disconn.close()
                return
        else:
            #User not registed
            embed = discord.Embed(
                title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(
                name="Error:", value=f"The Discord Account {ctx.author.mention} is currently not registered!\n"
                                    f"Please make a ticket as follows : `-new registration INSERTSTEAM64ID`", inline=False)
            await ctx.send(embed=embed)
            #Close the connections
            dzconn.close()
            disconn.close()
            return


def setup(bot):
    bot.add_cog(GamblingCog(bot))
