Scrape Discord channels

Installation (of requirements):
```
   pip install -r requirements.txt
```


Usage:
```
   python scrape_channels.py --user [user] --password [password] -sid [server id]
   or
   python scrape_channels.py --token [token] -sid [server id]
   or
   python scrape_channels.py --user [user] --password [password] -sid [server id] -c [channel_id_1] [channel_id_2]
```

Requirements: discordy.py, asyncio, python3
(only tested with python 3.4.3 and discord.py 0.16.8)

Saves reactions and "cleaned" messages to different files