import discord
import asyncio
import json
import sys, os
import argparse

from time import sleep, time

# example: python scrape_channels.py --user [user] --password [password] -sid [server id]
parser = argparse.ArgumentParser(description='Scrape channel logs.')
parser.add_argument('--server_id', '-sid', type=str, nargs=1, help='the discord server id', required=True)
parser.add_argument('--user', '-u', type=str, nargs=1, help='username')
parser.add_argument('--password', '-p', type=str, nargs=1, help='password')
parser.add_argument('--token', '-t', type=str, nargs=1, help='token')
parser.add_argument('--sleep', '-s', type=float, nargs=1, help='sleep')
parser.add_argument('--channels', '-c', type=str, nargs='*', help='channel ids')
parser.add_argument('--messages', '-m', type=int, nargs=1, help='messages')

SERVER_ID = ""
CHANNELS = []
SERVER = None
TIMESTAMP_STR = str(int(time()))
SLEEP_TIME = 0.2 # default, use --sleep or -s to change
MESSAGES = 200 # default, use --messages or -m to change

client = discord.Client()

@client.event
@asyncio.coroutine
def on_ready():
	print('Logged in as')
	print(client.user.name)
	print('------')

	SERVER = client.get_server(SERVER_ID)
	channels = [SERVER.get_channel(cid) for cid in CHANNELS] if CHANNELS else SERVER.channels
	channels = filter(None, channels) # Haven't encounterd a case where this is needed other than specifying incorrect channel id's
	for channel in sorted(channels, key=lambda c: c.position):
		if str(channel.type) == 'text' and SERVER.me.permissions_in(channel).read_message_history:
			yield from scrape_logs_from(channel)

	print("\n\nFinished. CTRL+C to exit")
		
# source: https://stackoverflow.com/a/37630397/312332
def progress_bar(value, endvalue, bar_length=20):
	percent = float(value) / endvalue
	arrow = '-' * int(round(percent * bar_length)-1) + '>'
	spaces = ' ' * (bar_length - len(arrow))
	
	try:
		sys.stdout.write("\rComplete: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
		sys.stdout.flush()
	except:
		pass
		
def scrape_logs_from(channel):
	all_messages = []
	all_clean_messages = []
	all_reactions = []
	
	log_dir = 'logs/' + channel.server.name + '/' + TIMESTAMP_STR + '/'
	log_prefix = channel.id + '_' + channel.name + '-'
	log_suffix = '-log.txt'
	
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
	
	f_messages = open(log_dir + log_prefix + 'messages' + log_suffix, mode='w')
	f_clean_messages = open(log_dir + log_prefix + 'clean-messages' + log_suffix, mode='w')
	f_reactions = open(log_dir + log_prefix + 'reactions' + log_suffix, mode='w')
	
	print('scraping logs for ' + channel.name)
	
	gen = yield from client.logs_from(channel, limit=1)
	all_messages += list(gen)
	last = all_messages[0]
		
	while True:
		gen = yield from client.logs_from(channel, before=last, limit=MESSAGES)
		new_messages = list(gen)
		if len(new_messages) == 0:
			break
		all_messages += new_messages
		print('collected ' + str(len(all_messages)) + ' messages')
		last = new_messages[-1]
			
		sleep(SLEEP_TIME)
	
	print('writing '+ str(len(all_messages)) +' messages to log files for ' + channel.name)
	
	for i, message in enumerate(all_messages[::-1]):
		f_messages.write(json.dumps({
			'id': message.id,
			'timestamp': str(message.timestamp), 
			'edited_timestamp': str(message.edited_timestamp), 
			'author_id': message.author.id, 
			'author_name': message.author.name, 
			'content': message.content
		}, sort_keys=True) + '\n')
		
		f_clean_messages.write(json.dumps({
			'id': message.id,
			'clean_content': message.clean_content
		}) + '\n')
		
		yield from process_reactions(message, f_reactions)
		progress_bar(i, len(all_messages))
		
	f_messages.close()
	f_reactions.close()
	f_clean_messages.close()
	
	progress_bar(1, 1)
	print("\nDone writing messages.\n")
	
def process_reactions(message, f_reactions):
	for reaction in message.reactions:
		try:
			gen = yield from client.get_reaction_users(reaction)
			reaction_users = [user.id for user in gen]
			
			f_reactions.write(json.dumps({
				'channel_name': message.channel.name,
				'channel_id': message.channel.id,
				'message_id': message.id,
				'emoji': reaction.emoji if not reaction.custom_emoji else reaction.emoji.name,
				'count': reaction.count,
				'user_ids': reaction_users
			}, sort_keys=True) + '\n')
			
		except Exception as exc:
				print('\nException when processing reaction: {0}\n\nContinuing...\n'.format(exc))
				
		sleep(SLEEP_TIME)
	
args = parser.parse_args()

if args.server_id:
	SERVER_ID = args.server_id[0]
if args.channels:
	CHANNELS = args.channels
if args.sleep:
	SLEEP_TIME = args.sleep[0]
if args.messages:
	MESSAGES = args.messages[0]

if args.user and args.password:
	client.run(args.user[0], args.password[0])
elif args.token:
	client.run(args.token[0])
else:
	print("No login credentials...")