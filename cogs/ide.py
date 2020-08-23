import discord
from discord.ext import commands as bot

import asyncio
import os
import queue
import subprocess
import threading
import time
import random

from io import StringIO
from util import *

for file in os.listdir("userdata"):
  os.remove(f"userdata/{file}")

def enqueue_output(out, out2, queue):
  for line in iter(out.readline, b''):
      queue.put(line)
  for line in iter(out2.readline, b''):
      queue.put(line)
  out.close()

async def get22(ctx, bot):
  def check(m):
    nonlocal ww
    ww = m.content
    return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id
  ww = ""
  try:
    confirm1 = await bot.wait_for("message", timeout = 600, check = check)
  except:
    await ctx.send(f"Ok {ctx.author}, timed out.")
    return "exit"
  return ww

class Ide(bot.Cog):
  """:computer: ide"""

  def __init__(self, bot):
    self.bot = bot
    self.channels = []

  @bot.command()
  async def code(self, ctx):
    """Allows you to program C++ inside Discord. Type `++code` to start, and then follow on-screen instructions."""
    print(ctx.author)
    if ctx.channel.id in self.channels:
      return await ctx.send(f"Sorry {ctx.author}, this channel is already in use. Please use another one. Thanks!")
    try:
      self.channels.append(ctx.channel.id)
      await mbed(ctx, "Welcome to Discord C++", "To use the interpreter, type the code you wish to execute line by line (or many lines at once) into the chat.\nThere are also a few special commands:", fields = [["run", "runs your code and then wipes the file you currently have"], ["view (coming soon)", "views the code you have so far"], ["//", "allows you to send text without triggering the bot (send it in the same line)"],["exit", "exits the program"]], footer = "ALPHA RELEASE. Coming soon:\n· support for multiple files\n· undo command\n· view existing code command\n· support for stdin\n\n©2020 James Yu. https://github.com/jbrightuniverse/C-Bot\nPart of the YuBot family of bots.")
      curfunc = []
      while True:
        val = await get22(ctx, self.bot)
        if val.lower() == "exit":
          self.channels.remove(ctx.channel.id)
          return await ctx.send("Exiting.")      
        if val.startswith("//") or val.startswith("/*"):
          continue
        if val == "run":
          program = "\n".join(curfunc)
          name = f"userdata/{str(time.time()).replace('.', '')}{random.randrange(1000)}"
          with open(f"{name}.cpp", "w") as f:
            f.write(program)
          curfunc = []
          ext = f"g++ {name}.cpp -o {name} -O3 -flto -march=native"
          res = subprocess.Popen(ext.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
          res.wait()
          b = res.communicate()[1]
          if b:
            await ctx.send(f"COMPILE ERROR:\n{b.decode('utf-8')}\nResetting.")
            try: os.remove(name)
            except: pass
            os.remove(f"{name}.cpp") 
            continue
          proc = subprocess.Popen([f"./{name}", "{name}.cpp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
          q = queue.Queue()
          t = threading.Thread(target=enqueue_output, args=(proc.stdout, proc.stderr, q))
          t.daemon = True
          t.start()
          operator = time.time()
          while True:
            try:
              line = q.get_nowait()
              await ctx.send(line.decode('utf-8')[:2000])
              operator = time.time()
              if proc.poll() != 0:
                await ctx.send("Finished. Resetting.")
                break
            except queue.Empty:
              await asyncio.sleep(0)
            if time.time() - operator > 5:
              await ctx.send("Exceeded alotted unresponsive wait time of 5 seconds. Resetting.")
              break   
          os.remove(name)
          os.remove(f"{name}.cpp") 
        elif val == "view":
          if not curfunc: await ctx.send("```No code yet!```")
          else:
            upperphr = "```cpp\n"+"\n".join(curfunc)
            await ctx.send(upperphr[:1996]+"\n```")
        else:
          curfunc.append(val)
          await ctx.send("ok")
        
    except Exception as e:
      self.channels.remove(ctx.channel.id)
      await ctx.send(f"ERROR: {e}\nExiting the command.")

def setup(bot):
  bot.add_cog(Ide(bot))

"""
#include <iostream>
using namespace std;

int main() {
  cout << "Hello World!";
  return 0;
}
"""