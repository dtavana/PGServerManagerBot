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
import typing


class MiscCog:
    def __init__(self, bot):
        self.bot = bot

    def getPattern(curCharacter, o, x):
        switcher = {
            "A": [[[o, 7]],
                [[o, 2], [x, 3], [o, 2]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x, 5], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o, 7]]],
            "B": [[[o, 7]],
                [[o], [x, 4], [o, 2]],
                [[o, 2], [x], [o, 2], [x], [o]],
                [[o, 2], [x], [o, 2], [x], [o]],
                [[o, 2], [x, 3], [o, 2]],
                [[o, 2], [x], [o, 2], [x], [o]],
                [[o, 2], [x], [o, 2], [x], [o]],
                [[o], [x, 4], [o, 2]],
                [[o, 7]]],
            "C": [[[o, 7]],
                [[o, 2], [x, 4], [o]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o, 2], [x, 4], [o]],
                [[o, 7]]],
            "D": [[[o, 7]],
                [[o], [x, 4], [o, 2]],
                [[o, 2], [x], [o, 2], [x], [o]],
                [[o, 2], [x], [o, 2], [x], [o]],
                [[o, 2], [x], [o, 2], [x], [o]],
                [[o, 2], [x], [o, 2], [x], [o]],
                [[o, 2], [x], [o, 2], [x], [o]],
                [[o], [x, 4], [o, 2]],
                [[o, 7]]],
            "E": [[[o, 7]],
                [[o], [x, 5], [o]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o], [x, 4], [o, 2]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o], [x, 5], [o]],
                [[o, 7]]],
            "F": [[[o, 7]],
                [[o], [x, 5], [o]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o], [x, 4], [o, 2]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o, 7]]],
            "G": [[[o, 7]],
                [[o, 2], [x, 4], [o]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 5]],
                [[o], [x], [o, 2], [x, 2], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o, 2], [x, 4], [o]],
                [[o, 7]]],
            "H": [[[o, 7]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x, 5], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o], [x], [o, 3], [x], [o]],
                [[o, 7]]],
            "I": [[[o, 7]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 7]]],
            "J": [[[o, 7]],
                  [[o, 3], [x, 3], [o]],
                  [[o, 5], [x], [o]],
                  [[o, 5], [x], [o]],
                  [[o, 5], [x], [o]],
                  [[o, 5], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x, 4], [o, 2]],
                  [[o, 7]]],
            "K": [[[o, 7]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 2], [x, 2], [o]],
                  [[o], [x], [o], [x, 2], [o, 2]],
                  [[o], [x, 3], [o, 3]],
                  [[o], [x], [o], [x, 2], [o, 2]],
                  [[o], [x], [o, 2], [x, 2], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o, 7]]],
            "L": [[[o, 7]],
                  [[o], [x], [o, 5]],
                  [[o], [x], [o, 5]],
                  [[o], [x], [o, 5]],
                  [[o], [x], [o, 5]],
                  [[o], [x], [o, 5]],
                  [[o], [x], [o, 5]],
                  [[o], [x, 5], [o]],
                  [[o, 7]]],
            "M": [[[o, 7]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x, 2], [o], [x, 2], [o]],
                  [[o], [x, 5], [o]],
                  [[o], [x], [o], [x], [o], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o, 7]]],
            "N": [[[o, 7]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x, 2], [o, 2], [x], [o]],
                  [[o], [x, 3], [o], [x], [o]],
                  [[o], [x], [o], [x], [o], [x], [o]],
                  [[o], [x], [o], [x, 3], [o]],
                  [[o], [x], [o, 2], [x, 2], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o, 7]]],
            "O": [[[o, 7]],
                  [[o], [x, 5], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x, 5], [o]],
                  [[o, 7]]],
            "P": [[[o, 7]],
                  [[o], [x, 4], [o, 2]],
                  [[o, 2], [x], [o, 2], [x], [o]],
                  [[o, 2], [x], [o, 2], [x], [o]],
                  [[o, 2], [x, 3], [o, 2]],
                  [[o, 2], [x], [o, 4]],
                  [[o, 2], [x], [o, 4]],
                  [[o, 2], [x], [o, 4]],
                  [[o, 7]]],
            "Q": [[[o, 7]],
                  [[o, 2], [x, 3], [o, 2]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o], [x], [o], [x], [o]],
                  [[o], [x], [o, 2], [x], [o, 2]],
                  [[o, 2], [x, 2], [o], [x], [o]],
                  [[o, 7]]],
            "R": [[[o, 7]],
                  [[o], [x, 4], [o, 2]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x, 4], [o, 2]],
                  [[o], [x], [o], [x], [o, 3]],
                  [[o], [x], [o, 2], [x], [o, 2]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o, 7]]],
            "S": [[[o, 7]],
                  [[o, 2], [x, 4], [o]],
                  [[o], [x], [o, 5]],
                  [[o], [x], [o, 5]],
                  [[o, 2], [x, 3], [o, 2]],
                  [[o, 5], [x], [o]],
                  [[o, 5], [x], [o]],
                  [[o], [x, 4], [o, 2]],
                  [[o, 7]]],
            "T": [[[o, 7]],
                  [[o], [x, 5], [o]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 7]]],
            "U": [[[o, 7]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o, 2], [x, 3], [o, 2]],
                  [[o, 7]]],
            "V": [[[o, 7]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 2], [x, 2], [o]],
                  [[o], [x], [o, 2], [x], [o, 2]],
                  [[o], [x], [o], [x, 2], [o, 2]],
                  [[o], [x], [o], [x], [o, 3]],
                  [[o], [x, 3], [o, 3]],
                  [[o], [x, 2], [o, 4]],
                  [[o, 7]]],
            "W": [[[o, 7]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x], [o], [x], [o], [x], [o]],
                  [[o], [x], [o], [x], [o], [x], [o]],
                  [[o], [x], [o], [x], [o], [x], [o]],
                  [[o, 2], [x], [o], [x], [o, 2]],
                  [[o, 7]]],
            "X": [[[o, 7]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x, 2], [o], [x, 2], [o]],
                  [[o, 2], [x, 3], [o, 2]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 2], [x, 3], [o, 2]],
                  [[o], [x, 2], [o], [x, 2], [o]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o, 7]]],
            "Y": [[[o, 7]],
                  [[o], [x], [o, 3], [x], [o]],
                  [[o], [x, 2], [o], [x, 2], [o]],
                  [[o, 2], [x], [o], [x], [o, 2]],
                  [[o, 2], [x], [o], [x], [o, 2]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 7]]],
            "Z": [[[o, 7]],
                  [[o], [x, 5], [o]],
                  [[o, 4], [x], [o, 2]],
                  [[o, 3], [x, 2], [o, 2]],
                  [[o, 3], [x], [o, 3]],
                  [[o, 2], [x, 2], [o, 3]],
                  [[o, 2], [x], [o, 4]],
                  [[o], [x, 5], [o]],
                  [[o, 7]]]
        }
        return switcher.get(curCharacter)
    
    @commands.command()
    @commands.has_any_role("Owner", "Manager", "Developer", "Head Admin", "Super Admin", "Emoji Memer")
    async def beerememe(self, ctx, emoji1: typing.Union[discord.Member, str], emoji2: typing.Union[discord.Member, str], text: str):
        
      if not(text.isalpha()):
            await ctx.send(f"Invalid input of {text} (Only letters)")
            return
      if isinstance(emoji1, discord.Member) or isinstance(emoji2, discord.Member):
            await ctx.send(f"No tagging people nonce")
            return
      text = text.upper()
      for curChar in text:
            pattern = MiscCog.getPattern(curChar, emoji1, emoji2)
            result = ""
            count = 0
            for line in pattern:
                  curLine = ""
                  for emoji in line:
                        curEmoji = emoji[0]
                        if len(emoji) == 2:
                              amount = emoji[1]
                              for i in range(0, amount):
                                    curLine += curEmoji
                        else:
                              curLine += curEmoji
                  count += 1
                  curLine += "\n" 
                  result += curLine
                  if count == 4:
                        await ctx.send(result)
                        result = ""
                  elif count == 9:
                        await ctx.send(result)


def setup(bot):
    bot.add_cog(MiscCog(bot))
