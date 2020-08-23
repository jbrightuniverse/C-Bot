import discord
from discord.ext import commands as bot

import asyncio
import os
import queue
import subprocess
import signal
import threading
import time
import random
import requests
import var

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
    if len(m.attachments):
      file = requests.get(m.attachments[0].url)
      ww = file.text
    else: ww = m.content
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
    if ctx.channel.id in self.channels:
      return await ctx.send(f"Sorry {ctx.author}, this channel is already in use. Please use another one. Thanks!")
    def handler(signum, frame):
      raise Exception("overtime")
    signal.signal(signal.SIGALRM, handler)
    try:
      self.channels.append(ctx.channel.id)
      await mbed(ctx, "Welcome to Discord C++", "To use the interpreter, type the code you wish to execute line by line (or many lines at once) into the chat.\nThere are also a few special commands (do **NOT** prefix with ++):", fields = [["run", "runs your code and then wipes the file you currently have (temporary behaviour)\ntype `run <arg1>, <arg2>, <argn>`(etc) to run program with command-line arguments"], ["view", "views the code you have so far in plaintext"], ["view num", "views the code you have so far, with line numbers"], ["edit 1", "moves the writing pointer to a specified line\nreplace 1 with the line number you wish to edit from"], ["overedit 1", "moves the writing pointer to a specified line, ignoring existing text until you call `edit` again\nreplace 1 with the start line number you wish to edit from"], ["pause", "disables all commands except `pause`, `view` and `exit` to allow you to send text without triggering the bot\nwhen paused, type `pause` again to unpause"],["stop", "ONLY FOR USE WHILE CODE IS RUNNING\nCancels execution of an ongoing program."], ["exit", "exits the program"]], footer = "ALPHA RELEASE\n\n©2020 James Yu.\nDISCLAIMER: I will not be held responsible for any injury, harm or misconduct arising from improper usage of the service.\nhttps://github.com/jbrightuniverse/C-Bot\nPart of the YuBot family of bots.")
      curfunc = []
      overwrite = False
      pause = False
      pointer = 0
      while True:
        val = await get22(ctx, self.bot)
        if val.lower() == "exit":
          self.channels.remove(ctx.channel.id)
          return await ctx.send("Exiting.")      
        if val == "pause":
          pause = not pause
          await ctx.send(["Unpaused IDE.", "Paused IDE. Type `pause` again to unpause."][pause])
        elif val.startswith("run") and not pause:
          args = [a.rstrip().lstrip() for a in val[4:].split(",")]
          program = "\n".join(curfunc)
          name = f"userdata/{str(time.time()).replace('.', '')}{random.randrange(1000)}"
          with open(f"{name}.cpp", "w") as f:
            f.write(program)
          curfunc = []
          msg = await ctx.send("Compiling...")
          ext = f"g++ {name}.cpp -o {name} -O2 -flto -march=native"
          signal.alarm(10)
          try:
            res = subprocess.Popen(ext.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            res.wait()
            b = res.communicate()[1]
            if b:
              await ctx.send(f"COMPILE ERROR:```\n{b.decode('utf-8')}```\nResetting.")
              try: os.remove(name)
              except: pass
              os.remove(f"{name}.cpp") 
              signal.alarm(0)
              continue
          except Exception as e:
            await ctx.send(f"ERROR: {e}\nResetting.")
            try: os.remove(name)
            except: pass
            os.remove(f"{name}.cpp") 
            signal.alarm(0)
            continue
          signal.alarm(0)
          await msg.edit(content =  "Finished compilng.")
          proc = subprocess.Popen([f"./{name}", "{name}.cpp"] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
          q = queue.Queue()
          t = threading.Thread(target=enqueue_output, args=(proc.stdout, proc.stderr, q))
          t.daemon = True
          t.start()
          operator = time.time()
          phr = f"{ctx.author.id}{ctx.channel.id}"
          var.msgqueue[phr] = []
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
            if len(var.msgqueue[phr]):
              nput = var.msgqueue[phr].pop(0)
              if nput == "stop":
                await ctx.send("Halting and resetting.")  
                break
          del var.msgqueue[phr]
          os.remove(name)
          os.remove(f"{name}.cpp") 
        elif val == "view":
          if not curfunc: await ctx.send("```No code yet!```")
          else:
            upperphr = "```cpp\n"+"\n".join(curfunc)
            await ctx.send(upperphr[:1996]+"\n```")
        elif val == "view num":
          if not curfunc: await ctx.send("```No code yet!```")
          else:
            code = curfunc
            code = [str(c[1]) + ". " + c[0]for c in zip(code, range(1, len(code)+1))]
            upperphr = "```cpp\n"+"\n".join(code)
            await ctx.send(upperphr[:1996]+"\n```")
        elif val.startswith("edit") and not pause:
          try: line = val.split()[1]
          except: line = str(len(curfunc)+1)
          if not line.isdigit() or int(line)-1 not in range(len(curfunc)+1):
            await ctx.send("ERROR: Invalid line number.")
            continue
          pointer = int(line)-1
          overwrite = False
          await ctx.send(f"Edit pointer set to line **{pointer+1}**. No overwrite.")
        elif val.startswith("overedit") and not pause:
          try: line = val.split()[1]
          except: line = str(len(curfunc)+1)
          if not line.isdigit() or int(line)-1 not in range(len(curfunc)+1):
            await ctx.send("ERROR: Invalid line number.")
            continue
          pointer = int(line)-1
          overwrite = True
          await ctx.send(f"Edit pointer set to line **{pointer+1}** with **overwrite existing lines** enabled. Call `edit {pointer+1}` to disable overwrite.")
        elif not pause:
          for line in val.split("\n"):
            if line.startswith("```"): continue
            if overwrite:
              try: curfunc[pointer] = line
              except: curfunc.insert(pointer, line)
            else:
              curfunc.insert(pointer, line)
            pointer += 1
          await ctx.send("Ok.")
        
    except Exception as e:
      self.channels.remove(ctx.channel.id)
      phr = f"{ctx.author.id}{ctx.channel.id}"
      if phr in var.msgqueue:
        del var.msgqueue[phr]
      await ctx.send(f"ERROR: ```{e}```\nExiting the command.")

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