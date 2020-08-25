import server
import util
import var

import discord
from discord.ext import commands

import importlib
import os
import traceback
import sys

from collections import defaultdict

bot = commands.Bot(command_prefix="++", case_insensitive = True)
bot.remove_command("help")

for extension in ["ide"]:
  bot.load_extension(f"cogs.{extension}")
  print(f"{extension} loaded")

@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="++help"))
  print(f"Ready: {bot.user}")

@bot.command(name="reload")
@commands.is_owner()
async def rl(ctx):
  bot.reload_extension(f"cogs.ide")
  modulecounter = 0
  for fl in os.listdir("functions"):
    if fl.endswith("py"):
      fl = fl[:-3]
      importlib.reload(sys.modules[f"functions.{fl}"])
      modulecounter += 1 
  await ctx.send(f"reloaded {modulecounter} modules from functions and reloaded ide extension")

@bot.event
async def on_message(message):
  phr = f"{message.author.id}{message.channel.id}"
  if phr in var.msgqueue:
    var.msgqueue[phr].append(message.content)
  await bot.process_commands(message)

@bot.command()
async def help(ctx, *args):
  cmdlist = []
  ignore = []
  cogdict = defaultdict(list)
  for name in sorted(bot.cogs):
    cog = bot.get_cog(name)
    for cmdx in cog.walk_commands():
      cmd = bot.get_command(cmdx.qualified_name)
      if cmd.help:
        cogdict[name].append(f"**{cmdx.qualified_name}**")
        cmdlist.append(cmdx.qualified_name)
      cogdict[name].sort()
    if cogdict[name] == []:
      del cogdict[name]
  cogs = list(set(bot.cogs)-set(ignore))
  if not args:
    fields = list(zip([bot.get_cog(name).description for name in cogdict], [", ".join(cogdict[name]) for name in cogdict]))
    fields.append(["Try ++help <command> for specific command help.", f"Or ping <@375445489627299851>\n\n{len(bot.guilds)} servers and counting"])
    return await util.mbed(ctx, "C++Bot", "Hi there! I'm a bot that can run C++ inside Discord.\n\nType **++help all** or **++help <module>** (e.g. ++help ide) for more details.", fields = fields, thumbnail = bot.user.avatar_url)
  if args[0] == "all" or args[0].lower().title() in cogs:
    if args[0] == "all": lst = cogs
    else: lst = [args[0].lower().title()]
    for name in lst:
      fields = []
      cog = bot.get_cog(name)
      for cmdx in cog.walk_commands():
        cmd = bot.get_command(cmdx.qualified_name)
        if cmd.help:
          fields.append([cmdx.qualified_name, cmd.help])
      await util.mbed(ctx, name, cog.description, fields = fields, thumbnail = bot.user.avatar_url)
    return
  if args[0] not in cmdlist or not bot.get_command(args[0]).help:
    return await util.mbed(ctx, f"++{args[0]}", "Sorry, that command doesn't exist.", thumbnail = bot.user.avatar_url)
  return await util.mbed(ctx, f"++{args[0]}", bot.get_command(args[0]).help, thumbnail = bot.user.avatar_url)

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    return
  elif isinstance(error, commands.MissingRequiredArgument):
    ctx.message.content = "++help" + ctx.message.content.split()[0][1:]
    await bot.process_commands(ctx.message)
  elif isinstance(error, commands.CommandOnCooldown):
    await ctx.send(f"**{ctx.author}**, this command is on cooldown. Try again in {error.retry_after} seconds")
  else:
    msg = "An error has occurred!\n```" + "".join(traceback.format_exception(type(error), error, error.__traceback__, 999)) + "```"
    await ctx.send(msg[:2000])

server.server_run()
bot.run(os.getenv("TOKEN"), bot=True, reconnect=True)