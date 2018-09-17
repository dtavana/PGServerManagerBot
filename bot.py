import discord
import asyncio
import aiomysql
from discord.ext import commands
import datetime

#CUSTOM MODULES
import config as cfg
#from dbcommands import *

prefix = "pg "
bot = commands.Bot(command_prefix=prefix)

loop  = asyncio.get_event_loop()
async def dzConnect():
    await bot.wait_until_ready()
    pool = await aiomysql.create_pool(host=cfg.dzhost, port=cfg.dzport,
        user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, loop=loop)
    with (await pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        bot.dzcur = cur
        bot.dzcommit = conn.commit()

loop  = asyncio.get_event_loop()
async def disConnect():
    await bot.wait_until_ready()
    pool = await aiomysql.create_pool(host=cfg.dishost, port=cfg.disport,
        user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, loop=loop)
    with (await pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        bot.discur = cur
        bot.discommit = conn.commit()


async def check_id(user: discord.Member):
    #Check if id exists
    await bot.discur.execute('SELECT PlayerUID FROM users WHERE DiscordUser = %s;', (str(user),))
    result = await asyncio.gather(bot.discur.fetchone())
    if not result:
        return False
    else:
        return True

async def get_steamid(user: discord.Member):
    await bot.discur.execute('SELECT PlayerUID from users WHERE DiscordUser = %s;', (str(user),))
    result = await asyncio.gather(bot.discur.fetchone())
    realsteamid = result[0].get("PlayerUID")
    return realsteamid

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_amountlog(ctx, amount, user, admin, type):
    embed = discord.Embed(title=f"{type} Log \U00002705", colour=discord.Colour(0xf44b42))
    embed.set_footer(text="PGServerManager | TwiSt#2791")
    embed.add_field(name="Data:", value=f"{admin} gave {user.mention} {amount} {type}!")
    
    channel = bot.get_channel(488893718125084687)
    await channel.send(embed=embed)

@bot.event
async def on_otherlog(ctx, user, steamid, admin, type):
    embed = discord.Embed(title=f"{type} Log \U00002705", colour=discord.Colour(0xf44b42))
    embed.set_footer(text="PGServerManager | TwiSt#2791")
    embed.add_field(name="Data:", value=f"{admin} registered {user.mention} to {steamid}!")
    
    channel = bot.get_channel(488893718125084687)
    await channel.send(embed=embed)
  

@bot.command()
@commands.has_any_role("Owner","Developer","Manager","Head Admin","Super Admin") 
async def register(ctx, user: discord.Member, steamid):
    if await check_id(user):
        await bot.discur.execute('SELECT PlayerUID from users WHERE DiscordUser = %s;', (str(user),))
        result = await asyncio.gather(bot.discur.fetchone())
        realsteamid = result[0].get("PlayerUID")
        embed = discord.Embed(title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name="Error:", value=f"The DiscordUser: {user.mention} is already registered to {realsteamid}!")
        await ctx.send(embed=embed)
        await ctx.send()
    else:
        await bot.discur.execute("INSERT INTO users (DiscordUser, PlayerUID) VALUES (%s,%s);", (str(user), steamid))
        bot.discommit()
        if check_id(user):
            embed = discord.Embed(title=f"**Success** \U00002705", colour=discord.Colour(0x32CD32))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Data:", value=f"{user.mention} succesfully bound to {steamid}!")
            await ctx.send(embed = embed)
            admin = ctx.message.author
            bot.dispatch("otherlog", ctx, user, steamid, admin, "Registration")
        else:
            await ctx.send("An error has occured!")

@bot.command()
@commands.has_any_role("Owner","Developer","Manager", "Head Admin","Super Admin","Admin","Moderator") 
async def ping(ctx):
    '''
    Gets the Bot's latency
    '''
    try:
        latency = bot.latency
        embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name="Data:", value=f"Latency: {latency}")
        await ctx.send(embed = embed)
    except:
        await ctx.send("You do not have access to use this command!")


@bot.command()
@commands.has_any_role("Owner","Manager","Developer","Head Admin","Super Admin") 
async def playerdata(ctx, user: discord.Member):
    '''
    if await check_id(user):
        steamid = await get_steamid(user)
        #Get the data
        await bot.dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
        bankData = await asyncio.gather(bot.dzcur.fetchone())
        await bot.dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
        xpData = await asyncio.gather(bot.dzcur.fetchone())	
        embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name=f"BankCoins Data:", value=f"**BankCoins**: {bankData[0]['BankCoins']}")
        embed.add_field(name=f"XP Data:", value=f"**XP**: {xpData[0]['XP']}")
        await ctx.send(embed = embed)
    else:
	    await ctx.send(f"The DiscordUser: {user.mention} is not registered.")
    
    '''
    '''
	Gets all of a player's data
	'''
    #Checks to see if user is registered
    try:
        if await check_id(user):
            steamid = await get_steamid(user)
            #Get the data
            await bot.dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
            bankData = await asyncio.gather(bot.dzcur.fetchone())
            await bot.dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
            xpData = await asyncio.gather(bot.dzcur.fetchone())			
            embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name=f"BankCoins Data:", value=f"**BankCoins**: {bankData[0]['BankCoins']}")
            embed.add_field(name=f"XP Data:", value=f"**XP**: {xpData[0]['XP']}")
            await ctx.send(embed = embed)
        else:
            await ctx.send(f"The DiscordUser: {user.mention} is not registered.")
    except Exception as e:
        embed = discord.Embed(title=f"**Exception** \U0000274c", colour=discord.Colour(0xf44b42))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name="There was the following exception!", value=f"```{e}```")
        await ctx.send(embed=embed)
        channel = bot.get_channel(488893718125084687)
        await channel.send(embed=embed)

@bot.command()
@commands.has_any_role("Owner","Manager","Developer","Head Admin","Super Admin") 
async def coins(ctx, user: discord.Member, amount: int):
    '''
    Changes a player's BankCoins in the Database
    '''
    #Checks to see if user is registered
    try:
        if await check_id(user):
            steamid = await get_steamid(user)
            #Get starting value
            await bot.dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
            original = await asyncio.gather(bot.dzcur.fetchone())
                
            #Perform the query
            await bot.dzcur.execute('UPDATE player_data SET BankCoins = BankCoins + %s WHERE PlayerUID = %s;', (amount, steamid))
            bot.dzcommit

            #Check if it actually changed
            await bot.dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
            new = dzcursor.fetchone()
            if(new == original):
                await ctx.send("An error has occured! Nothing has been changed. Please fix your syntax")
            else:
                embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="Data:", value=f"{user.mention} has received **{amount} Coins to Bank**!")
                embed.add_field(name="Original:", value=f"{user.mention} had **{original[0]['BankCoins']} Coins in Bank**!")
                embed.add_field(name="New:", value=f"{user.mention} now has **{new[0]['BankCoins']} Coins in Bank**!")
                await ctx.send(embed = embed)
                admin = ctx.message.author
                bot.dispatch("amountlog", ctx, amount, user, admin, "Coins to Bank")
        else:
            await ctx.send(f"The DiscordUser: {user.mention} is not registered.")
    except Exception as e:
        embed = discord.Embed(title=f"{type} Exception \U0000274c", colour=discord.Colour(0xf44b42))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name="There was the following exception!", value=f"```{e}```")
        await ctx.send(embed=embed)
        channel = bot.get_channel(488893718125084687)
        await channel.send(embed=embed)



@bot.command()
@commands.has_any_role("Owner","Manager","Developer","Head Admin","Super Admin") 
async def xp(ctx, user: discord.Member, amount: int):
    try:
        if await check_id(user):
            steamid = await get_steamid(user)
            #Get starting value
            await bot.dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
            original = await asyncio.gather(bot.dzcur.fetchone())

            await bot.dzcur.execute('UPDATE xpsystem SET XP = XP + %s WHERE PlayerUID = %s;', (amount, steamid))
            bot.dzcommit
                
            #Check if it actually changed
            await dzcursor.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
            new = dzcursor.fetchone()

            if(new == original):
                await ctx.send("An error has occured! Nothing has been changed. Please fix your syntax")
            else:
                embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                embed.set_footer(text="PGServerManager | TwiSt#2791")
                embed.add_field(name="Data:", value=f"{user.mention} has received **{amount} XP**!")
                embed.add_field(name="Original:", value=f"{user.mention} had **{original[0]['XP']} XP**!")
                embed.add_field(name="New:", value=f"{user.mention} now has **{new[0]['XP']} XP**!")
                await ctx.send(embed = embed)
                admin = ctx.message.author
                bot.dispatch("amountlog", ctx, amount, user, admin, "XP")
        else:
            await ctx.send(f"The DiscordUser: {user.mention} is not registered. Please create a ticket with your SteamID in the subject!")
    except Exception as e:
        embed = discord.Embed(title=f"{type} Exception \U0000274c", colour=discord.Colour(0xf44b42))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name="There was the following exception!", value=f"```{e}```")
        await ctx.send(embed=embed)
        channel = bot.get_channel(488893718125084687)
        await channel.send(embed=embed)


@bot.command()
@commands.has_any_role("Owner", "Developer") 
async def customquery(ctx, query:str, db: str):
    if db == "dz":
        await bot.dzcur.execute(query)
        bot.dzcommit
        result = bankData = await asyncio.gather(bot.dzcur.fetchall())
        for x in result:
            embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Data:", value=f"`{x}`")
            await ctx.send(embed = embed)
    elif db == "dis":
        await bot.discur.execute(query)
        bot.discommit
        result = await asyncio.gather(bot.discur.fetchall())
        for x in result:
            embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
            embed.set_footer(text="PGServerManager | TwiSt#2791")
            embed.add_field(name="Data:", value=f"`{x}`")
            await ctx.send(embed = embed)
    

bot.loop.create_task(dzConnect())
bot.loop.create_task(disConnect())
bot.run(cfg.token)
