Scrape Discord channels

Installation (of requirements):
```
   pip install -r requirements.txt
```


Usage:
```
   python scrape_channels.py --token [token] -sid [server id]
   or
   python scrape_channels.py --token [token] -sid [server id] -c [channel_id_1] [channel_id_2]
```

*NOTE!* Can be used with user/password or with selfbots, but remember that these methods are disallowed,
and any such use may put your account in peril. The allowed way to scrape is to register a bot
to your discord server and use the bot's token.

Requirements: discordy.py, asyncio, python3.4+

Saves reactions and "cleaned" messages to different files

Tested with:
python 3.4.3
python 3.6.4