import discord
import os
from util import *
import signal
sysfunctions = ["zcd", "zrename", "zopen", "zremove", "zabout", "zrmdir", "zls"]

async def zcd(ctx, val, curfunc, curdata):
  dir = val[3:].lstrip()
  if not dir: 
    return await ctx.send("ERROR: Please provide a folderpath.")
  if "." in dir and "../" not in dir:
    return await ctx.send("ERROR: Invalid filename character included.")
  curdir = curdata["curdir"]
  if "../" in dir:
    curdir = "/".join(curdir.split("/")[:-dir.count("../")-1])
  elif dir == "/" or dir == "~":
    curdir = "/"
  else:
    curdir += dir
  if not curdir.endswith("/"):
    curdir += "/"
  curdata["curdir"] = curdir
  await ctx.send(f"Working directory is now **{curdir}**.\nAny new files you manipulate will be in this directory.\nYou still currently have **{curdata['curfile']}** open (absolute path).")

async def zabout(ctx, val, curfunc, curdata):
  curfile = curdata['curfile']
  await mbed(ctx, f"Current File: **{curfile}**", "Absolute path.", fields = [["Edit Pointer", curfunc[curfile]['pointer']], ["Overwrite Mode On?", curfunc[curfile]['overwrite']], ["Working Directory", curdata['curdir']]])

async def zrename(ctx, val, curfunc, curdata):
  name = val[7:].lstrip() 
  if not name: 
    return await ctx.send("ERROR: Please provide a filename.")   
  if "Makefile" in name:
    return await ctx.send("ERROR: Invalid filename.")
  curdir = curdata["curdir"]
  curfile = curdata["curfile"]
  if curdir + name in curfunc or curdir + name in curdata["prime"]:
    return await ctx.send("ERROR: File exists.")
  curfunc[curdir + name] = curfunc[curfile].copy()
  del curfunc[curfile]
  await ctx.send(f"Renamed **{curfile}** to **{curdir + name}**.")
  curdata["curfile"] = curdir + name

async def zopen(ctx, val, curfunc, curdata):
  name = val[5:].lstrip()
  if not name: 
    return await ctx.send("ERROR: Please provide a filename.") 
  if "Makefile" in name:
    return await ctx.send("ERROR: Invalid filename.") 
  curdir = curdata["curdir"]
  if curdir + name in curdata["prime"]:
    return await ctx.send("ERROR: Primary filesystem file. Cannot be edited.")
  if curdir + name not in curfunc:
    curfunc[curdir + name] = {
      "code": [],
      "overwrite": False,
      "pointer": 0
    }
  curfile = curdir + name
  curdata["curfile"] = curfile
  await ctx.send(f"You are now editing **{curfile}**. Edit pointer is at line **{curfunc[curfile]['pointer']}** and overwrite is **{['off', 'on'][curfunc[curfile]['overwrite']]}**.")

async def zremove(ctx, val, curfunc, curdata):
  name = val[7:].lstrip()
  if not name: 
    return await ctx.send("ERROR: Please provide a filename.")   
  curdir = curdata["curdir"]
  curfile = curdata["curfile"]
  try: del curfunc[curdir + name]
  except:
    try:
      os.remove(curdata["path"]+curdir + name)
      curdata["prime"].remove(curdir+name)
      return await ctx.send(f"Deleted **{curdir + name}**. This was a primary filesystem file so you are still viewing **{curfile}** with current directory **{curdir}**")
    except: pass
    return await ctx.send("ERROR: File not found.")
  if curdir + name == curfile:
    keys = list(curfunc.keys())
    curdata["curdir"] = "/"
    if len(keys) == 0:
      curfunc["/main.cpp"] = {
        "code": [],
        "overwrite": False,
        "pointer": 0
      }
      curdata["curfile"] = "/main.cpp"
      return await ctx.send(f"Deleted **{curdir + name}**. As this was the last remaining file, regenerated **/main.cpp** as current file and set directory to **/**.")
    else:
      curdata["curfile"] = keys[0]
      return await ctx.send(f"Deleted **{curdir + name}**. Current file is now **{curdata['curfile']}** and current directory is now **/**.")
  await ctx.send(f"Deleted **{curdir + name}**.")

async def zrmdir(ctx, val, curfunc, curdata):
  name = val[6:].lstrip()
  if not name: 
    return await ctx.send("ERROR: Please provide a folderpath.")   
  curdir = curdata["curdir"]
  deleted = []
  for entry in curfunc.copy():
    if entry.startswith(curdir + name):
      del curfunc[entry]
      deleted.append(entry)
  delet = '\n'.join(deleted)
  curfile = curdata["curfile"]
  if curfile in deleted:
    keys = list(curfunc.keys())
    curdata["curdir"] = "/"
    if len(keys) == 0:
      curfunc["/main.cpp"] = {
        "code": [],
        "overwrite": False,
        "pointer": 0
      }
      return await ctx.send(f"Deleted the following {len(deleted)} files:\n**{delet}**\nAs no files are left, regenerated **/main.cpp** as current file and set directory to **/**.")
    else:
      curdata["curfile"] = keys[0]
      return await ctx.send(f"Deleted the following {len(deleted)} files:\n**{delet}**\nCurrent file is now **{curdata['curfile']}** and current directory is now **/**.")
  await ctx.send(f"Deleted the following {len(deleted)} files:\n**{delet}**")

async def zls(ctx, val, curfunc, curdata):
  def handler(signum, frame):
    raise Exception("compilation taking too long")
  signal.signal(signal.SIGALRM, handler)
  signal.alarm(2)
  try:
    curdir = curdata["curdir"]
    output = []
    for entry in curfunc:
      if val.endswith("all"):
        output.append(entry)
      elif entry.startswith(curdir):
        pathsize = len(curdir.split("/"))
        text = "/".join(entry.split("/")[:pathsize])
        if pathsize != len(entry.split("/")):
          text += "/"
        output.append(text)
    if not val.endswith("all"):
      output += ["/" + a + " (internal)" for a in os.listdir(curdata["path"] + curdir) if a not in curdir]
      output = sorted([a.replace(curdir, "") for a in list(set(output))])
      text = f"**{curdir}**:\n" + "\n".join(output)
    else:
      opath = "/"
      for root, dirs, files in os.walk(curdata["path"]):
        opath += os.path.basename(root)+"/"
        for file in files:
          if "." not in file: continue
          output.append(opath.replace(curdata["path"], "") + file + " (internal)")
      text = "\n".join(sorted(output))
    await ctx.send(text[:2000])
  except Exception as e:
    if "No such file or directory" in str(e): await ctx.send("Folder is empty.")
    else: await ctx.send(f"ERROR: Filesystem print failure.\nFull error: {e}")
  signal.alarm(0)
