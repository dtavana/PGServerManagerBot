#Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands

#Misc. Modules
import datetime
import config as cfg

class DBCommandsCog:
	def __init__(self, bot):
		self.bot = bot
    
	#--------------ID Checks--------------
	async def check_id(self, user: discord.Member):
		#Check if ID exists
		await self.bot.discur.execute('SELECT PlayerUID FROM users WHERE DiscordUser = %s;', (str(user),))
		result = await asyncio.gather(self.bot.discur.fetchone())
		#Check if anything was returned
		if not result:
			return False
		else:
			return True
 
	async def get_steamid(self, user: discord.Member):
		await self.bot.discur.execute('SELECT PlayerUID from users WHERE DiscordUser = %s;', (str(user),))
		result = await asyncio.gather(self.bot.discur.fetchone())
		realsteamid = result[0].get("PlayerUID")
		return realsteamid
	
	#--------------Logging--------------
	async def on_amountlog(self, ctx, amount, user, admin, type):
		embed = discord.Embed(title=f"{type} Log \U00002705", colour=discord.Colour(0xf44b42))
		embed.set_footer(text="PGServerManager | TwiSt#2791")
		embed.add_field(name="Data:", value=f"{admin} gave {user.mention} {amount} {type}!")
		
		channel = self.bot.get_channel(488893718125084687)
		await channel.send(embed=embed)

	async def on_otherlog(self, ctx, user, steamid, admin, type):
		if type == "Registration":
			embed = discord.Embed(title=f"{type} Log \U00002705", colour=discord.Colour(0xf44b42))
			embed.set_footer(text="PGServerManager | TwiSt#2791")
			embed.add_field(name="Data:", value=f"{admin} registered {user.mention} to {steamid}!")
		channel = self.bot.get_channel(488893718125084687)
		await channel.send(embed=embed)
	
	@commands.command()
	@commands.has_any_role("Owner","Developer","Manager","Head Admin","Super Admin") 
	async def register(self, ctx, user: discord.Member, steamid):
		if await DBCommandsCog.check_id(self, user):
			await self.bot.discur.execute('SELECT PlayerUID from users WHERE DiscordUser = %s;', (str(user),))
			result = await asyncio.gather(self.bot.discur.fetchone())
			realsteamid = result[0].get("PlayerUID")
			embed = discord.Embed(title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
			embed.set_footer(text="PGServerManager | TwiSt#2791")
			embed.add_field(name="Error:", value=f"The DiscordUser: {user.mention} is already registered to {realsteamid}!")
			await ctx.send(embed=embed)
			await ctx.send()
		else:
			await self.bot.discur.execute("INSERT INTO users (DiscordUser, PlayerUID) VALUES (%s,%s);", (str(user), steamid))
			self.bot.discommit()
			if await DBCommandsCog.check_id(self, user):
				embed = discord.Embed(title=f"**Success** \U00002705", colour=discord.Colour(0x32CD32))
				embed.set_footer(text="PGServerManager | TwiSt#2791")
				embed.add_field(name="Data:", value=f"{user.mention} succesfully bound to {steamid}!")
				await ctx.send(embed = embed)
				admin = ctx.message.author
				self.dispatch("otherlog", ctx, user, steamid, admin, "Registration")
			else:
				await ctx.send("An error has occured!")
    
	@commands.command()
	@commands.has_any_role("Owner","Manager","Developer","Head Admin","Super Admin") 
	async def coins(self, ctx, user: discord.Member, amount: int):
		'''
		Changes a player's BankCoins in the Database
		'''
		#Checks to see if user is registered
		if await DBCommandsCog.check_id(self, user):
			steamid = await DBCommandsCog.get_steamid(self, user)
			#Get starting value
			await self.bot.dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
			original = await asyncio.gather(self.bot.dzcur.fetchone())
                    
			#Perform the query
			await self.bot.dzcur.execute('UPDATE player_data SET BankCoins = BankCoins + %s WHERE PlayerUID = %s;', (amount, steamid))
			self.bot.dzcommit

			#Check if it actually changed
			await self.bot.dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
			new = await asyncio.gather(self.bot.dzcur.fetchone())
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
				self.dispatch("amountlog", ctx, amount, user, admin, "Coins to Bank")
		else:
			await ctx.send(f"The DiscordUser: {user.mention} is not registered.")

	@commands.command()
	@commands.has_any_role("Owner","Manager","Developer","Head Admin","Super Admin") 
	async def xp(self, ctx, user: discord.Member, amount: int):
		if await DBCommandsCog.check_id(self, user):
			steamid = await DBCommandsCog.get_steamid(self, user)
			#Get starting value
			await self.bot.dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
			original = await asyncio.gather(self.bot.dzcur.fetchone())

			await self.bot.dzcur.execute('UPDATE xpsystem SET XP = XP + %s WHERE PlayerUID = %s;', (amount, steamid))
			self.bot.dzcommit
                    
			#Check if it actually changed
			await self.bot.dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
			new = await asyncio.gather(self.bot.dzcur.fetchone())

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
				self.dispatch("amountlog", ctx, amount, user, admin, "XP")
		else:
			await ctx.send(f"The DiscordUser: {user.mention} is not registered. Please create a ticket with your SteamID in the subject!")

	@commands.command()
	@commands.has_any_role("Owner","Manager","Developer","Head Admin","Super Admin") 
	async def playerdata(self, ctx, user: discord.Member):
		'''
		Gets all of a player's data
		'''
		#Checks to see if user is registered
		if await DBCommandsCog.check_id(self, user):
			steamid = await DBCommandsCog.get_steamid(self, user)
			#Get the data
			await self.bot.dzcur.execute('SELECT BankCoins FROM player_data WHERE PlayerUID = %s;', (steamid,))
			bankData = await asyncio.gather(self.bot.dzcur.fetchone())
			await self.bot.dzcur.execute('SELECT XP FROM xpsystem WHERE PlayerUID = %s;', (steamid,))
			xpData = await asyncio.gather(self.bot.dzcur.fetchone())			
			embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
			embed.set_footer(text="PGServerManager | TwiSt#2791")
			embed.add_field(name=f"BankCoins Data:", value=f"**BankCoins**: {bankData[0]['BankCoins']}")
			embed.add_field(name=f"XP Data:", value=f"**XP**: {xpData[0]['XP']}")
			await ctx.send(embed = embed)
		else:
			await ctx.send(f"The DiscordUser: {user.mention} is not registered.")
    
	@commands.command()
	@commands.has_any_role("Owner", "Developer") 
	async def customquery(self, ctx, query:str, db: str):
		if db == "dz":
			await self.bot.dzcur.execute(query)
			self.bot.dzcommit
			result = await asyncio.gather(self.dzcur.fetchall())
			for x in result:
				embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
				embed.set_footer(text="PGServerManager | TwiSt#2791")
				embed.add_field(name="Data:", value=f"`{x}`")
				await ctx.send(embed = embed)
		elif db == "dis":
			await self.bot.discur.execute(query)
			self.bot.discommit
			result = await asyncio.gather(self.discur.fetchall())
			for x in result:
				embed = discord.Embed(title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
				embed.set_footer(text="PGServerManager | TwiSt#2791")
				embed.add_field(name="Data:", value=f"`{x}`")
				await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(DBCommandsCog(bot))