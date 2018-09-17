#Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands

#Misc. Modules
import datetime
import config as cfg

extensions = ['modules.logging',
              'modules.dbcommands',
			  'modules.admin']

class PGManager(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=self.get_pref, case_insensitive=True)

	async def get_pref(self, bot, ctx):
		return 'pg '
		'''
		await self.discur.execute("SELECT prefix FROM prefixes WHERE guildid=$1;", ctx.guild.id)
		result = await asyncio.gather(self.discur.fetchone())
        if not result:
            return ['pg ']
        return data['prefix']
		'''

	#Error Handling
	
	
	def run(self):
		self.remove_command("help")
		for ext in extensions:
			try:
				self.load_extension(ext)
				print(f"Loaded extension {ext}")
			except Exception as e:
				print(f"Failed to load extensions {ext}")
				print(f"{type(e).__name__}: {e}")
		super().run(cfg.token)

	async def on_ready(self,):
		print("Bot loaded")
		print(f"Logged in as: {self.user}")
		print(f"Total Servers: {len(self.guilds)}")
		print(f"Total Cogs: {len(self.cogs)}")
		await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"PGManager | {len(self.users)} members"))
		
		#DZ DB
		self.dzdb = await aiomysql.create_pool(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema)
		with (await self.dzdb) as dzconn:
			self.dzcur = await dzconn.cursor(aiomysql.DictCursor)
			self.dzcommit = dzconn.commit()
		#Discord DB
		self.disdb = await aiomysql.create_pool(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema)
		with (await self.disdb) as disconn:
			self.discur = await disconn.cursor(aiomysql.DictCursor)
			self.discommit = disconn.commit()
		
		#Error logging
		async def on_command_error(ctx, error):
			embed = discord.Embed(title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
			embed.set_footer(text="PGServerManager | TwiSt#2791")
			embed.add_field(name="There was the following exception!", value=f"```{error}```")
			await ctx.send(embed=embed)
			channel = self.get_channel(488893718125084687)
			await channel.send(embed=embed)
        
		async def on_error(ctx, error):
			embed = discord.Embed(title=f"**ERROR** \U0000274c", colour=discord.Colour(0xf44b42))
			embed.set_footer(text="PGServerManager | TwiSt#2791")
			embed.add_field(name="There was the following exception!", value=f"```{error}```")
			await ctx.send(embed=embed)
			channel = self.get_channel(488893718125084687)
			await channel.send(embed=embed)

if __name__ == "__main__":
	PGManager().run()