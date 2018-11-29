# Base Modules for Bot
import discord
import asyncio
import aiomysql
from discord.ext import commands
import traceback

# Misc. Modules
import datetime
import config as cfg
import os
import subprocess
import ast


class ServerManagementCog:
    def __init__(self, bot):
        self.bot = bot
    
    async def validsteamidcheck(self, ctx, steamid):
        if (steamid[:7] == "7656119" and len(steamid) == 17):
            return True
        else:
            return False
    
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

    @commands.command()
    @commands.has_any_role("Owner", "Developer")
    async def globalitemcheck(self, ctx, classname: str, minCount: int):
        try:
            # Open Connection
            dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
            dzcur = await dzconn.cursor(aiomysql.DictCursor)
            disconn = await aiomysql.connect(host=cfg.dishost, port=cfg.disport, user=cfg.disuser, password=cfg.dispass, db=cfg.disschema, autocommit=True)
            discur = await disconn.cursor(aiomysql.DictCursor)

            notfound = False

            #Object Data
            await dzcur.execute('SELECT ObjectUID, ObjectID, Worldspace, Inventory, Classname FROM object_data WHERE LOCATE(%s, Inventory) > 0;', (classname,))
            data = await asyncio.gather(dzcur.fetchall())
            if not data[0]:
                notfound = True
            else:
                for x in data[0]:
                    inventory = x['Inventory']
                    inventory = ast.literal_eval(inventory)
                    guns = inventory[0]
                    mags = inventory[1]
                    backpacks = inventory[2]
                    worldspace = x['Worldspace']
                    
                    startuidIndex = worldspace.find('7656')
                    playeruid = worldspace[startuidIndex:startuidIndex + 17]
                    await discur.execute("SELECT DiscordID FROM users WHERE PlayerUID = %s;", (playeruid,))
                    did = await asyncio.gather(discur.fetchone())
                    disMemberString = "**Discord User**: Discord Member not found\n"
                    if(did[0] != None):
                        did = did[0]['DiscordID']
                        disMember = ctx.guild.get_member(int(did))
                        if disMember is not None:
                            disMemberString = f"**Discord User**: {disMember.mention}\n"
                    
                    worldspace = worldspace[1:]
                    worldspace = worldspace[worldspace.find(
                        '['):worldspace.find(']') + 1]
                    ouid = x['ObjectUID']
                    oid = x['ObjectID']
                    objectclassname = x['Classname']

                    guns[0] = [x.lower() for x in guns[0]]
                    mags[0] = [x.lower() for x in mags[0]]
                    backpacks[0] = [x.lower() for x in backpacks[0]]
                    newclassname = classname.lower()

                    if newclassname in guns[0]:
                        index = guns[0].index(newclassname)
                        count = guns[1][index]
                    elif newclassname in mags[0]:
                        index = mags[0].index(newclassname)
                        count = mags[1][index]
                    elif newclassname in backpacks[0]:
                        index = backpacks[0].index(newclassname)
                        count = backpacks[1][index]
                    else:
                        await ctx.send("An error has occured")
                        return
                    if count >= minCount:
                        embed = discord.Embed(
                            title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                        embed.set_footer(text="PGServerManager | TwiSt#2791")
                        embed.add_field(name=f"Data:", value=f"**Type**: Object\n"
                                        f"**Classname**: {classname}\n"
                                        f"**Count**: {count}\n"
                                        f"**Worldspace**: {worldspace}\n"
                                        f"**Object Classname**: {objectclassname}\n"
                                        f"**Object UID**: {ouid}\n"
                                        f"**Object ID**: {oid}\n"
                                        f"**PlayerUID**: {playeruid}\n" + disMemberString, inline=False)
                        await ctx.send(embed=embed)
            #Garage
            await dzcur.execute('SELECT PlayerUID, id, DisplayName, Classname, Inventory FROM garage WHERE LOCATE(%s, Inventory) > 0;', (classname,))
            data = await asyncio.gather(dzcur.fetchall())
            if not data[0] and notfound:
                await ctx.send(f"Did not find any objects containing {classname}")
            else:
                for x in data[0]:
                    inventory = x['Inventory']
                    inventory = ast.literal_eval(inventory)
                    guns = inventory[0]
                    mags = inventory[1]
                    backpacks = inventory[2]
                    
                    playeruid = x['PlayerUID']
                    await discur.execute("SELECT DiscordID FROM users WHERE PlayerUID = %s;", (playeruid,))
                    did = await asyncio.gather(discur.fetchone())
                    disMemberString = "**Discord User**: Discord Member not found\n"
                    if(did[0] != None):
                        did = did[0]['DiscordID']
                        disMember = ctx.guild.get_member(int(did))
                        if disMember is not None:
                            disMemberString = f"**Discord User**: {disMember.mention}\n"
                        
                    gid = x['id']
                    objectclassname = x['Classname']
                    objectdisplayname = x['DisplayName']

                    guns[0] = [x.lower() for x in guns[0]]
                    mags[0] = [x.lower() for x in mags[0]]
                    backpacks[0] = [x.lower() for x in backpacks[0]]
                    newclassname = classname.lower()

                    if newclassname in guns[0]:
                        index = guns[0].index(newclassname)
                        count = guns[1][index]
                    elif newclassname in mags[0]:
                        index = mags[0].index(newclassname)
                        count = mags[1][index]
                    elif newclassname in backpacks[0]:
                        index = backpacks[0].index(newclassname)
                        count = backpacks[1][index]
                    else:
                        await ctx.send("An error has occured")
                        return
                    if count >= minCount:
                        embed = discord.Embed(
                            title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                        embed.set_footer(text="PGServerManager | TwiSt#2791")
                        embed.add_field(name=f"Data:", value=f"**Type**: Garage\n"
                                        f"**Item Classname**: {classname}\n"
                                        f"**Count**: {count}\n"
                                        f"**Object Displayname**: {objectdisplayname}\n"
                                        f"**Object Classname**: {objectclassname}\n"
                                        f"**Garage ID**: {gid}\n"
                                        f"**PlayerUID**: {playeruid}\n" + disMemberString, inline=False)
                        await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")
        finally:
            dzconn.close()
            disconn.close()
    
    @commands.command()
    @commands.has_any_role("Owner", "Developer", "Manager", "Head Admin", "Super Admin")
    async def itemcheck(self, ctx, user, classname: str):
        try: 
            # Open Connection
            dzconn = await aiomysql.connect(host=cfg.dzhost, port=cfg.dzport, user=cfg.dzuser, password=cfg.dzpass, db=cfg.dzschema, autocommit=True)
            dzcur = await dzconn.cursor(aiomysql.DictCursor)

            notfound = False

            if(await ServerManagementCog.validsteamidcheck(self, ctx, user) != True):
                try:
                    user = await commands.MemberConverter().convert(ctx, user)
                    steamid = await ServerManagementCog.get_steamid(self, user)
                    if (steamid == None):
                        await ctx.send(f"Could not find a registration for {user.mention}")
                except:
                    await ctx.send(f"Invalid value for user: `{user}` (Must be a **Discord User* or a Valid **STEAM64ID**)")
            else:
                steamid = user
            
            #Object Data
            await dzcur.execute('SELECT ObjectUID, ObjectID, Worldspace, Inventory, Classname FROM object_data WHERE LOCATE(%s, Worldspace) > 0 AND LOCATE(%s, Inventory) > 0;', (steamid, classname))
            data = await asyncio.gather(dzcur.fetchall())
            if not data[0]:
                notfound = True
            else:
                for x in data[0]:
                    inventory = x['Inventory']
                    inventory = ast.literal_eval(inventory)
                    guns = inventory[0]
                    mags = inventory[1]
                    backpacks = inventory[2]
                    worldspace = x['Worldspace']
                    worldspace = worldspace[1:]
                    worldspace = worldspace[worldspace.find('['):worldspace.find(']') + 1]
                    ouid = x['ObjectUID']
                    oid = x['ObjectID']
                    objectclassname = x['Classname']

                    guns[0] = [x.lower() for x in guns[0]]
                    mags[0] = [x.lower() for x in mags[0]]
                    backpacks[0] = [x.lower() for x in backpacks[0]]
                    newclassname = classname.lower()

                    if newclassname in guns[0]:
                        index = guns[0].index(newclassname)
                        count = guns[1][index]
                    elif newclassname in mags[0]:
                        index = mags[0].index(newclassname)
                        count = mags[1][index]
                    elif newclassname in backpacks[0]:
                        index = backpacks[0].index(newclassname)
                        count = backpacks[1][index]
                    else:
                        await ctx.send("An error has occured")
                        return
                    try:
                        userString = f"**User**: {user.mention}\n"
                    except:
                        userString = f"**User**: {user}\n"
                    
                    embed = discord.Embed(
                        title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(name=f"Data:", value=f"**Type**: Object\n"
                                    f"**Classname**: {classname}\n"
                                    f"**Count**: {count}\n"
                                    f"**Worldspace**: {worldspace}\n"
                                    f"**Object Classname**: {objectclassname}\n"
                                    f"**Object UID**: {ouid}\n"
                                    f"**Object ID**: {oid}\n" + userString, inline=False)
                    
                    await ctx.send(embed=embed)
            #Garage
            await dzcur.execute('SELECT id, DisplayName, Classname, Inventory FROM garage WHERE PlayerUID = %s AND LOCATE(%s, Inventory) > 0;', (steamid, classname))
            data = await asyncio.gather(dzcur.fetchall())
            if not data[0] and notfound:
                try:
                    await ctx.send(f"Did not find any objects containing {classname} that are owned by {user.mention}")
                except:
                    await ctx.send(f"Did not find any objects containing {classname} that are owned by {user}")
            else:
                for x in data[0]:
                    inventory = x['Inventory']
                    inventory = ast.literal_eval(inventory)
                    guns = inventory[0]
                    mags = inventory[1]
                    backpacks = inventory[2]
                    gid = x['id']
                    objectclassname = x['Classname']
                    objectdisplayname = x['DisplayName']

                    guns[0] = [x.lower() for x in guns[0]]
                    mags[0] = [x.lower() for x in mags[0]]
                    backpacks[0] = [x.lower() for x in backpacks[0]]
                    newclassname = classname.lower()

                    if newclassname in guns[0]:
                        index = guns[0].index(newclassname)
                        count = guns[1][index]
                    elif newclassname in mags[0]:
                        index = mags[0].index(newclassname)
                        count = mags[1][index]
                    elif newclassname in backpacks[0]:
                        index = backpacks[0].index(newclassname)
                        count = backpacks[1][index]
                    else:
                        await ctx.send("An error has occured")
                        return
                    try:
                        userString = f"**User**: {user.mention}\n"
                    except:
                        userString = f"**User**: {user}\n"

                    embed = discord.Embed(
                        title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
                    embed.set_footer(text="PGServerManager | TwiSt#2791")
                    embed.add_field(name=f"Data:", value=f"**Type**: Garage\n"
                                    f"**Item Classname**: {classname}\n"
                                    f"**Count**: {count}\n"
                                    f"**Object Displayname**: {objectdisplayname}\n"
                                    f"**Object Classname**: {objectclassname}\n"
                                    f"**Garage ID**: {gid}\n" + userString, inline=False)
                    await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")
        finally:
            dzconn.close()
             
    
    
    @commands.command()
    @commands.has_any_role("Owner", "Developer", "Manager", "Head Admin", "Super Admin", "Admin")
    async def viewchernorpt(self, ctx):
        embed = discord.Embed(
            title=f"Success \U00002705", colour=discord.Colour(0x32CD32))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(name=f"Current RPT:", value=f"It is below")
        await ctx.author.send(embed=embed)
        await ctx.author.send(file=discord.File("C:\\Cherno_Main\\DZE_Server_Config\\arma2oaserver.rpt"))
    
    @commands.command()
    @commands.has_any_role("Owner", "Developer", "Manager", "Head Admin", "Super Admin", "Admin")
    async def restartcherno(self, ctx):
        embed = discord.Embed(
            title=f"ReactToConfirm \U0001f4b1", colour=discord.Colour(0xFFA500))
        embed.set_footer(text="PGServerManager | TwiSt#2791")
        embed.add_field(
            name="Server:", value=f"Are you sure you would like to restart the `Chernarus` server?")
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
        p = subprocess.Popen(
            ['cmd','/c','start C:\\Users\\TwiSt\\Desktop\\Files\\PGServerManagerBot\\forceclosecherno.lnk'])


def setup(bot):
    bot.add_cog(ServerManagementCog(bot))
