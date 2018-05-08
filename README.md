Scrape Discord channels

Installation (of requirements):
```
   pip install -r requirements.txt
```

**If you're on Ubuntu (example of how to install and run the scraper):**
```
	sudo apt install python3 python3-pip
	pip3 install -r requirements.txt
	python3 scrape_channels.py --token [token] -sid [server id]
```
It's important to note the ``3`` at the end of both pip and python here.


Usage:
```
   python scrape_channels.py --token [token] -sid [server id]
   or
   python scrape_channels.py --token [token] -sid [server id] -c [channel_id_1] [channel_id_2]
```

How to get server/channel id's:
https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-

*NOTE!* Can be used with user/password or with selfbots, but remember that these methods are disallowed,
and any such use may put your account in peril. The allowed way to scrape is to register a bot
to your discord server and use the bot's token.

If you still want to use a selfbot, here's how to retrieve a selfbot token:
https://github.com/TheRacingLion/Discord-SelfBot/wiki/Discord-Token-Tutorial


Requirements: discordy.py, asyncio, python3.4+

Saves reactions and "cleaned" messages to different files

Tested with:
python 3.4.3
python 3.6.3 (Ubuntu)
python 3.6.4