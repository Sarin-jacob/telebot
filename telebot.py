#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
from os import execv, listdir, makedirs, path, remove, system, getenv
import subprocess
import sys
import re
import unicodedata
from telethon import TelegramClient,events,Button
from telethon.sessions import StringSession
from telethon.password import compute_check
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.functions.channels import CreateChannelRequest ,EditPhotoRequest,EditAdminRequest,EditCreatorRequest
from telethon.tl.functions.bots import SetBotCommandsRequest
from telethon.tl.types import InputChatUploadedPhoto,PeerChannel,BotCommand, BotCommandScopeDefault, InputMediaUploadedDocument,InputFile,ChatAdminRights
from utils.imdbs import search_files,gen4mId
from utils.medino import get_media_info
from utils.tmdb import TMDB,clean_name
from utils.reald import async_shot_bird, shot_bird
from utils.fasttelethon import fupload_file
from utils.ytdldr import p_links, yt_down
from humanize import naturalsize
from telethon.utils import get_attributes
from utils.funcs import read_config, sectostr,sendHelloMessage,finddetails,load_data,save_data,add_entry,extract_file,finddetails,stream_output,mystify
import uuid
import traceback
from asyncio import sleep
from info import PROGRESS_FREQUENCY,SESSION,TELEGRAM_DAEMON_SESSION_PATH,CONFIG_FILE,MOVIES_FILE_PATH,TV_SHOWS_FILE_PATH,PARALLEL_DOWNLOADS,PASS2fA

TELEGRAM_DAEMON_API_ID =None
TELEGRAM_DAEMON_API_HASH =None
TELEGRAM_DAEMON_CHANNEL=None
DOCKER= bool(getenv("DOCKER","False"))


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
# async def run_parallel(func, *args):
#     loop = asyncio.get_running_loop()
#     task = loop.create_task(func(*args))
#     return task
async def run_parallel(func, *args):
    task = asyncio.create_task(func(*args))
    return task

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
print(f"\033[1;32m\nTelebot is Up n Running on channel: {channel_id}\n\033[0m")
bot_client = TelegramClient('bot', api_id, api_hash)
bot_client.start(bot_token=BOT_TOKEN)
# tmdb=TMDB(TMDB_API_KEY)
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
7. `mov <Moviename year>`: sent movie added message with button to update channel. Usage: mov <name>#rest of message, each entry seperated by /
8. `ser <Seriesname season>`: sent series added message with button to update channel. Usage: ser <name>#rest of message, each entry seperated by /
9. `update`: update the telebot script. Usage: update
10. `comm <commands>`: change the bot commands. Usage: comm <command1:use,command2:use...>
11. `test <Moviename year>`: sent movie added message with button to test channel. Usage: test <name>
12. `giy <links>`: download files from links and upload to channel. Usage: giy <link...> each link in new line
13. `ypt <links>`: get links from yt playlist and upload to channel. Usage: ypt <link...> each link in new line
'''


async def update_progress(sent, total, file_name, sm, last_message, last_update_time):
    # Calculate progress
    progress = sent / total * 100
    sent_size = naturalsize(sent, binary=True)
    total_size = naturalsize(total, binary=True)

    # Create a progress bar with better visuals
    progress_bar_length = 25
    filled_length = int(progress_bar_length * sent / total)
    progress_bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)

    # Format the progress message with file size and progress percentage
    progress_message = (
        f"Uploading {file_name.split('/')[-1]}\n"
        f"[{progress_bar}] {progress:.2f}%\n"
        f"{sent_size} of {total_size}"
    )

    # Check if 5 seconds have passed since the last update
    current_time = datetime.now()
    if current_time - last_update_time[0] >= timedelta(seconds=PROGRESS_FREQUENCY) and progress_message != last_message[0]:
        await sm.edit(progress_message)
        last_message[0] = progress_message
        last_update_time[0] = current_time

    # Edit the final message when upload is complete
    if sent >= total:
        final_message = f"Finished uploading {file_name} ({total_size})"
        await sm.edit(final_message)
        last_message[0] = final_message

async def yt_downloader(text):
    mat = dict(finddetails(text))
    yt, nm = mat.get("yt") or mat.get("Yt"), mat.get("nm") or '%(title)s'
    await msgo(f"Link: {yt}")
    nm += '.%(ext)s'
    makedirs("downloads", exist_ok=True)
    await msgo("Downloading Youtube link")
    
    process = await asyncio.create_subprocess_shell(
        # f"yt-dlp --no-check-certificate -f 'bv*[filesize<3.7G]+ba/b[filesize<4G]' -N {PARALLEL_DOWNLOADS} -i -P 'downloads' -o '{nm}' --restrict-filenames --extractor-args youtube:formats=dashy '{yt}'",
        f"yt-dlp --no-check-certificate -f 'bv*[filesize<3.7G]+ba/b[filesize<4G]' -N {PARALLEL_DOWNLOADS} -i -P 'downloads' -o '{nm}' --restrict-filenames --no-warnings  '{yt}'",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Stream stdout and stderr asynchronously
    stdout_task = asyncio.create_task(stream_output(process.stdout, "stdout"))
    stderr_task = asyncio.create_task(stream_output(process.stderr, "stderr"))

    # Wait for the process to complete and the tasks to finish
    await process.wait()
    await stdout_task
    await stderr_task

    files = [f"downloads/{i}" for i in listdir("downloads")]
    sm = await msgo("Uploading files...")
    for fl in files: await uploood(fl, sm, caption=fl.split('/')[1], thumb="thumb.jpg")


async def up_bird(links: list, channelid=-1002171035047):
    thumb = "thumb.jpg"
    fnms = []
    dir='downloads'
    async def process_link(link):
        try:
            fl = await async_shot_bird(link, dir=dir)
            fnms.append(fl)
        except Exception as e:
            await msgo("Could not download file\nError: " + str(e))
            # Optional: You might want to add logging here instead of returning

    # Process all links concurrently
    await asyncio.gather(*[process_link(link) for link in links])
    await msgo("All files downloaded. Preparing for upload...")

    processed_files = []
    for j in fnms:
        try:
            extt = extract_file(j)
        except Exception as e:
            await msgo("Extraction Failed\nError: " + str(e))
            extt = None
        if extt:
            if isinstance(extt, list):
                processed_files.extend(extt)
            else:
                processed_files.append(extt)
        else:
            processed_files.append(j)
    fnms = processed_files
    uplds=''
    for i in fnms:
        if i.endswith('/'):fnms.remove(i)
        uplds+=f"{i.split('/')[-1]}\n"
    await msgo(f"Files to be uploaded: \n{uplds}")
    sm = await msgo("Uploading files...")

    try:
        if len(fnms) > 0:
            for fl in fnms:
                if fl ==None:continue
                if path.isfile(fl):
                    media_info_str = ""
                    # Get media info and update the caption
                    #if fl is audio run media info without metadata, if video run with metadata
                    if fl.endswith('.mp3') or fl.endswith('.m4a'):
                        duration, artist, title=await get_media_info(fl, metadata=False)
                        duration=sectostr(duration)
                        media_info_str=f"\n🎵 {'**'+artist+'**' if artist else ''}{' - **'+title+'**' if title else ''} [{duration}]"
                    elif fl.endswith('.sub') or fl.endswith('.srt'):
                        pass
                    else:
                        duration, qual, lang, subs  = await get_media_info(fl, metadata=True)
                        duration=sectostr(duration)
                        media_info_str = f"\n🎬 **{qual}** | ⏳ **{duration}**\n{'🔉: **'+ lang+'**' if lang != 'Unknown language' or lang == '' else '' }   \n{'**💬: ESUB**' if 'English' in subs else ''}"
                    updated_cap = f"{fl.split('/')[1]}\n{media_info_str}"
                    try:
                        await uploood(fl, sm, channelid, caption=updated_cap, thumb=thumb)
                    except Exception as e:
                        await msgo("Upload Failed\nError: " + str(e))
                else:
                    await msgo(f"Error: {fl} not found!!")
            #remove empty dirs if any in dir folder
            system(f'find {dir} -type d -empty -delete')
            system(f'rm -r {dir}/*.part*')
    except Exception as e:
        await msgo("Error: " + str(e))

async def con_warp():
    res=system('warp-cli connect')
    if res==0: await msgo("Connected Warp")
    if res!=0:
        await msgo("Error Connecting Warp")
        while res!=0:
            await sleep(2)
            res=system('warp-cli connect')
            if res==0:
                await msgo("Connected Warp")

async def dis_warp():
    res=system('warp-cli disconnect')
    if res==0: await msgo("Disconnected Warp")
    if res!=0:
        await msgo("Error Disconnecting Warp")
        while res!=0:
            await sleep(2)
            res=system('warp-cli disconnect')
            if res==0:
                await msgo("Disconnected Warp")

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
    async def change_commands(commands=None):
        cmds = [
            ('request', 'Request a movie or tv show'),
            ('movie', 'Request a movie'),
            ('tv', 'Request a tv show')
        ]
        if commands:
            commands = commands.split(',')
            commands = [(i.split(':')[0], i.split(':')[1]) for i in commands]
        else:
            commands = cmds

        await bot_client(SetBotCommandsRequest(
            scope=BotCommandScopeDefault(),
            lang_code='en',
            commands=[BotCommand(command=cmd, description=desc) for cmd, desc in commands]
        ))
    
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
        await client(EditAdminRequest(
        channel=channel_id,
        user_id='RockyBhayi755',
        admin_rights=ChatAdminRights(
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=True,
            anonymous=True,
            manage_call=True,
            other=True,
            manage_topics=True,
            post_stories=True,
            edit_stories=True,
            delete_stories=True
        ),
        rank='Don'))
        try:
            password_check = compute_check(await client(GetPasswordRequest()),PASS2fA)
            await client(EditCreatorRequest(
            channel=channel_id,
            user_id='RockyBhayi755',
            password=password_check
            ))
        except Exception as e:
            error_message = str(e)
            match = re.search(r'(\d+) seconds', error_message)
            if match:
                seconds = int(match.group(1))
                minutes = seconds / 60
                await msgo(f"try again in {minutes+1:.0f} mins")
            print(f"Error: {e}")
        return channel_id
    async def start_bot_client():
        if not bot_client.is_connected():
            await bot_client.start(bot_token=BOT_TOKEN)


    async def uploood(fl, sm, channelid=-1002171035047, last_message=[''], last_update_time=[datetime.now()], caption=None, thumb=None):
        async def progress_callback(sent, total):
            await update_progress(sent, total, fl, sm, last_message, last_update_time)

        try:
            with open(fl, "rb") as out:
                res = await fupload_file(client,out, progress_callback=progress_callback)
                
                
                attributes, mime_type = get_attributes(fl)
                # thumb = InputFile(thumb) if thumb and path.isfile(thumb) else None

                
                await client.send_file(
                    entity=channelid,
                    attributes=attributes,
                    force_document=True,
                    file=res,
                    thumb=thumb,
                    caption=caption
                )
            remove(fl)
        except Exception as e:
            await msgo("Upload error: " + str(e)) 
    def movie_or_tv(query):
        if query in ['movie', 'tv movie', 'short']:
            return False
        elif query in ['tv series', 'tv mini series', 'tv special', 'tv short']:
            return True
        return None
    
    @bot_client.on(events.NewMessage(pattern='/(request|movie|tv)( |@ProSearchUpdaterBot )(.+)'))
    async def request_handler(event):
        ty=event.pattern_match.group(1)
        query=event.pattern_match.group(3).strip()
        cn=clean_name(query)
        if ty=="request":
            mv, sr = search_files(cn)
            filtered_data = mv + sr
        elif ty=="movie":
            filtered_data,_=search_files(cn)
        elif ty=="tv":
            _,filtered_data=search_files(cn)
        snp=re.compile(r"[sS]\d{2}([eE]\d{2})?")
        sinfo=snp.search(query)
        sinfo = sinfo.group() if sinfo else None
        if len(filtered_data) == 0:
            await event.reply(f"No movie/tv found for {cn}")
            return f"No entry found for {cn}"
        elif len(filtered_data) ==1:
            con=f"{filtered_data[0][1]} {filtered_data[0][2]} {sinfo if sinfo else ''}"
            add_entry(TV_SHOWS_FILE_PATH,con) if movie_or_tv(filtered_data[0][0]) else add_entry(MOVIES_FILE_PATH,con) 
            await event.reply(f"Request added: {con}")
            return f"added {con}"
        jn=re.sub(r"(?<=[_\s.])\d{4}", "", cn).strip()
        exact_title_matches = [i for i in filtered_data if i[1].lower() == jn.lower()]
        if len(exact_title_matches) == 1:
            con=f"{exact_title_matches[0][1]} {exact_title_matches[0][2]} {sinfo if sinfo else ''}"
            add_entry(TV_SHOWS_FILE_PATH,con) if movie_or_tv(exact_title_matches[0][0]) else add_entry(MOVIES_FILE_PATH,con) 
            await event.reply(f"Request added: {con}")
            return f"added {con}"
        elif len(exact_title_matches) > 1:
            # Check for exact title and year match
            exact_title_year_matches = [i for i in exact_title_matches if f"{i[2]}" in cn]
            if len(exact_title_year_matches) == 1:
                con=f"{exact_title_year_matches[0][1]} {exact_title_year_matches[0][2]} {sinfo if sinfo else ''}"
                add_entry(TV_SHOWS_FILE_PATH,con) if movie_or_tv(exact_title_year_matches[0][0]) else add_entry(MOVIES_FILE_PATH,con) 
                await event.reply(f"Request added: {con}")
                return f"added {con}"
            elif len(exact_title_year_matches) > 1:
                    filtered_data = exact_title_year_matches
            else:
                filtered_data = exact_title_matches
        if len(filtered_data) > 10:
            filtered_data = filtered_data[:10]
        try:
            buttons = []
            for i in filtered_data:
                unique_id = str(uuid.uuid4())
                query_imdb_mapping[unique_id] = (movie_or_tv(i[0]), f"{i[1]} {i[2]} {sinfo if sinfo else ''}",event.sender_id)
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
            message=f"✅ **{mystify(name)}**"
            name=name.split('#')[0].replace(' ', '%20').split('\n')[0]
            if imdb:
                # nm=name.replace('%20',' ')
                # message=message.replace(nm,f"[{nm}](https://www.imdb.com/title/{imdb})")
                gen=gen4mId(imdb)
                link_text ='IMDB info'
                link=f"** [{link_text}](https://www.imdb.com/title/tt{imdb})**"
                message=f"{message}\n\n⭐️ {link}"
                if gen: message+=f"\n📽 **Genre:** `{gen}`"
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
                await msgo("XXError: "+str(e)+"\n",traceback.format_exc())
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
                query_imdb_mapping["none"] = (query, None,tv)
                buttons.append([Button.inline(f"No Link", data="add:none")])
                buttons.append([Button.inline(f"Close", data="none")])
            except Exception as e:
                await msgo(str(e))
            await bot_client.send_message(entity, "Search Results:", buttons=buttons,silent=True)
            return '...'
    async def latester(msg,tv=False):
        head='⭕️ Latest HD Releases. \n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n'
        mssg=await client.get_messages(-1002060127817,ids=3) if tv else await client.get_messages(-1002060127817,ids=2) 
        if len(mssg.text + f"✅ **{msg}**\n\n")>4096:
            mesg=head+f"\n✅ **{msg}**"
        else:
            mesg=head+f"\n✅ **{msg}**\n"+ mssg.text.replace(head,'') 
        await mssg.edit(mesg)

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
                tv, req,op = query_imdb_mapping[unique_id]
                print(f"Request for {req} by {op} clicked by {event.sender_id}")
                if (event.is_channel and event.chat_id != op) or (not event.is_channel and event.sender_id != op):
                    await event.answer("You are not the sender of this request")
                    return 
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
                output = valve
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
                elif "cmdr," in command[:5]:
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
                    execv(sys.executable, ['python'] + sys.argv)
                elif command=="reboot":
                    if DOCKER:system('sudo docker restart telebot')
                elif command=="update":
                    loca='cd /usr/src/app' if DOCKER else 'cd ~/telebot'
                    system(f'{loca} && git pull')
                    if DOCKER:execv(sys.executable, ['python'] + sys.argv)  
                    else: system('systemctl restart telebot --user')
                    await msgo("Downloaded New files..\nRestarting Service")
                    output="Updated"
                elif "yt:" in command:
                    # await msgo(f"{PARALLEL_DOWNLOADS=}")
                    # await run_parallel(yt_downloader,valve)
                    await yt_downloader(valve)
                    output=""
                elif "mov" == command[:3]:
                    prt=valve[4:]
                    output='Processing...'
                    for i in prt.split('/'):
                        a=await fet(i,channelid=-1001847045854,searchbot="ProSearchX1Bot",strt=1)
                        await latester(i)
                        output+=f"{a}\n"
                elif command=="ls":
                    output=subprocess.check_output('ls downloads', shell=True).decode()
                    if output=='':output="No files in downloads"
                elif "ser" == command[:3]:
                    output='Processing...'
                    prt=valve[4:]
                    for i in prt.split('/'):
                        a=await fet(i,tv=True,channelid=-1001847045854,searchbot="ProWebSeriesBot",strt=1)
                        await latester(i,tv=True)
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
                elif "comm"in command[:4]:
                    cmds=None if command[4:].strip()=="" else command[4:].strip() 
                    await change_commands(cmds)
                    output="Commands Changed"
                elif "test" in  command[:4]:
                    output=""
                    prt=valve[5:]
                    try:
                        await fet(prt,channnelid=channel_id)
                    except Exception as e:
                        output+=str(e)
                elif "giy" in  command[:3]:
                    prt=valve[4:]
                    prts=prt.split('\n')
                    prts=list(prts)
                    output="Processing Files to Download..."
                    await run_parallel(up_bird,prts)
                elif "ypt" in  command[:3]:
                    prt=valve[4:]
                    prts=prt.split('\n')
                    prts=list(prts)
                    async def plister(prts):
                        for i in prts:
                            output=f"{i}\n```\n"
                            links=await p_links(i)
                            output+=links
                            output+="\n```"
                            await msgo(output)
                    await run_parallel(plister,prts)
                    output=f"Processing {prts}.."
                elif command=="rm":
                    system(f'rm -r downloads/*')
                    output="Download Directories Cleared"
                elif "lest" in  command[:4]:
                    output=""
                    prt=valve[5:]
                    try:
                        # await change_commands()
                        await fet(prt,tv=True)
                    except Exception as e:
                        output+=str(e)
                elif "sd:" in command:
                    mat=dict(finddetails(valve))
                    sd,ev,fr=mat.get("Sd") or mat.get("sd"),mat.get("ev"),mat.get("fr",1)
                    await sdule(sd,int(ev),int(fr))
                    output=f"{sd} scheduled for {fr} times, every {ev} minutes"
                else:
                    return
                await msgo(output)
                await event.delete()
        except:
            pass
    
    async def start():
        await sendHelloMessage(client, peerChannel)
        await client.run_until_disconnected()
    client.loop.run_until_complete(start())
