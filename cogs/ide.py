import discord
from discord.ext import commands as bot

import asyncio
import os
import queue
import subprocess
import signal
import threading
import shutil
import time
import random
import requests
import var
import traceback

from functions.filesys import *
from functions.edit import *

from io import StringIO
from util import *

def enqueue_output(out, out2, queue):
  try:
    for line in iter(out.readline, b''):
      queue.put(line)
  except: pass
  try: 
    for line in iter(out2.readline, b''):
      queue.put(line)
  except: pass
  out.close()
  out2.close()

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
    """Allows you to program C++ inside Discord. Type `++code` to start, and then type `help` for full docs."""
    if ctx.channel.id in self.channels:
      return await ctx.send(f"Sorry {ctx.author}, this channel is already in use. Please use another one. Thanks!")
    def handler(signum, frame):
      raise Exception("compilation taking too long")
    signal.signal(signal.SIGALRM, handler)
    foldername = str(ctx.author.id)
    self.channels.append(ctx.channel.id)
    try: os.mkdir(f"userdata/{foldername}")
    except: pass
    try:
      curfunc = {
        "/main.cpp":{
          "code": [],
          "overwrite": False,
          "pointer": 0
        }
      }
      curdata = {
        "curfile": "/main.cpp",
        "curdir": "/"
      }
      pause = False
      await mbed(ctx, "Discord C++", "Type `help` for a commands list.", footer = "©2020 James Yu.\nDISCLAIMER: I will not be held responsible for any injury, harm or misconduct arising from improper usage of the service.")
      while True:
        val = await get22(ctx, self.bot)
        if val.lower() == "exit":
          self.channels.remove(ctx.channel.id)
          return await ctx.send("Exiting.") 
        elif "z" + val.split()[0].lower() in editfunctions + sysfunctions and not pause:
          await globals()["z" + val.split()[0].lower()](ctx, val, curfunc, curdata)
        elif val.lower() == "pause":
          pause = not pause
          await ctx.send(["Unpaused IDE.", "Paused IDE. Type `pause` again to unpause."][pause])
        elif val.lower().startswith("view"):
          curfile = curdata["curfile"]
          await ctx.send(f"**{curfile}**")
          code = curfunc[curfile]["code"]
          if not code: await ctx.send("```No code yet!```")
          else:
            if val.lower().endswith("num"): todisplay = [str(c[1]) + ". " + c[0]for c in zip(code, range(1, len(code)+1))]
            else: todisplay = code
            upperphr = "```cpp\n"+"\n".join(todisplay)
            await ctx.send(upperphr[:1996]+"\n```")
        elif val.lower() == "save" and not pause:
          for file in curfunc:
            path = file.split("/")
            if path[-1] == "Makefile":
              replace_tabs = True
            else:
              replace_tabs = False
            del path[-1]
            folder = "/".join(path)
            try: os.makedirs(f"userdata/{foldername}{folder}")
            except: pass
            with open(f"userdata/{foldername}{file}", "w") as f:
              if not replace_tabs:
                text = "\n".join(curfunc[file]["code"])
              else:
                out = []
                for line in curfunc[file]["code"]:
                  if line.startswith("    "):
                    out.append('\t' + line[4:])
                  else: out.append(line)
                text = "\n".join(out)
              f.write(text)
          await ctx.send("Saved current workspace.")
        elif val.lower().startswith("make") and not pause:
          for file in curfunc:
            path = file.split("/")
            if path[-1] == "Makefile":
              replace_tabs = True
            else:
              replace_tabs = False
            del path[-1]
            folder = "/".join(path)
            try: os.makedirs(f"userdata/{foldername}{folder}")
            except: pass
            with open(f"userdata/{foldername}{file}", "w") as f:
              if not replace_tabs:
                text = "\n".join(curfunc[file]["code"])
              else:
                out = []
                for line in curfunc[file]["code"]:
                  if line.startswith("    "):
                    out.append('\t' + line[4:])
                  else: out.append(line)
                text = "\n".join(out)
              f.write(text)
          msg = await ctx.send("Saved current workspace. Compiling...")
          signal.alarm(600)
          res = None
          try:
            os.chdir(f"userdata/{foldername}")
            res = subprocess.Popen(["make"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            os.chdir("/home/runner/CBot")
            res.wait()
            b = res.communicate()
            if b[1]:
              tx = b[1].decode('utf-8').split("\n")
              if " Error " not in tx:
                await ctx.send(f"Warning:\n```{tx[:1978]}```")
              else:
                await ctx.send(f"COMPILE ERROR:\n```{tx[:1970]}```")
                signal.alarm(0)
                continue
          except:
            res.kill()
            await ctx.send(f"ERROR: {e}")
            signal.alarm(0)
            continue
          signal.alarm(0)
          await msg.edit(content = f"Finished compilng.\n```{b[0].decode('utf-8')}```")
        elif val.lower().startswith("./") and not pause:
          args = [a.rstrip().lstrip() for a in val.split(",")]
          try:
            os.chdir(f"userdata/{foldername}")
            proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
          except Exception as e:
            os.chdir("/home/runner/CBot")
            await ctx.send(f"ERROR: {e}")
            continue
          os.chdir("/home/runner/CBot")
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
              try: await ctx.send(line.decode('utf-8')[:2000])
              except: pass
              operator = time.time()
              """
              if proc.poll() != 0:
                await ctx.send("Finished. Resetting.")
                break
              """
            except queue.Empty:
              await asyncio.sleep(0)
            if time.time() - operator > 60:
              await ctx.send("Exceeded alotted unresponsive wait time of 60 seconds. Resetting.")
              proc.kill()
              break 
            if len(var.msgqueue[phr]):
              nput = var.msgqueue[phr].pop(0)
              if nput == "stop":
                await ctx.send("Halting and resetting.")
                proc.kill()  
                break
              elif cin:
                res = proc.communicate(input=nput.encode())[0]
                await ctx.send(f"Input received.\n{res.decode('utf-8')}")
          del var.msgqueue[phr]
        elif not pause:
          curfile = curdata["curfile"]
          for line in val.split("\n"):
            if line.startswith("```"): continue
            if curfunc[curfile]["overwrite"]:
              try: curfunc[curfile]["code"][curfunc[curfile]["pointer"]] = line
              except: curfunc[curfile]["code"].insert(curfunc[curfile]["pointer"], line)
            else:
              curfunc[curfile]["code"].insert(curfunc[curfile]["pointer"], line)
            curfunc[curfile]["pointer"] += 1
          await ctx.send("Ok.")
        
    except Exception as e:
      self.channels.remove(ctx.channel.id)
      if foldername in var.msgqueue:
        del var.msgqueue[foldername]
      phrase = ''.join(traceback.format_exception(type(e), e, e.__traceback__, 999)).replace("`", "\`")[:1967]
      await ctx.send(f"ERROR: ```{phrase}```Exiting the command.")

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