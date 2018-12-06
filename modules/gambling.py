# Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands
import traceback

#Misc. Modules
import datetime
import config as cfg
import typing
import uuid
import random


class GamblingCog:
    def __init__(self, bot):
        self.bot = bot
        self.openpot = True
        self.potstarted = False
        self.curflips = {}

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

    async def createFlipChannel(self, ctx, amount: int):
        try:
            disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
            discur = await disconn.cursor(aiomysql.DictCursor)
            channelToken = str(uuid.uuid4())
            channelToken = channelToken[:channelToken.find('-')]
            category = ctx.guild.get_channel(518926958630010911)
            channelName = f'coinflip-{channelToken}'
            channel = await ctx.guild.create_text_channel(channelName, category=category)
            await discur.execute("INSERT INTO coinflip (DiscordID, ChannelID, Amount) VALUES (%s, %s, %s);", (ctx.author.id, channel.id, amount))
            await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
            await ctx.send(f"You have started a flip in <#{channel.id}>")
            await ctx.send(f"{ctx.author.mention} waiting for 1 other player to join your flip channel.")
            await channel.send(f"This flip is for {amount} Coins.")
        except Exception as e:
            await ctx.send(e)
        finally:
            disconn.close()

    async def getCurFlips(self, ctx, type = False):
        try:
            disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
            discur = await disconn.cursor(aiomysql.DictCursor)
            savedFlips = {}
            await discur.execute('SELECT * FROM coinflip;')
            curFlips = await asyncio.gather(discur.fetchall())
            curFlips = curFlips[0]
            for x in curFlips:
                savedFlips[int (x['ChannelID'])] = [x['Amount'], int(x['DiscordID'])]
            if type:
                channelStrings = []
                for x in ctx.guild.channels:
                    if int(x.id) in savedFlips:
                        channelStrings.append(
                            f"**Channel**: <#{x.id}> | **Amount**: {savedFlips.get(int(x.id))[0]} | **User**: {ctx.guild.get_member(savedFlips.get(int(x.id))[1]).mention}")
                return channelStrings
            else:
                return savedFlips
        except Exception as e:
            await ctx.send(e)
        finally:
            disconn.close()
        
    
    async def addtoflip(self, ctx, channel, amount):
        try:
            disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
            discur = await disconn.cursor(aiomysql.DictCursor)
            await discur.execute('SELECT DiscordID FROM coinflip WHERE ChannelID = %s;', (channel.id,))
            origUser = await asyncio.gather(discur.fetchone())
            origUser = origUser[0]
            origUser = origUser['DiscordID']
            await discur.execute("DELETE FROM coinflip WHERE ChannelID = %s;", (channel.id,))
           
            await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
            await channel.send("Starting coinflip!")
            await channel.send("Calculating winner...")
            await asyncio.sleep(3)

            coin = random.randint(1, 2)
            if coin == 1:
                winner = ctx.guild.get_member(int(origUser))
            else:
                winner = ctx.guild.get_member(ctx.author.id)
            
            await channel.send("And the winner is...")
            await asyncio.sleep(3)
            await channel.send(f"{winner.mention}")
            await channel.send(f"Total Earnings: {amount}")
            await channel.send(f"Use `pg claim ENTERAMOUNT` to claim your rewards!")
            await discur.execute('UPDATE users SET Balance = Balance + %s WHERE DiscordID = %s;', ((amount * 2), winner.id))
            await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (winner.id))
            curBal = await asyncio.gather(discur.fetchone())
            curBal = curBal[0]['Balance']
            await channel.send(f"{winner.mention}'s new balance is **{curBal}**")
            await channel.send("Deleting channel in 30 seconds")
            await winner.send(f"You won your coinflip for {amount} coins!")
            await asyncio.sleep(30)
            await channel.delete()
        except Exception as e:
            await channel.send(e)
        finally:
            disconn.close()

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

    async def bankcheck(self, ctx, steamid):
        try:
            dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
            dzcur = await dzconn.cursor(aiomysql.DictCursor)
            await dzcur.execute('SELECT Perks FROM xpsystem WHERE PlayerUID = %s', (steamid,))
            result = await asyncio.gather(dzcur.fetchone())
            result = result[0]['Perks']
            result = result[1:-1]
            result = result.split(',')
            if ("'UnlimitedBank'" in result):
                return -1
            elif ("'BankLimit20M'" in result):
                return 2
            elif ("'BankLimit10M'" in result):
                return 2
            else:
                return 0

        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
            await ctx.send(e)
            return False
        dzconn.close()

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
        realsteamid = realsteamid['PlayerUID']
        # Close Connection
        disconn.close()
        return realsteamid

    # ---------Misc--------
    async def calcCurPercentages(self, ctx):
        try:
            disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
            discur = await disconn.cursor(aiomysql.DictCursor)

            curBets = {}
            curTotal = 0
            await discur.execute('SELECT DiscordID, Amount FROM jackpot')
            curPot = await asyncio.gather(discur.fetchall())
            for x in curPot[0]:
                curTotal += x['Amount']
                if x['DiscordID'] not in curBets:
                    curBets[x['DiscordID']] = x['Amount']
                else:
                    curBets[x['DiscordID']] += x['Amount']
            curBetsSorted = sorted(curBets, key=curBets.get, reverse=True)
            curBetPercentages = {}
            for i in curBetsSorted:
                curBetPercentages[i] = "{0:.2f}".format(
                    100 * (float(curBets[i]) / float(curTotal)))
            data = ""

            for key, value in curBetPercentages.items():
                try:
                    data += (f"{ctx.guild.get_member(int (key)).mention} |  **{value}%**\n")
                except:
                    data += (f"{key} |  **{value}%**\n")

            embed = discord.Embed(
                title=f"Current Bets \U0001f911", colour=discord.Colour(0xFF00FF))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name=f"Data:",
                            value=data, inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Calculations have failed. Report this to TwiSt")
        finally:
            disconn.close()

    async def startcountdown(self, ctx):
        import random

        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)

        self.potstarted = True

        await ctx.send("Countdown for the jackpot has started!")
        await asyncio.sleep(15)
        await ctx.send("45 seconds left to join the pot!")
        await GamblingCog.calcCurPercentages(self, ctx)
        await asyncio.sleep(15)
        await ctx.send("30 seconds left to join the pot!")
        await GamblingCog.calcCurPercentages(self, ctx)
        await asyncio.sleep(15)
        await ctx.send("15 seconds left to join the pot!")
        await GamblingCog.calcCurPercentages(self, ctx)
        await asyncio.sleep(10)
        await ctx.send("5 seconds left to join the pot!")
        await GamblingCog.calcCurPercentages(self, ctx)
        await asyncio.sleep(5)

        self.openpot = False
        await ctx.send("Jackpot has closed! Picking a winner...")
        await discur.execute('SELECT DiscordID, Amount, BetID FROM jackpot')
        data = await asyncio.gather(discur.fetchall())
        tickets = []
        for x in data[0]:
            await discur.execute('SELECT TicketStart, TicketEnd FROM jackpot')
            ticketsData = await asyncio.gather(discur.fetchall())
            for y in ticketsData[0]:
                tickets.append(y['TicketEnd'])
            player = x['DiscordID']
            amount = x['Amount']
            betid = x['BetID']
            await discur.execute('UPDATE jackpot SET TicketStart = %s, TicketEnd = %s WHERE DiscordID = %s AND BetID = %s;', (max(tickets) + 1, max(tickets) + amount, player, betid))
            tickets = []

        await discur.execute('SELECT * FROM jackpot')
        curPot = await asyncio.gather(discur.fetchall())

        ticketsFin = []
        total = 0
        for x in curPot[0]:
            ticketsFin.append(x['TicketEnd'])
            total += x['Amount']
        winningTicket = random.randint(1, max(ticketsFin) + 1)
        await discur.execute('SELECT DiscordID from jackpot WHERE TicketStart <= %s and TicketEnd >= %s;', (winningTicket, winningTicket))
        winner = await asyncio.gather(discur.fetchone())
        while winner[0] == None:
            winningTicket = random.randint(min(ticketsFin), max(ticketsFin))
            await discur.execute('SELECT DiscordID from jackpot WHERE TicketStart <= %s and TicketEnd >= %s;', (winningTicket, winningTicket))
            winner = await asyncio.gather(discur.fetchone())

        winnerUser = winner[0]['DiscordID']
        winnerMember = ctx.guild.get_member(int(winnerUser))
        if winnerMember == None:
            winnerMember = winnerUser

        await discur.execute('SELECT * FROM jackpot')
        curPot = await asyncio.gather(discur.fetchall())
        winnerTotal = 0
        curTotal = 0
        for x in curPot[0]:
            # Get the players true total
            if (x['DiscordID'] == winnerUser):
                winnerTotal += x['Amount']
            curTotal += x['Amount']

        # Calculate chance of winning
        chance = (100 * (float(winnerTotal) / float(curTotal)))
        chance = "{0:.2f}".format(chance)

        await ctx.send(f"{winnerMember.mention} won **{total}** coins with a **{chance}%** chance. Ticket#**{winningTicket}**")
        await ctx.send(f"Use `pg claim ENTERAMOUNT` to claim your rewards!")
        await discur.execute('UPDATE users SET Balance = Balance + %s WHERE DiscordID = %s;', (total, winnerMember.id))
        await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (winnerMember.id))
        curBal = await asyncio.gather(discur.fetchone())
        curBal = curBal[0]['Balance']
        await ctx.send(f"{winnerMember.mention}'s new balance is **{curBal}**")
        await discur.execute('DELETE FROM jackpot')
        self.openpot = True
        self.potstarted = False
        disconn.close()

    @commands.command(aliases=['coinflip'])
    async def startflip(self, ctx, amount: typing.Union[int, str]):
        try:
            disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
            discur = await disconn.cursor(aiomysql.DictCursor)

            coinflipchanid = 519315014490914816
            channelCheck = self.bot.get_channel(coinflipchanid)
            if (ctx.channel != channelCheck):
                await ctx.send(f"Please run this in <#{coinflipchanid}>")
                return
            
            if await GamblingCog.check_id(self, ctx.author):
                await discur.execute("SELECT COUNT(IF (DiscordID = %s, 1, NULL)) AS numFlips FROM coinflip;", (ctx.author.id,))
                numFlips = await asyncio.gather(discur.fetchone())
                numFlips = numFlips[0]
                numFlips = numFlips['numFlips']
                if numFlips >= 2:
                    await ctx.send(f"{ctx.author.mention} can only have 2 flips at a time!")
                    return
                await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
                curBal = await asyncio.gather(discur.fetchone())
                curBal = curBal[0]['Balance']

                if amount == "max":
                    amount = curBal
                elif curBal >= amount:
                    pass
                else:
                    await ctx.send(f"{ctx.author.mention} does not have enough coins in their balance to start a coinflip of {amount}")
                    return
                
                if amount < 5000:
                    await ctx.send(f"{ctx.author.mention} minimum amount for a coinflip is 5000!")
                    return
                '''
                if amount > 10000000 and amount == "max":
                    amount = 10000000
                elif amount > 10000000:
                    await ctx.send(f"{ctx.author.mention} maximum amount for a coinflip is 10000000!")
                    return
                '''
                
                await GamblingCog.createFlipChannel(self, ctx, amount)
                await discur.execute('UPDATE users SET Balance = Balance - %s WHERE DiscordID = %s;', (amount, ctx.author.id))
                
                await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
                newBal = await asyncio.gather(discur.fetchone())
                newBal = newBal[0]['Balance']
            else:
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The Discord Account {ctx.author.mention} is currently not registered!\n"
                    f"Please make a ticket as follows : `-new registration INSERTSTEAM64ID`", inline=False)
                await ctx.send(embed=embed)
                return

        except Exception as e:
            await ctx.send(e)
        finally:
            disconn.close()
    
    @commands.command()
    async def viewflips(self, ctx):
        try:
            coinflipchanid = 519315014490914816
            channelCheck = self.bot.get_channel(coinflipchanid)
            if (ctx.channel != channelCheck):
                await ctx.send(f"Please run this in <#{coinflipchanid}>")
                return
            
            curFlips = await GamblingCog.getCurFlips(self,ctx,True)
            data = ""
            if curFlips:
                for x in curFlips:
                    data += f"{x}\n"

                embed = discord.Embed(
                    title=f"Current Flips \U0001f911", colour=discord.Colour(0xFF00FF))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name=f"Data:",
                                value=data, inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{ctx.author.mention} there are no active flips")
        except Exception as e:
            await ctx.send(e)
    
    @commands.command()
    async def joinflip(self, ctx, channel: discord.TextChannel):
        try:
            disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
            discur = await disconn.cursor(aiomysql.DictCursor)

            coinflipchanid = 519315014490914816
            channelCheck = self.bot.get_channel(coinflipchanid)
            if (ctx.channel != channelCheck):
                await ctx.send(f"Please run this in <#{coinflipchanid}>")
                return
            
            savedFlips = await GamblingCog.getCurFlips(self, ctx)
            amount = savedFlips.get(channel.id)[0]
            if not savedFlips:
                await ctx.send("No open flips")
                return
            
            curFlips = await GamblingCog.getCurFlips(self, ctx)
            try:
                tempVar = curFlips[channel.id]
            except Exception as e:
                await ctx.send(e)
                await ctx.send("Could not find that flip channel")
                return
            
            if savedFlips.get(channel.id)[1] != ctx.author.id:
                if await GamblingCog.check_id(self, ctx.author):
                    await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
                    curBal = await asyncio.gather(discur.fetchone())
                    curBal = curBal[0]['Balance']

                    if curBal >= amount:
                        await discur.execute('UPDATE users SET Balance = Balance - %s WHERE DiscordID = %s;', (amount, ctx.author.id))
                        await ctx.send(f"Starting flip! Head to <#{channel.id}>")
                        await GamblingCog.addtoflip(self, ctx, channel, amount)
                        return
                    else:
                        await ctx.send(f"{ctx.author.mention} does not have enough in their balance to join the flip!")
                        return
                else:
                    embed = discord.Embed(
                        title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Error:", value=f"The Discord Account {ctx.author.mention} is currently not registered!\n"
                        f"Please make a ticket as follows : `-new registration INSERTSTEAM64ID`", inline=False)
                    await ctx.send(embed=embed)
            else:
                await ctx.send(f"{ctx.author.mention} tried to join <#{channel.id}> which is their own flip!")
        except Exception as e:
            await ctx.send(e)
            await ctx.send("Flip not found.")
        finally:
            disconn.close()
    
    @commands.command()
    async def deposit(self, ctx, amount: typing.Union[int, str]):
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        if await GamblingCog.check_id(self, ctx.author):
            steamid = await GamblingCog.get_steamid(self, ctx.author)
            # Get the users current balance
            await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
            curBal = await asyncio.gather(discur.fetchone())
            curBal = curBal[0]['Balance']
            # Get users current BankCoins
            await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
            original = await asyncio.gather(dzcur.fetchone())
            origCoins = original[0]['BankCoins']

            if (amount == "all"):
                amount = origCoins

            if (amount > origCoins):
                # Check if they have enough
                await ctx.send(f"{ctx.author.mention} does not have enough coins in their bank to add {amount} to their balance")
                dzconn.close()
                disconn.close()
                return

            '''
            if (amount + curBal > 20000000):
                # Over Max Balance
                await ctx.send(f"{ctx.author.mention} can not add {amount} coins it would put their Balance of {curBal} over 20000000")
                dzconn.close()
                disconn.close()
                return
            '''

            curPlayers = await GamblingCog.currentplayers(self, ctx)
            if (steamid not in curPlayers):
                # Update the balance
                await discur.execute('UPDATE users SET Balance = Balance + %s WHERE DiscordID = %s;', (amount, ctx.author.id,))
                await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
                newBal = await asyncio.gather(discur.fetchone())
                newBal = newBal[0]['Balance']

                if (newBal == curBal):
                    await ctx.send(f"An error has occurred. {ctx.author.mention}'s balance has not changed and no coins were lost")
                    dzconn.close()
                    disconn.close()
                    return

                # Update their In Game Coins
                await dzcur.execute('UPDATE player_data SET BankCoins = BankCoins - %s WHERE PlayerUID = %s;', (amount, steamid))

                # Check if it actually changed
                await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                new = await asyncio.gather(dzcur.fetchone())

                if (original == new):
                    await ctx.send(f"An error has occurred. {ctx.author.mention}'s coins have not changed")
                    dzconn.close()
                    disconn.close()
                    return

                embed = discord.Embed(
                    title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Data:", value=f"{ctx.author.mention} has deposited **{amount} Coins** to balance!\n"
                                        f"{ctx.author.mention}'s new balance is {newBal}", inline=False)
                await ctx.send(embed=embed)
                await GamblingCog.gamblelog(self, ctx, newBal, "Withdraw")
                dzconn.close()
                disconn.close()
                return
            else:
                # User was in game
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The STEAM64ID bound to {ctx.author.mention} ({steamid}) is currently in game")
                await ctx.send(embed=embed)
                dzconn.close()
                disconn.close()
                return
        else:
            await ctx.send(f"The DiscordUser: {ctx.author.mention} is not registered. Please create a ticket with your SteamID in the subject!")
            dzconn.close()
            disconn.close()
            return

    @commands.command(aliases=['claim'])
    async def withdraw(self, ctx, amount: typing.Union[int, str]):
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)

        curPlayers = await GamblingCog.currentplayers(self, ctx)
        if await GamblingCog.check_id(self, ctx.author):
            steamid = await GamblingCog.get_steamid(self, ctx.author)
            if (steamid not in curPlayers):
                await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
                curBal = await asyncio.gather(discur.fetchone())
                curBal = curBal[0]['Balance']
                await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                original = await asyncio.gather(dzcur.fetchone())
                origCoins = original[0]['BankCoins']

                if (curBal == 0):
                    await ctx.send(f"{ctx.author.mention}'s current balance is 0!")
                    disconn.close()
                    dzconn.close()
                    return

                if (amount == "all"):
                    amount = curBal

                if (amount > curBal):
                    await ctx.send(f"{ctx.author.mention} can not withdraw {amount} coins as it is over their current balance of {curBal}")
                    dzconn.close()
                    disconn.close()
                    return

                result = await GamblingCog.bankcheck(self, ctx, steamid)
                if (result == 2):
                    if (origCoins + amount > 20000000):
                        await ctx.send(f"{ctx.author.mention} can not claim {amount} coins as it will put their bank over 20,000,000")
                        await ctx.send(f"{ctx.author.mention}'s current BankCoins is {origCoins}")
                        dzconn.close()
                        disconn.close()
                        return
                elif (result == 1):
                    if (origCoins + amount > 10000000):
                        await ctx.send(f"{ctx.author.mention} can not claim {amount} coins as it will put their bank over 10,000,000")
                        await ctx.send(f"{ctx.author.mention}'s current BankCoins is {origCoins}")
                        dzconn.close()
                        disconn.close()
                        return
                elif (result == 0):
                    if (origCoins + amount > 5000000):
                        await ctx.send(f"{ctx.author.mention} can not claim {amount} coins as it will put their bank over 5,000,000")
                        await ctx.send(f"{ctx.author.mention}'s current BankCoins is {origCoins}")
                        dzconn.close()
                        disconn.close()
                        return

                # Perform the query
                await dzcur.execute('UPDATE player_data SET BankCoins = BankCoins + %s WHERE PlayerUID = %s;', (amount, steamid))

                # Check if it actually changed
                await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                new = await asyncio.gather(dzcur.fetchone())
                if (new == original):
                    await ctx.send("An error has occured and you have not lost any coins")
                else:
                    # Perform the query
                    await discur.execute('UPDATE users SET Balance = Balance - %s WHERE DiscordID = %s;', (amount, ctx.author.id,))
                    await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
                    newBal = await asyncio.gather(discur.fetchone())
                    newBal = newBal[0]['Balance']
                    if (newBal == curBal):
                        await ctx.send("An error has occured")
                    else:
                        embed = discord.Embed(
                            title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                        embed.set_footer(text="PGServerManager | TwiSt#2791")
                        embed.add_field(
                            name="Data:", value=f"{ctx.author.mention} has withdrawn **{amount} Coins** from balance!\n"
                                                f"{ctx.author.mention}'s new balance is {newBal}", inline=False)
                        await ctx.send(embed=embed)
                        await GamblingCog.gamblelog(self, ctx, newBal, "Withdraw")
            else:
                # User was in game
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
    async def jackpot(self, ctx, amount: typing.Union[int, str]):
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)

        jackpotchanid = 492488744440561674
        channel = self.bot.get_channel(jackpotchanid)
        if (ctx.channel != channel):
            await ctx.send(f"Please run this in <#{jackpotchanid}>")
            disconn.close()
            return

        await discur.execute('SELECT Amount FROM jackpot WHERE DiscordID = %s;', (ctx.author.id))
        curBets = await asyncio.gather(discur.fetchall())
        curTotal = 0
        for x in curBets[0]:
            # Get the players true total
            curTotal += x['Amount']

        maxBet = 10000000 - curTotal

        if maxBet == 0:
            await ctx.send(f"{ctx.author.mention} can not bet anymore!")
            disconn.close()
            return

        if(type(amount) is int):
            if (amount < 5000):
                await ctx.send(f"{ctx.author.mention} needs to bet at least 5000 coins!")
                disconn.close()
                return

            if(amount > maxBet):
                await ctx.send(f"{ctx.author.mention} can not bet over 10000000 coins in one pot!")
                disconn.close()
                return

        if await GamblingCog.check_id(self, ctx.author):
            steamid = await GamblingCog.get_steamid(self, ctx.author)
            # Get starting value
            await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
            curBal = await asyncio.gather(discur.fetchone())
            curBal = curBal[0]['Balance']
            # Check if they have enough
            if(amount == "max"):
                amount = maxBet
                if(curBal < amount):
                    amount = curBal
            if(curBal and (curBal >= amount)):
                # Check if another user has gone in before going in again
                await discur.execute('SELECT * FROM jackpot')
                curPot = await asyncio.gather(discur.fetchall())
                if self.openpot == False:
                    await ctx.send("The pot currently is not open try again in a minute!")
                    disconn.close()
                    return
                if(len(curPot[0]) == 1 and (curPot[0][0]['DiscordUser'] == str(ctx.author))):
                    await ctx.send("Wait until another user goes in before going in again")
                    disconn.close()
                    return
                await discur.execute('INSERT INTO jackpot (DiscordUser, DiscordID, Amount) VALUES (%s,%s,%s);', (str(ctx.author), ctx.author.id, amount))
                # Remove coins
                await discur.execute('UPDATE users SET Balance = Balance - %s WHERE DiscordID = %s;', (amount, ctx.author.id))
                await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
                newBal = await asyncio.gather(discur.fetchone())
                newBal = newBal[0]['Balance']
                if newBal != curBal:
                    await discur.execute('SELECT * FROM jackpot')
                    curPot = await asyncio.gather(discur.fetchall())
                    trueTotal = 0
                    curTotal = 0
                    for x in curPot[0]:
                        # Get the players true total
                        if (x['DiscordUser'] == str(ctx.author)):
                            trueTotal += x['Amount']
                        # Get total of all bets
                        curTotal += x['Amount']

                    # Calculate chance of winning
                    chance = (100 * (float(trueTotal) / float(curTotal)))
                    chance = "{0:.2f}".format(chance)

                    embed = discord.Embed(
                        title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Data:", value=f"{ctx.author.mention} has entered the jackpot with **{amount} Coins**!")
                    embed.add_field(
                        name="Current Chance:", value=f"{ctx.author.mention} current chance of winning is {chance}%")

                    # embed.add_field(
                    # name="Player:", value=f"{ctx.author.mention}'s current chance of winning is {chance}%")
                    await ctx.send(embed=embed)
                    await GamblingCog.gamblelog(self, ctx, amount, "Jackpot")
                    # Start the countdown with 2 players
                    if(len(curPot[0]) >= 2 and not self.potstarted):
                        await GamblingCog.startcountdown(self, ctx)

                else:
                    # Coins didn't change
                    embed = discord.Embed(
                        title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Error:", value=f"{ctx.author.mention}, an error has occured and your coins haven't changed!")
                    await ctx.send(embed=embed)
                    # Close the connections
                    disconn.close()
                    return
            else:
                # Not enough Coins
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"{ctx.author.mention} does not have enough in their Balance for this bet!")
                await ctx.send(embed=embed)
                # Close the connections
                disconn.close()
                return
        else:
            # User not registed
            embed = discord.Embed(
                title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(
                name="Error:", value=f"The Discord Account {ctx.author.mention} is currently not registered!\n"
                f"Please make a ticket as follows : `-new registration INSERTSTEAM64ID`", inline=False)
            await ctx.send(embed=embed)
            # Close the connections
            disconn.close()
            return
        disconn.close()

    @commands.command(aliases=['wiretransfer'])
    async def transfer(self, ctx, user: discord.Member, amount: int):
        if ctx.author == user:
            await ctx.send(f"{ctx.author.mention} can not transfer to themselves")
            return

        if amount < 1:
            await ctx.send(f"{ctx.author.mention} used an invalid transfer amount of {amount}")
            return

        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)

        if await GamblingCog.check_id(self, ctx.author) and await GamblingCog.check_id(self, user):
            '''
            embed = discord.Embed(
                title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="**Transfer:**", value=f"{user.mention}")
            embed.add_field(name="**Amount:**", value=f"`{amount}`")
            message = await ctx.author.send(embed=embed)
            await message.add_reaction("\U0001f44d")
            await message.add_reaction("\U0001f44e")

            def reactioncheck(reaction, member):
                validreactions = ["\U0001f44d", "\U0001f44e"]
                return member.id == ctx.author.id and reaction.emoji in validreactions
            reaction, member = await self.bot.wait_for('reaction_add', check=reactioncheck, timeout=30)
            # Check if thumbs up
            if reaction.emoji != "\U0001f44d":
                await ctx.author.send("Command cancelled")
                disconn.close()
                return
            '''
            # Get starting values
            await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
            curBalDonator = await asyncio.gather(discur.fetchone())
            curBalDonator = curBalDonator[0]['Balance']
            await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (user.id,))
            curBalReceiver = await asyncio.gather(discur.fetchone())
            curBalReceiver = curBalReceiver[0]['Balance']
            # Check if they have enough
            if(curBalDonator and (curBalDonator >= amount)):
                # Remove coins
                await discur.execute('UPDATE users SET Balance = Balance - %s WHERE DiscordID = %s;', (amount, ctx.author.id))
                await discur.execute('UPDATE users SET Balance = Balance + %s WHERE DiscordID = %s;', (amount, user.id))

                await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (ctx.author.id,))
                newBalDonator = await asyncio.gather(discur.fetchone())
                newBalDonator = newBalDonator[0]['Balance']
                await discur.execute('SELECT Balance FROM users WHERE DiscordID = %s;', (user.id,))
                newBalReceiver = await asyncio.gather(discur.fetchone())
                newBalReceiver = newBalReceiver[0]['Balance']

                if newBalDonator != curBalDonator and newBalReceiver != curBalReceiver:
                    embed = discord.Embed(
                        title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Data:", value=f"{ctx.author.mention} gave {user.mention} **{amount} Coins**!")
                    await ctx.send(embed=embed)
                    # await GamblingCog.gamblelog(self, ctx, amount, "Jackpot")
                    # Start the countdown with 2 players

                else:
                    # Coins didn't change
                    embed = discord.Embed(
                        title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Error:", value=f"{ctx.author.mention}, an error has occured. Please screenshot this and make a ticket")
                    await ctx.send(embed=embed)
                    # Close the connections
                    disconn.close()
                    return
            else:
                # Not enough Coins
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"{ctx.author.mention} does not have enough in their Balance for this transfer!")
                await ctx.send(embed=embed)
                # Close the connections
                disconn.close()
                return
        else:
            # User not registed
            embed = discord.Embed(
                title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            if not (await GamblingCog.check_id(self, ctx.author)):
                embed.add_field(
                    name="Error:", value=f"The Discord Account {ctx.author.mention} is currently not registered!\n"
                    f"Please make a ticket as follows : `-new registration INSERTSTEAM64ID`", inline=False)
            else:
                embed.add_field(
                    name="Error:", value=f"The Discord Account {user.mention} is currently not registered!\n"
                    f"Please make a ticket as follows : `-new registration INSERTSTEAM64ID`", inline=False)
            await ctx.send(embed=embed)
            # Close the connections
            disconn.close()
            return
        disconn.close()


def setup(bot):
    bot.add_cog(GamblingCog(bot))
