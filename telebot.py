#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
from os import path, system, getenv
import re
import unicodedata
from telethon import TelegramClient,events,Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import CreateChannelRequest ,EditPhotoRequest
from telethon.tl.types import InputChatUploadedPhoto,PeerChannel,PeerChat
from utils.imdbs import search_files
from utils.tmdb import TMDB,clean_name
import uuid

TELEGRAM_DAEMON_API_ID =None
TELEGRAM_DAEMON_API_HASH =None
TELEGRAM_DAEMON_CHANNEL=None
TELEGRAM_DAEMON_SESSION_PATH=''
CONFIG_FILE="telebot.cnf"
SESSION="telebot"
MOVIES_FILE_PATH = 'movies.txt'
TV_SHOWS_FILE_PATH = 'tv_shows.txt'

from utils.funcs import read_config,sendHelloMessage,log_reply,log_edit,finddetails,load_data,save_data,add_entry



if path.isfile(CONFIG_FILE):
    print("Using Config File.\n")
    config = read_config(CONFIG_FILE)
    TELEGRAM_DAEMON_API_ID = config.get('TELEGRAM_DAEMON_API_ID')
    TELEGRAM_DAEMON_API_HASH = config.get('TELEGRAM_DAEMON_API_HASH')
    TELEGRAM_DAEMON_CHANNEL = int(config.get('TELEGRAM_DAEMON_CHANNEL'))
    BOT_TOKEN = config.get('BOT_TOKEN')
    TMDB_API_KEY = config.get('TMDB_API_KEY')
else:
    print("config file Not Found creating one....\n")
    TELEGRAM_DAEMON_API_ID = input("Enter Telegram API ID: ")
    TELEGRAM_DAEMON_API_HASH = input("Enter Telegram API Hash: ")
    TELEGRAM_DAEMON_CHANNEL = input("Enter Telegram Channel ID: ")
    config = {
        'TELEGRAM_DAEMON_API_ID': TELEGRAM_DAEMON_API_ID,
        'TELEGRAM_DAEMON_API_HASH': TELEGRAM_DAEMON_API_HASH,
        'TELEGRAM_DAEMON_CHANNEL': TELEGRAM_DAEMON_CHANNEL,
    }
    with open(CONFIG_FILE, 'w') as file:
        for key, value in config.items():
            file.write(f"{key}={value}\n")
sessionName = SESSION
stringSessionFilename = f"{sessionName}.session"

def _getStringSessionIfExists():
    sessionPath = path.join(TELEGRAM_DAEMON_SESSION_PATH, stringSessionFilename)
    if path.isfile(sessionPath):
        try:
            with open(sessionPath, 'r') as file:
                session = file.read()
                print(f"Session loaded from {sessionPath}")
                return session
        except Exception as e:
            print(f"Error loading session file: {e}")
    return None

def getSession():
    if TELEGRAM_DAEMON_SESSION_PATH is None:
        return sessionName
    return StringSession(_getStringSessionIfExists())

def normalize_string(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii').lower()

def saveSession(session):
    if TELEGRAM_DAEMON_SESSION_PATH is not None:
        sessionPath = path.join(TELEGRAM_DAEMON_SESSION_PATH, stringSessionFilename)
        try:
            with open(sessionPath, 'w') as file:
                file.write(session.save())
            print(f"Session saved in {sessionPath}")
        except Exception as e:
            print(f"Error saving session file: {e}")

api_id = TELEGRAM_DAEMON_API_ID
api_hash = TELEGRAM_DAEMON_API_HASH
channel_id = TELEGRAM_DAEMON_CHANNEL

bot_client = TelegramClient('bot', api_id, api_hash)
bot_client.start(bot_token=BOT_TOKEN)
tmdb=TMDB(TMDB_API_KEY)
query_imdb_mapping = {}

cods='''
This script contains the following commands and their usage:

0. `cmd`: list all the commands. Usage: cmd
1. `cmdr, <command>`: run a command on the system. Usage: cmdr, <command>
2. `channelz`: create a channel with a profile picture and add The Botz. Usage: channelz
3. `roast`: restart the telebot service. Usage: roast
4. `sen:`: send a file to the sender. Usage: sen: <file_path>
5. `delch`: delete channels with specific keywords. Usage: delch <keywords to be added, seperated by space>
6. `sd:`: schedule a command to be sent multiple times. Usage: sd:<command> ev:<interval in minutes> fr:<times>
7. `mov <Moviename year>`: sent movie added message with button to update channel. Usage: mov <name>
8. `ser <Seriesname season>`: sent series added message with button to update channel. Usage: ser <name>
9. `update`: update the telebot script. Usage: update
'''

with TelegramClient(getSession(), api_id, api_hash).start() as client:
    saveSession(client.session)
    global peerChannel
    peerChannel = PeerChannel(channel_id)

    async def clearchannels():
        # List of keywords to look for in group names
        ndel=[] #list of channels/groups to never delete
        chy=await client.get_entity(PeerChannel(TELEGRAM_DAEMON_CHANNEL))
        ndel.append(chy.title.lower())
        with open('keywords.txt', 'r') as f:
            keywords = [line.strip() for line in f]
        # never leave curent channel

        # Get the list of your groups
        dialogs = await client.get_dialogs()

        for dialog in dialogs:
            # Check if the dialog is a chat (group or channel)
            if not dialog.is_group and dialog.is_channel:
                chat_name = normalize_string(dialog.name)

                if chat_name not in ndel :
                    # Check if any of the keywords are in the chat name
                    if any(keyword in chat_name for keyword in keywords):
                        # Leave the group
                        await dialog.delete()
                        await msgo(f'Left group: {chat_name}')

    async def msgo(mssg,hand=False,channel=peerChannel):
        # print(mssg)
        entity = await client.get_entity(channel)
        chunk_size=4096
        chunks = [mssg[i:i+chunk_size] for i in range(0, len(mssg), chunk_size)]
        for chunk in chunks:
            # print(chunk)     
            lmsg= await client.send_message(entity, chunk,parse_mode='markdown',link_preview=False,silent=True)
        if hand==True:
            await handler(events.NewMessage.Event(lmsg))
        return lmsg
    
    async def sdule(command: str, ev: int, times: int):
        entty = await client.get_entity(peerChannel)
        for i in range(times):
            # Calculate the scheduled time for each message
            scheduled_time = datetime.now() + timedelta(minutes=ev * i) - timedelta(hours=5, minutes=30)
            # Use the send_message function with the schedule parameter
            lo=await client.send_message(entty, command, schedule=scheduled_time)
    
    async def Bots2Channel(channel_name, profile_pic, bot_list):
        # Create the channel
        result = await client(CreateChannelRequest(
            title=channel_name,
            about='',
            megagroup=False
        ))

        channel_id = result.chats[0].id
        print(f"Channel created with ID: {channel_id}")

        # Add bots to the channel and promote them to admin
        for bot in bot_list:
            try:
                bot_entity = await client.get_input_entity(bot)
                await client.edit_admin(channel_id, bot_entity, is_admin=True)
                print(f"Bot '{bot}' added to channel '{channel_name}' and promoted to admin!")
            except Exception as e:
                print(f"Error adding bot '{bot}' to channel '{channel_name}': {e}")
     
        # Optionally, set the profile picture and add bots to the channel
        if profile_pic:
            file = await client.upload_file(profile_pic)
            await client(EditPhotoRequest(
                channel=channel_id,
                photo=InputChatUploadedPhoto(file)
            ))
        
        return channel_id
    async def start_bot_client():
        if not bot_client.is_connected():
            await bot_client.start(bot_token=BOT_TOKEN)
    
    def movie_or_tv(query):
        if query in ['movie', 'tv movie', 'short']:
            return False
        elif query in ['tv series', 'tv mini series', 'tv special', 'tv short']:
            return True
        return None
    
    @bot_client.on(events.NewMessage(pattern='/request( |@ProSearchUpdaterBot )(.+)'))
    async def request_handler(event):
        query=event.pattern_match.group(2).strip()
        cn=clean_name(query)
        mv, sr = search_files(cn)
        filtered_data = mv + sr
        snp=re.compile(r"[sS]\d{2}([eE]\d{2})?")
        sinfo=snp.search(query)
        sinfo = sinfo.group() if sinfo else None
        if len(filtered_data) == 0:
            await event.reply(f"No movie/tv found for {cn}")
            return f"No links found for {cn}"
        elif len(filtered_data) ==1:
            con=f"{filtered_data[0][1]} {filtered_data[0][2]} {sinfo if sinfo else ''}"
            add_entry(TV_SHOWS_FILE_PATH,con) if movie_or_tv(filtered_data[0][0]) else add_entry(MOVIES_FILE_PATH,con) 
            await event.reply(f"Added {con}")
            return f"added {con}"
        jn=re.sub(r"(?<=[_\s.])\d{4}", "", cn).strip()
        exact_title_matches = [i for i in filtered_data if i[1].lower() == jn.lower()]
        if len(exact_title_matches) == 1:
            con=f"{exact_title_matches[0][1]} {exact_title_matches[0][2]} {sinfo if sinfo else ''}"
            add_entry(TV_SHOWS_FILE_PATH,con) if movie_or_tv(exact_title_matches[0][0]) else add_entry(MOVIES_FILE_PATH,con) 
            await event.reply(f"Added {con}")
            return f"added {con}"
        elif len(exact_title_matches) > 1:
            # Check for exact title and year match
            exact_title_year_matches = [i for i in exact_title_matches if f"{i[2]}" in cn]
            if len(exact_title_year_matches) == 1:
                con=f"{exact_title_year_matches[0][1]} {exact_title_year_matches[0][2]} {sinfo if sinfo else ''}"
                add_entry(TV_SHOWS_FILE_PATH,con) if movie_or_tv(exact_title_year_matches[0][0]) else add_entry(MOVIES_FILE_PATH,con) 
                await event.reply(f"Added {con}")
                return f"added {con}"
            elif len(exact_title_year_matches) > 1:
                    filtered_data = exact_title_year_matches
            else:
                filtered_data = exact_title_matches
        elif len(filtered_data) > 10:
            filtered_data = filtered_data[:10]
        try:
            buttons = []
            for i in filtered_data:
                unique_id = str(uuid.uuid4())
                query_imdb_mapping[unique_id] = (movie_or_tv(i[0]), f"{i[1]} {i[2]} {sinfo if sinfo else ''}")
                buttons.append([Button.inline(f"{i[1]} ({i[2]}) [{i[0]}]", data=f"req:{unique_id}")])
            buttons.append([Button.inline(f"Close", data="none")])

        except Exception as e:
            await msgo(str(e))
        await event.reply("Search Results:", buttons=buttons)

    async def newfile(name:str ,channelid=-1002171035047,searchbot="ProSearchX1Bot",strt=1,imdb:str|None=None):
        if BOT_TOKEN: 
            await start_bot_client()
            entity = await bot_client.get_entity(channelid)
            name=name.replace("."," ")
            message=f"✅ **{name}**"
            name=name.split('#')[0].replace(' ', '%20').split('\n')[0]
            if imdb:
                # nm=name.replace('%20',' ')
                # message=message.replace(nm,f"[{nm}](https://www.imdb.com/title/{imdb})")
                link_text ='IMDb Link'
                link=f"** [{link_text}](https://www.imdb.com/title/tt{imdb})**"
                width = max(len(line) for line in message.split('\n'))
                message=f"{message}\n\n{' '*int((width +len(link_text)+2)/2)}{link}"
            search_url = f"tg://resolve?domain={searchbot}&text={name}"
            if strt==1:
                search_url = f"tg://resolve?domain={searchbot}&start=search_{name.replace('%20','_')}"
            butt=[Button.url("Click to Search",search_url)]
            await bot_client.send_message(entity, message,buttons=butt,link_preview=False,silent=True)
            return name.replace('%20',' ').replace('_',' ')
        else:
            print("Bot Token not found")
            await msgo("Bot Token not found\nAdd Bot Token in telebot.cnf file\nBOT_TOKEN=your_bot_token")

    async def fet(query:str,tv=False,channelid=-1002171035047,searchbot="ProSearchX1Bot",strt=1):
        # searchbot="ProWebSeriesBot" if tv else "ProSearchX1Bot"
        # strt= 0 if tv else 1
        tn=query.replace('.',' ').split('\n')[0].split('#')[0].strip()
        tn=clean_name(tn)
        if BOT_TOKEN: 
            await start_bot_client()
            entity = await bot_client.get_entity(channel_id)
            try:
                mv,sr=search_files(tn)
                filtered_data=sr if tv else mv
            except Exception as e:
                await msgo("Error: "+str(e))
            if len(filtered_data) == 0:
                await newfile(query,channelid=channelid,searchbot=searchbot,strt=strt)
                return f"No links found for {tn}"
            elif len(filtered_data) ==1:
                await newfile(query,channelid=channelid,searchbot=searchbot,strt=strt,imdb=filtered_data[0][3])
                return  f"added {tn}"
            # Check for exact title match
            jn=re.sub(r"(?<=[_\s.])\d{4}", "", tn).strip()
            exact_title_matches = [i for i in filtered_data if i[1].lower() == jn.lower()]
            # If exact title matches found
            if len(exact_title_matches) == 1:
                await newfile(query, channelid=channelid, searchbot=searchbot, strt=strt, imdb=exact_title_matches[0][3])
                return f"added {tn}"
            elif len(exact_title_matches) > 1:
                # Check for exact title and year match
                exact_title_year_matches = [i for i in exact_title_matches if f"({i[2]})" in tn]
                if len(exact_title_year_matches) == 1:
                    await newfile(query, channelid=channelid, searchbot=searchbot, strt=strt, imdb=exact_title_year_matches[0][3])
                    return f"added {tn}"
                elif len(exact_title_year_matches) > 1:
                    filtered_data = exact_title_year_matches
                else:
                    filtered_data = exact_title_matches

            elif len(filtered_data) > 10:
                filtered_data = filtered_data[:10]
            try:
                buttons = []
                for i in filtered_data:
                    unique_id = str(uuid.uuid4())
                    query_imdb_mapping[unique_id] = (query, i[3],tv)
                    buttons.append([Button.inline(f"{i[1]} ({i[2]})", data=f"add:{unique_id}")])
                buttons.append([Button.inline(f"Close", data="none")])
            except Exception as e:
                await msgo(str(e))
            await bot_client.send_message(entity, "Search Results:", buttons=buttons,silent=True)
            return '...'

    @bot_client.on(events.CallbackQuery())
    async def callback_handler(event):
        if event.data:
            unique_id = event.data.decode()
            if unique_id == "none": return await event.delete() 
            data = unique_id.split(':')
            cmd=data[0]
            unique_id = data[1]
            if cmd == "add":
                if unique_id not in query_imdb_mapping:return
                query, imdb_id,tv = query_imdb_mapping[unique_id]
                entity = await bot_client.get_entity(channel_id)
                searchbot= "ProWebSeriesBot" if tv else "ProSearchX1Bot"
                await newfile(query,channelid=-1001847045854,searchbot=searchbot,strt=1,imdb=imdb_id)
                await event.delete()
                tn=query.replace('.',' ').split('\n')[0].split('#')[0]
                await bot_client.send_message(entity, f"{tn} Added message sent",silent=True)
                del query_imdb_mapping[unique_id]
            elif cmd == "req":
                if unique_id not  in query_imdb_mapping: return
                tv, req = query_imdb_mapping[unique_id]
                filepath= TV_SHOWS_FILE_PATH if tv else MOVIES_FILE_PATH
                add_entry(filepath, req)
                await event.edit(f"Added request for {req}")
                del query_imdb_mapping[unique_id]



    @client.on(events.NewMessage())
    async def handler(event):
        if event.to_id != peerChannel:
            return     
        try:    
            if not event.media and event.message and not event.message.silent:
                command = event.message.message
                print(command)
                if command[0] == "/":
                    command = command[1:]
                valve=command
                command = command.lower()
                output = "Unknown command"
                if command == "cmd":
                    output = cods
                elif command[:4]=="sen:":
                    file_path = command[4:].strip()  # Extract the file path from the command
                    try:
                        await client.send_file(event.message.sender_id, file=file_path)
                        output = "File sent successfully"
                    except:
                        output = "File not found"
                elif "delch" in command[:5]:
                    if command != "delch ":
                        keywords = command[6:].split()
                    with open('keywords.txt', 'a') as f:
                        for keyword in keywords:
                            f.write(keyword + '\n')
                    # await queue.task_done()
                    await clearchannels()
                    output="cleared"
                elif "cmdr," in command:
                    if 'cmdr,' in valve:
                        cmdr=valve.split('cmdr, ')[-1]
                    else:
                        cmdr=valve.split('Cmdr, ')[-1]
                    if system(cmdr + " > puto.txt")!=0:
                        system(cmdr + " 2>> puto.txt")
                    g=open("puto.txt", "r")
                    output=g.read()
                    g.close
                    if output=='':
                        output="Command Run Successful"
                elif command=='reqs':
                    output="Requested Movies:\n"
                    for i in load_data(MOVIES_FILE_PATH):
                        output+=f"`{i}`"
                    output+="\n\nRequested TV Shows:\n"
                    for i in load_data(TV_SHOWS_FILE_PATH):
                        output+=f"`{i}`"
                elif command=="roast":
                    await msgo("trying to sta..")
                    system('systemctl --user restart telebot')
                elif command=="update":
                    system('cd ~/telebot && git pull')
                    await msgo("Downloaded New files..\nRestarting Service")
                    system('systemctl --user restart telebot')
                    output="Updated"
                elif "mez" == command[:3]:
                    output=''
                    prt=valve[4:]
                    for i in prt.split(','):
                        nm=await newfile(i,channelid=-1001847045854, strt=1)
                        output+=f"{nm} added message Sent.\n"
                elif "sez" == command[:3]:
                    output=''
                    prt=valve[4:]
                    for i in prt.split(','):
                        nm=await newfile(i,channelid=-1001847045854,searchbot="ProWebSeriesBot",strt=0)
                        output+=f"{nm} added message Sent.\n"
                elif "test" in  command:
                    output=""
                    prt=valve[5:]
                    # nm=await newfile(prt,channelid=-1002171035047,searchbot="ProSearchTestBot",strt=1)
                    # output+=f"{nm} added message Sent.\n"
                    # try:
                    await fet(prt)
                    output+="test done"
                    # except Exception as e:
                        # output+=str(e)
                elif "mov" == command[:3]:
                    output='Processing...'
                    prt=valve[4:]
                    for i in prt.split(','):
                        a=await fet(i,channelid=-1001847045854,searchbot="ProSearchX1Bot",strt=1)
                        output+=f"{a}\n"
                elif "ser" == command[:3]:
                    output='Processing...'
                    prt=valve[4:]
                    for i in prt.split(','):
                        a=await fet(i,tv=True,channelid=-1001847045854,searchbot="ProWebSeriesBot",strt=1)
                        output+=f"{a}\n"
                elif command=="channelz":
                    profile_pic = "0c5b070bd2ea83f9163cd.jpg"
                    channel_name ="Search Bot User 🔍 ⚓️ "
                    bot_list = ['ProSearch4Bot',
                                'ProSearch5Bot',
                                'ProSearchX1Bot',
                                'ProSeriesTelegramBot',
                                'ProWebSeriesBot',
                                'MProSearchBot',
                                'GroupProSearchBot']
                    ids=await Bots2Channel(channel_name,profile_pic,bot_list)
                    output=f"Bots added to channel `-100{ids}`"
                elif "sd:" in command:
                    mat=dict(finddetails(valve))
                    sd,ev,fr=mat.get("Sd") or mat.get("sd"),mat.get("ev"),mat.get("fr",1)
                    await sdule(sd,int(ev),int(fr))
                    output=f"{sd} scheduled for {fr} times, every {ev} minutes"
                await msgo(output)
                await event.delete()
        except:
            pass
    
    async def start():
        await sendHelloMessage(client, peerChannel)
        await client.run_until_disconnected()
    client.loop.run_until_complete(start())
