import discord
from util import *

sysfunctions = ["zcd", "zrename", "zopen", "zremove", "zabout", "zrmdir", "zls"]

async def zcd(ctx, val, curfunc, curdata):
  dir = val[3:].lstrip()
  if not dir: 
    return await ctx.send("ERROR: Please provide a folderpath.")
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
  curdir = curdata["curdir"]
  curfile = curdata["curfile"]
  curfunc[curdir + name] = curfunc[curfile].copy()
  del curfunc[curfile]
  await ctx.send(f"Renamed **{curfile}** to **{curdir + name}**.")
  curdata["curfile"] = curdir + name

async def zopen(ctx, val, curfunc, curdata):
  name = val[5:].lstrip()
  if not name: 
    return await ctx.send("ERROR: Please provide a filename.")  
  curdir = curdata["curdir"]
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
    output = sorted([a.replace(curdir, "") for a in list(set(output))])
    text = f"**{curdir}**:\n" + "\n".join(output)
  else:
    text = "\n".join(sorted(output))
  await ctx.send(text[:2000])