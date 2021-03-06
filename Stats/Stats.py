import requests
import discord
from discord.ext import commands
import json
import os

from cogs.utils.dataIO import dataIO

class Stats:
    """Prints how many times you've used commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        """Prints how many times you've used commands."""
        # Check if stats is being called in a private message
        if (ctx.message.server == None):
            serverid = "PrivateMessage"
        else:
            serverid = ctx.message.server.id
            
        datapath = "data/stats/" + serverid
        userid = ctx.message.author.id
        displayname = ctx.message.author.display_name

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

        # Can't print if data invalid
        if not os.path.isfile(datapath + "/" + userid + ".json"):
            await self.bot.say("You don't have any stats tracked, " + displayname + "! Try using some commands.")
            return
        elif not dataIO.is_valid_json(datapath + "/" + userid + ".json"):
            await self.bot.say("Invalid stats JSON found. All your stats are gone forever. Blame a dev :^(")
            data = {}
            dataIO.save_json(datapath + "/" + userid + ".json", data)
            return

        output = "Here are your stats for commands called in this server, " + ctx.message.author.display_name + ":\n\n"
        # Print all available stats
        userdata = dataIO.load_json(datapath + "/" + userid + ".json")

        if "commands" in userdata and not len(userdata["commands"]) == 0:
            output += "--Times commands called--\n"
            for commandname, count in userdata["commands"].items():
                output += commandname + ":  " + str(count) + "\n"

        if "achievements" in userdata and not len(userdata["achievements"]) == 0:
            output += "\n--Achievements--\n"
            for achievement, count in userdata["achievements"].items():
                output += achievement + ":  " + str(count) + "\n"

        await self.bot.say(output)


        return


class StatsTracker:
    async def updateStat(self, stattype, ctx, commandname):
        userid = ctx.message.author.id
        name = ctx.message.author.display_name
        # Check if stats is being called in a private message
        if (ctx.message.server == None):
            serverid = "PrivateMessage"
        else:
            serverid = ctx.message.server.id
        datapath = "data/stats"

        # Use only first word of command if stat is command
        command = commandname
        if (stattype == "commands"):
            command = command.split(' ', 1)[0]

        # Create directory if does not exist
        if not os.path.exists(datapath):
            print("Creating stats data directory...")
            os.makedirs(datapath)

        # Create directory for server if it doesn't already exist
        datapath += "/" + serverid
        if not os.path.exists(datapath):
            print("Creating server data directory...")
            os.makedirs(datapath)

        # Create JSON file if does not exist or if invalid
        invalidJSON = False
        if not os.path.isfile(datapath + "/" + userid + ".json"):
            invalidJSON = True
        elif not dataIO.is_valid_json(datapath + "/" + userid + ".json"):
            await self.bot.say("Invalid stats JSON found. All your stats are gone forever. Blame a dev :^(")
            invalidJSON = True

        if (invalidJSON):
            data = {"commands": {}, "achievements": {}}
            dataIO.save_json(datapath + "/" + userid + ".json", data)

        # Read in JSON file, increment command count, write
        userdata = dataIO.load_json(datapath + "/" + userid + ".json")
        userdata["username"] = name
        if stattype not in userdata:
            userdata[stattype] = {}
        if command not in userdata[stattype]:
            userdata[stattype][command] = 0


        # TEMP BUGFIX, remove after April 2017
        if "achievements" in userdata:
            userdata['achievements'].pop("Waifus", None)


        userdata[stattype][command] += 1
        dataIO.save_json(datapath + "/" + userid + ".json", userdata)


        return

    @commands.command(pass_context=True)

    async def stats(self, ctx):
        return



def checkFolders():
    if not os.path.exists("data/stats"):
        print("Creating directory data/stats...")
        os.makedirs("data/stats")

def setup(bot):
    checkFolders()
    bot.add_cog(Stats(bot))