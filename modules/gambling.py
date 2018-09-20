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
        realsteamid = realsteamid.get('PlayerUID')
        # Close Connection
        disconn.close()
        return realsteamid

    @commands.command()
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
                if(curCoins and (curCoins > amount)):
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
                        #Calculate the true total for the player
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
                    else:
                        #Coins didn't change
                        embed = discord.Embed(
                            title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                        embed.set_footer(text="PGServerManager | TwiSt#2791")
                        embed.add_field(
                            name="Error:", value=f"An error has occured and your coins haven't changed!")
                        await ctx.send(embed=embed)
                else:
                    #Not enough Coins
                    embed = discord.Embed(
                        title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                    name="Error:", value=f"You do not have enough BankCoins for this bet!")
                    await ctx.send(embed=embed)
            else:
                #User was in game
                embed = discord.Embed(
                    title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(
                    name="Error:", value=f"The STEAM64ID bound to {ctx.author.mention} ({steamid}) is currently in game")
                await ctx.send(embed=embed)
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


def setup(bot):
    bot.add_cog(GamblingCog(bot))
