# C++Bot

This is a bot that runs C++ for use in Discord servers. That's basically it.
Most instructions are available when you activate the bot and call `++code`

# Installation

Link to the original bot: https://discord.com/api/oauth2/authorize?client_id=746953990910246962&permissions=100352&scope=bot

## 1. Discord
Create a Discord account and go to the [Developer Portal](https://discord.com/developers/applications/me).
Create a new application, then go to `bot` and create a new bot.
Copy the token, you'll need it later.

## 2a. repl.it
The bot is designed to be used inside repl.it, a cloud-based online IDE. As such, it is equipped with files for automatic package installation with Poetry, and a web server designed to keep the bot running longer.

1. Create a new repl through "import from github" and link this repl.
2. Once loaded, create a file called `.env` and paste `TOKEN=mytoken` where mytoken is the token you made earlier.
3. Hit run. A server window should pop up on the upper right. Copy the URL.
4. Go to [Uptime Robot](https://uptimerobot.com), make an account, and create a new HTTPs monitor, pasting the URL you just saved. Set polling interval to something more frequent than an hour.

## 2b. local install
Alternatively, you could install this on your local machine.

1. Download the repository as zip and unzip to your computer.
2. Download Python 3.8 if you don't have it already.
3. Replace the call to `os.getenv("TOKEN")` in `main.py` with your bot token from before.
4. Remove the calls to `import server` and `server.server_run()`. Feel free to delete `server.py` or any of the packaging files.
5. Open a terminal with your Python install and run `pip install discord.py`
6. Run `python3 main.py` (or just `main.py` on some systems).

## 3. Get the bot
Go back to the developer portal and go to `Oauth2`.
Scroll down, click the checkbox beside `bot`.
Below, hit checkboxes beside `Send Messages`, `Attach Files` and `Read Message History`.
Hit copy beside the link.
Paste the link into your browser to add the bot to servers you own.

That's it!

