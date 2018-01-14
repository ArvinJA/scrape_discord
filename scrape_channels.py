import discord
import asyncio
import json
import sys, os
import argparse

from time import time
from datetime import datetime

# example: python scrape_channels.py --user [user] --password [password] -sid [server id]
parser = argparse.ArgumentParser(description='Scrape channel logs.')
parser.add_argument('--server_id', '-sid', type=str, help='the discord server id, required', required=True)
parser.add_argument('--token', '-t', type=str, help='token, used to log in')
parser.add_argument('--user', '-u', type=str, help='username, note: should not be used')
parser.add_argument('--password', '-p', type=str, help='password, note: should not be used')
parser.add_argument('--channels', '-c', type=str, nargs='*', help='channel ids')
parser.add_argument('--messages', '-m', type=int, help='number of messages to fetch per request')
parser.add_argument('--selfbot', action='store_true', help='is the connecting user a selfbot/regular user? note: should not be used')

SERVER_ID = ""
CHANNELS = []
SERVER = None
TIMESTAMP_STR = str(int(time()))
MESSAGES = 100 # default, use --messages or -m to change

client = discord.Client()

@client.event
@asyncio.coroutine
def on_ready():
	print('Logged in as: %s' % client.user.name)
	print('------')

	SERVER = client.get_server(SERVER_ID)
	channels = [SERVER.get_channel(cid) for cid in CHANNELS] if CHANNELS else SERVER.channels
	channels = list(filter(None, channels)) # Haven't encounterd a case where this is needed other than specifying incorrect channel id's
	for channel in sorted(channels, key=lambda c: c.position):
		if str(channel.type) == 'text' and SERVER.me.permissions_in(channel).read_message_history:
			yield from scrape_logs_from(channel)
			
	try:
		yield from client.close()
	except:
		pass
		
	print("Finished scraping %d channel(s)." % len(channels))
		
@asyncio.coroutine		
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
	
	print('scraping logs for %s' % channel.name)
	
	last = channel.created_at
	total = 0
	
	while True:
		gen = yield from client.logs_from(channel, after=last, limit=MESSAGES)
		messages = list(gen)
		if len(messages) == 0:
			break
			
		yield from write_messages(messages, f_messages, f_clean_messages, f_reactions)
		last = messages[0]
		total += len(messages)
		print(str(total) + " messages scraped")
		
	f_messages.close()
	f_reactions.close()
	f_clean_messages.close()
	
	print("\nDone writing messages for %s.\n" % channel.name)

@asyncio.coroutine
def write_messages(messages, f_messages, f_clean_messages, f_reactions):
	for message in messages[::-1]:
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
		}, sort_keys=True) + '\n')
		
		yield from process_reactions(message, f_reactions)
		
	
@asyncio.coroutine	
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

args = parser.parse_args()

if args.server_id:
	SERVER_ID = args.server_id
if args.channels:
	CHANNELS = args.channels
if args.messages:
	if args.messages > 0 and args.messages <= 100:
		MESSAGES = args.messages
	else:
		print("Max number of messages to return (1-100), using default: %d" % MESSAGES)

if args.selfbot:
	print("Using self-bots is not recommended.")
	if args.token:
		client.run(args.token, bot=False)
	elif args.user and args.password:
		print("Using user/password is not recommended.")
		client.run(args.user, args.password)
elif args.token:
	client.run(args.token)