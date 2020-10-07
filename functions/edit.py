import discord
from util import *

editfunctions = ["zdelete", "zedit", "zhelp"]

async def zdelete(ctx, val, curfunc, curdata):
  curfile = curdata["curfile"]
  code = curfunc[curfile]["code"]
  line = val.split()
  if len(line) < 2:
    return await ctx.send("ERROR: Please specify a line number.")
  if not line[1].isdigit() or int(line[1])-1 not in range(len(code)+1):
    return await ctx.send("ERROR: Invalid first line number.")
  if len(line) == 3:
    if not line[2].isdigit() or int(line[2])-1 not in range(len(code)+1):
      return await ctx.send("ERROR: Invalid last line number.")
  else:
    line.append(line[1])
  for i in range(int(line[2])-int(line[1]) + 1):
    del curfunc[curfile]["code"][int(line[1])-1]
  await ctx.send(f"Removed lines **{int(line[1])}** to **{int(line[2])}**.")

async def zedit(ctx, val, curfunc, curdata):
  curfile = curdata["curfile"]
  code = curfunc[curfile]["code"]
  try: line = val.split()[1]
  except: line = str(len(code)+1)
  if not line.isdigit() or int(line)-1 not in range(len(code)+1):
    return await ctx.send("ERROR: Invalid line number.")
  pointer = curfunc[curfile]["pointer"] = int(line)-1
  if val.lower().endswith("overwrite"):
    curfunc[curfile]["overwrite"] = True
    extra = f" with **overwrite existing lines** enabled. Call `edit {pointer+1}` to disable overwrite."
  else:
    curfunc[curfile]["overwrite"] = False
    extra = f". No overwrite."
  await ctx.send(f"Edit pointer set to line **{pointer+1}**{extra}")

async def zhelp(ctx, val, curfunc, curdata):
  await mbed(ctx, "Welcome to Discord C++", "To use the interpreter, first type `++code` to launch the bot and then `code` to start coding.\nThen type the code you wish to execute line by line (or many lines at once) into the chat.\nThere are also a few special commands (do **NOT** prefix with ++):", 
  fields = [
  ["make", "compiles your code\ntype `make 221` to include cs221util"],
  ["run", "runs your code\ntype `run <arg1>, <arg2>, <argn>`(etc) to run program with command-line arguments"], 
  ["view", "views the code you have so far in plaintext"], 
  ["view num", "views the code you have so far, with line numbers"], 
  ["view filename.ext", "views a non-code file (a file in the internal filesystem, such as an image)]"],
  ["edit 1", "moves the writing pointer to a specified line\nreplace 1 with the line number you wish to edit from"], 
  ["edit 1 overwrite", "moves the writing pointer to a specified line, ignoring existing text until you call `edit` again\nreplace 1 with the start line number you wish to edit from"], 
  ["pause", "disables all commands except `pause`, `view` and `exit` to allow you to send text without triggering the bot\nwhen paused, type `pause` again to unpause"],
  ["stop", "ONLY FOR USE WHILE CODE IS RUNNING\nCancels execution of an ongoing program.\nONLY USABLE BY THE OWNER OF A SESSION"], 
  ["delete 1", "deletes a specified line\nreplace 1 with the line you want to delete"],
  ["delete 1 4", "deletes all lines from first to next specified line numbers (inclusive)\nreplace 1 with first line and 4 with last line"],
  ["open filename.ext", "opens a new or existing file of a specified name\nreplace filename.ext with your filename"],
  ["remove filename.ext", "removes a file of a specified name\nreplace filename.ext with your filename"],
  ["cd directory", "changes your working directory folder to a specified directory\nreplace directory with directory name, which can be new or existing\ntype `../` as the directory to move up one level\ntype `~` to go to root"],
  ["rename filename.ext", "renames the file **you are currently viewing** to a specified filename\nreplace filename.ext with your filename\nif you include slashes, the file will automatically be moved to the specified folder"],
  ["about", "explains the current state of the program"],
  ["ls", "lists all files in the current directory\ntype `ls all` to view all files"],
  ["upload filename.ext", "uploads a file to the internal filesystem\nsupports images and txt files only\nthese files cannot be edited nor renamed, but can be deleted"],
  ["++leave", "leaves a session that someone else is running"],
  ["++code", "if you use this command where someone else is already coding, they will be able to add you to their session and share files"],
  ["exit", "exits the program"]], footer = "©2020 James Yu.\nDISCLAIMER: I will not be held responsible for any injury, harm or misconduct arising from improper usage of the service.\nPart of the YuBot family of bots.")
