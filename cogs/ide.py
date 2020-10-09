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
import tempfile
import pwd

from functions.filesys import *
from functions.edit import *

from collections import defaultdict

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

def enqueue_output2(out, out2, queue, queue2):
  try:
    for line in iter(out.readline, b''):
      queue.put(line)
  except: pass
  try:
    for line in iter(out2.readline, b''):
      queue2.put(line)
  except: pass
  out.close()
  out2.close()


async def get22(ctx, bot, users):
  def check(m):
    nonlocal ww
    if len(m.attachments):
      type =  m.attachments[0].url.split(".")[-1].split("?")[0]
      if not type.startswith("png") and not type.startswith("bmp") and not type.startswith("jpeg") and not type.startswith("jpg") and not type.startswith("txt"):
        ww = "upload fail"
      elif not m.content.lower().startswith("upload"):
        ww = f"upload {int(time.time())}.{type} {m.attachments[0].url}"
      else:
        filename = m.content.split(".")
        if len(filename) == 1: 
          filename.append(f"{int(time.time())}.{type}")
          filename[0] += " "
          m.content = " ".join(filename)
        else: 
          filename[-1] = type
          m.content = ".".join(filename)
        ww = m.content + " "+ m.attachments[0].url
    else: ww = m.content
    return m.channel.id == ctx.channel.id and m.author.id in users
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
    self.channels = {}

  @bot.command()
  async def chelp(self, ctx):
    await globals()["zhelp"](ctx, "zhelp", None, None) 

  @bot.command()
  async def sessions(self, ctx):
    await ctx.send(len(self.channels.keys()))

  @bot.command()
  async def leave(self, ctx):
    """Leaves a coding channel if you have joined it."""
    user = ctx.author.id
    if user in self.channels:
      await ctx.send(f"A ghost channel has been constructed in <#{channel}>. Be sure to exit.")
      return await ctx.send("ERROR:```\nGhost channel constructed. See https://www.youtube.com/watch?v=ub82Xb1C8os to fix.\n```") 
    for user in self.channels:
      if ctx.author.id in self.channels[user]["users"]:
        self.channels[user]["users"].remove(ctx.author.id)
        return await ctx.send(f"Ok {ctx.author}, you have left this session.")
    await ctx.send(f"{ctx.author}, you are not in this session.")

  @bot.command()
  async def code(self, ctx):
    """Allows you to program C++ inside Discord. Type `++code` to start, and then type `help` for full docs."""
    userlist = []
    for u in self.channels:
      userlist += self.channels[u]["users"]
    if ctx.author.id in self.channels or ctx.author.id in userlist:
      if ctx.author.id in self.channels: channel = self.channels[ctx.author.id]["channel"]
      else: 
         for u in self.channels:
           if ctx.author.id in self.channels[u]["users"]:
             channel = self.channels[u]["channel"]
             break
      return await ctx.send(f"Sorry {ctx.author}, you already have a session running in <#{channel}>.")
    if ctx.channel.id in [self.channels[a]["channel"] for a in self.channels]:
      for user in self.channels:
        if self.channels[user]["channel"] == ctx.channel.id:
          await ctx.send(f"<@{user}>, do you authorize this user to join? Type `yes` to confirm or `no` to not.")
          res = await get22(ctx, self.bot, [user])
          if res != "yes":
            return await ctx.send("Denied.")
          else:
            self.channels[user]["users"].append(ctx.author.id)
            break
      return await ctx.send(f"Added {ctx.author} to channel.") 
    self.channels[ctx.author.id] = {
      "channel": ctx.channel.id,
      "users": []
    }
    def handler(signum, frame):
      raise Exception("compilation taking too long")
    signal.signal(signal.SIGALRM, handler)
    user = str(ctx.author.id)
    try: os.mkdir(f"/home/james/userdata/{user}")
    except: pass
    foldername = f"/home/james/userdata/{user}"
    res = subprocess.Popen(f"sudo chmod 777 {foldername}", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell = True)
    res.wait()
    #f = res.communicate()
    #await ctx.send(f)
    #foldername = foldername[0].decode('utf-8')
    #os.chmod("/home/james/userdata/", 777)
    #os.chmod(foldername, 777)
    res = subprocess.Popen(f"sudo useradd -s /bin/bash -d {foldername} -M {user}".split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    res.wait()
    res = subprocess.Popen(f"sudo setquota -u {user} 200M 200M 50 50 /".split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    res.wait()
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
        "curdir": "/",
        "path": foldername,
        "prime": []
      }
      pause = True
      await mbed(ctx, "Discord C++", "Type `help` for a commands list.\nThe IDE is currently paused. Type `code` to start programming in `main.cpp`")
      while True:
        checkval = await get22(ctx, self.bot, self.channels[ctx.author.id]["users"]+[ctx.author.id])
        val = checkval.replace("++", "")
        if val.lower() == "exit" or val.lower() == "stop":
          shutil.rmtree(foldername)
          res = subprocess.Popen(f"sudo userdel {user}".split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
          res.wait()
          try: del self.channels[ctx.author.id]
          except: pass
          return await ctx.send("Exiting.")
        elif val.lower() in ["yes", "no", "++leave", "++code"]:
          pass

        elif "z" + val.split()[0].lower() in editfunctions + sysfunctions:
          if val.split()[0].lower() == "help" or not pause:
            await globals()["z" + val.split()[0].lower()](ctx, val, curfunc, curdata)
          else:
            await ctx.send("IDE is currently paused. Type `pause` or `code` to unpause the IDE.")

        elif val.lower() == "pause" or val.lower() == "code":
          pause = not pause
          await ctx.send(["Unpaused IDE. Type `exit` or `stop` to exit.", "Paused IDE. Type `pause` again to unpause."][pause])


        elif val.lower().startswith("view"):
          if len(val.split()) == 2 and os.path.isfile(f"{foldername}{curdata['curdir']}" + val.split()[1]):
            await ctx.send(file = discord.File(f"{foldername}{curdata['curdir']}" + val.split()[1]))
            continue
          curfile = curdata["curfile"]
          await ctx.send(f"**{curfile}**")
          code = curfunc[curfile]["code"]
          if not code: await ctx.send("```No code yet!```")
          else:
            todisplay = code.copy()
            indentcounter = 0
            for i in range(len(todisplay)):
              if todisplay[i].count("}") > todisplay[i].count("{"):
                indentcounter -= 4
              todisplay[i] = " "*indentcounter + todisplay[i]
              if todisplay[i].count("{") > todisplay[i].count("}"):
                indentcounter += 4*(todisplay[i].count("{"))
            if val.lower().endswith("num"): todisplay = [str(c[1]).rjust(2) + ". " + c[0] for c in zip(todisplay, range(1, len(todisplay)+1))]
            upperphr = "```cpp\n"+"\n".join(todisplay)
            await ctx.send(upperphr[:1996]+"\n```")


        elif val.lower().startswith("upload") and not pause:
          if val == "upload fail":
            await ctx.send("ERROR: Unsupported filetype for direct upload.")
            continue
          args = val.split()
          if (len(args) != 3):
            await ctx.send("ERROR: Please specify a name.")
            continue
          if curdata['curdir']+args[1] in curdata["prime"] or curdata['curdir']+args[1] in curfunc:
            await ctx.send("ERROR: Filename in use.")
            continue
          url = args[2]
          res = requests.get(url, stream=True)
          os.makedirs(f"{foldername}{curdata['curdir']}", exist_ok = True)
          with open(f"{foldername}{curdata['curdir']}"+args[1], 'wb') as f:
            for line in res.iter_content():
              await asyncio.sleep(0)
              f.write(line)
          curdata["prime"].append(curdata['curdir']+args[1])
          await ctx.send(f"Saved file to **{curdata['curdir']+args[1]}**.")


        elif val.lower().startswith("make") and not pause:
          for file in curfunc:
            path = file.split("/")
            del path[-1]
            folder = "/".join(path)
            os.makedirs(f"{foldername}{folder}", exist_ok = True)
            with open(f"{foldername}{file}", "w") as f:
              out = []
              for line in curfunc[file]["code"]:
                out.append(line)
                check = " ".join(line.split())
                if "int main" in check and "}" in check:
                  check = check.split("{")
                  check[1] = "std::atexit(exitfunc);" + check[1]
                  check ="{".join(check)
                  out.insert(0, 'void exitfunc() {std::cout << std::endl; std::cout << "221TERMINATEIMMEDIATELY" << std::endl;}')
                  out.insert(0, "#include <cstdlib>")
                  out.insert(0, "#include <iostream>") 
                elif "int main(" in check or "int main (" in check and "}" not in check:
                  out.append("std::atexit(exitfunc);")
                  out.insert(0, 'void exitfunc() {std::cout << std::endl; std::cout << "221TERMINATEIMMEDIATELY" << std::endl;}')
                  out.insert(0, "#include <cstdlib>")
                  out.insert(0, "#include <iostream>")
              text = "\n".join(out)
              f.write(text)
          shutil.copy2("Makefile", f"{foldername}/Makefile")
          if val.lower() == "make 221":
            shutil.copytree("cs221util", f"{foldername}/cs221util")
          msg = await ctx.send("Saved current workspace. Compiling...")
          signal.alarm(600)
          flag = None
          res = None
          b = None
          os.chdir(foldername)
          res = subprocess.Popen(["make","clean"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
          res.wait()
          try:
            res = subprocess.Popen(["make"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            os.chdir("/home/james/cbot")
            while True:
              if res.poll() == None:
                await asyncio.sleep(0)
              else:
                b = res.communicate()
                tx = b[1].decode('utf-8')
                if not f"{tx}": break
                if " Error " not in tx and "Stop." not in tx:
                  await ctx.send(f"Warning:\n```{tx[:1978]}```")
                  break
                else:
                  await ctx.send(f"COMPILE ERROR:\n```{tx[:1970]}```")
                  signal.alarm(0)
                  os.remove(f"{foldername}/Makefile")
                  if val.lower() == "make 221":
                    shutil.rmtree(f"{foldername}/cs221util")
                  for file in curfunc:
                    os.remove(f"{foldername}{file}")
                  flag = True
                  break
            if flag: continue

          except:
            res.kill()
            await ctx.send(f"ERROR: {e}")
            signal.alarm(0)
            os.remove(f"{foldername}/Makefile")
            if val.lower() == "make 221":
              shutil.rmtree(f"{foldername}/cs221util")
            for file in curfunc:
              os.remove(f"{foldername}{file}")
            continue
          signal.alarm(0)
          os.remove(f"{foldername}/Makefile")
          if val.lower() == "make 221":
            shutil.rmtree(f"{foldername}/cs221util")
          for file in curfunc:
            os.remove(f"{foldername}{file}")
          await msg.edit(content = f"Finished compilng.\n```{b[0].decode('utf-8')}```")


        elif val.lower().startswith("run") and not pause:
          if val.endswith("cin"):
            val = val[:-3]
            cin = True
          else:
            cin = False
          args = " ".join(val.split()[1:])
          try:
            #res = subprocess.Popen(f"sudo chown -R {user}:{user} {foldername}/*", stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            #res.wait()
            #b = res.communicate()
            #await ctx.send(b)
            #res = subprocess.Popen(f"runuser -l {user} -c 'cd {foldername}'", stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            #res.wait()
            #res = subprocess.Popen(f"runuser -l {user} -c 'ls'", stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            #res.wait()
            #b = res.communicate()
            #await ctx.send(b)
            proc = subprocess.Popen(f"runuser -l {user} -c './main {args}'", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
          except Exception as e:
            #os.chdir("/home/james/cbot")
            await ctx.send(f"PROCESS LAUNCH ERROR: {e}")
            continue
          await ctx.send("Running. Type `stop` to stop the program.")
          #os.chdir("/home/james/cbot")
          q = queue.Queue()
          t = threading.Thread(target=enqueue_output, args=(proc.stdout, proc.stderr, q))
          t.daemon = True
          t.start()
          operator = time.time()
          phr = f"{ctx.author.id}{ctx.channel.id}"
          var.msgqueue[phr] = []
          outcounter = 0
          while True:
            try:
              line = q.get_nowait()
              if "221TERMINATEIMMEDIATELY" in line.decode('utf-8'):
                await ctx.send("Program complete.")
                break
              try: await ctx.send(line.decode('utf-8')[:2000])
              except: pass
              outcounter+= 1
              operator = time.time()
            except queue.Empty:
              await asyncio.sleep(0)
            if time.time() - operator > 600:
              await ctx.send("Exceeded alotted unresponsive wait time of 600 seconds. Halting.")
              proc.kill()
              break 
            if outcounter == 15:
              await ctx.send("Exceeded alotted message buffer of 15 messages. Halting.")
              proc.kill()
              break
            if len(var.msgqueue[phr]):
              nput = var.msgqueue[phr].pop(0)
              if nput == "stop":
                await ctx.send("Halting.")
                proc.kill()  
                break
              elif cin:
                res = proc.communicate(input=nput.encode())[0]
                await ctx.send(f"Input received.\n{res.decode('utf-8')}")
          del var.msgqueue[phr]


        elif not pause:
          curfile = curdata["curfile"]
          exceptions = ["popen", "tmp", "##", "execl", "execlp", "execle", "execv", "execvp", "execvpe", "system", "fork", "vfork", "clone", "posix_spawn", "sigaction", "dlsym", "dlopen", "chmod", "chown", "fchdir", "chroot", "setuid"]
          for line in checkval.split("\n"):
            if any(x in line.lower() for x in exceptions):
              await ctx.send("Terminated codewrite. One of your lines contains a banned function or phrase.")
              break
            if line.startswith("```"): continue
            if curfunc[curfile]["overwrite"]:
              try: curfunc[curfile]["code"][curfunc[curfile]["pointer"]] = line.lstrip()
              except: curfunc[curfile]["code"].insert(curfunc[curfile]["pointer"], line.lstrip())
            else:
              curfunc[curfile]["code"].insert(curfunc[curfile]["pointer"], line.lstrip())
            curfunc[curfile]["pointer"] += 1
          pointer = curfunc[curfile]["pointer"]
          curfile = curdata["curfile"]
          code = curfunc[curfile]["code"]
          await ctx.send(f"Added line to **{curfile}**.")
          todisplay = code.copy()
          indentcounter = 0
          for i in range(len(todisplay)):
            if todisplay[i].count("}") > todisplay[i].count("{"):
              indentcounter -= 4
            todisplay[i] = " "*indentcounter + todisplay[i]
            if todisplay[i].count("{") > todisplay[i].count("}"):
              indentcounter += 4*(todisplay[i].count("{"))
          todisplay = [str(c[1]).rjust(2) + ". " + c[0] for c in zip(todisplay, range(1, len(todisplay)+1))]
          base = max(0, pointer-5)
          top = min(pointer+3, len(code))
          toinsert = todisplay[base:top]
          if base != 0: toinsert.insert(0, "...")
          if top != len(code): toinsert.append("...")
          upperphr = "```cpp\n"+"\n".join(toinsert)
          await ctx.send(upperphr[:1996]+"\n```")


    except Exception as e:
      shutil.rmtree(foldername)
      res = subprocess.Popen(f"sudo userdel {user}".split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
      res.wait()
      try: del self.channels[ctx.author.id]
      except: pass
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
