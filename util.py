import discord
import random

async def mbed(ctx, upper, lower, fields = [], thumbnail = None, footer = None):
  embed = discord.Embed(title = upper, description = lower, color = random.randint(0, 0xffffff))
  for field in fields:
    embed.add_field(name = field[0], value = field[1], inline = False)
  if thumbnail:
    embed.set_thumbnail(url=thumbnail)
  if footer:
    embed.set_footer(text = footer)
  await ctx.send(embed = embed)