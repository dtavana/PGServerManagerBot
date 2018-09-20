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
      
    #---------Checks--------
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
            
    @commands.command()
    async def jackpot(self, ctx, amount: int):
        dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
        dzcur = await dzconn.cursor(aiomysql.DictCursor)
        disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
        discur = await disconn.cursor(aiomysql.DictCursor)
        
        if await GamblingCog.check_id(self, ctx.author):
            steamid = await DBCommandsCog.get_steamid(self, player)
            curPlayers = await DBCommandsCog.currentplayers(self, ctx)
            if (steamid not in curPlayers):
                # Get starting value
                await dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
                curCoins = await asyncio.gather(dzcur.fetchone())
                #Check if they have enough
                if(curCoins and (curCoins[0]['BankCoins'] > amount)):
                    discur.execute('INSERT INTO jackpot (DiscordUser, amount) VALUES (%s, %s);', (ctx,author, amount)
                    discur.execute('SELECT * FROM jackpot')
                    curUsers = await asyncio.gather(discur.fetchall())
                    
                    embed = discord.Embed(
                        title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(
                        name="Data:", value=f"{ctx.author.mention} has entered the jackpot with **{amount} Coins**!")
                    for x in curCoins:
                        
                    await ctx.send(embed=embed)
                  
                else:
                  
              
            else:
        
        else:
          
        


def setup(bot):
    bot.add_cog(GamblingCog(bot))
