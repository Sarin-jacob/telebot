from contextlib import suppress
from langcodes import Language
from asyncio import create_subprocess_exec, create_subprocess_shell
from asyncio.subprocess import PIPE

async def cmd_exec(cmd, shell=False):
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    return stdout, stderr, proc.returncode

async def get_media_info(path, metadata=False):
    """
    Retrieves media information from a specified file using `ffprobe` via a subprocess.
    
    Parameters:
    -----------
    path : str
        The file path of the media to analyze.
    metadata : bool, optional
        If `True`, returns additional metadata such as quality, language, and subtitle info. 
        If `False`, only duration, artist, and title are returned (default is `False`).

    Returns:
    --------
    tuple
        If `metadata` is `True`:
            (duration: int, quality: str, language: str, subtitles: str)
            - duration: The media duration in seconds.
            - quality: The video quality in "p" resolution format (e.g., "720p", "1080p").
            - language: Comma-separated string of audio language(s), if available.
            - subtitles: Comma-separated string of subtitle language(s), if available.
        If `metadata` is `False`:
            (duration: int, artist: str, title: str)
            - duration: The media duration in seconds.
            - artist: The artist's name from the media tags, if available.
            - title: The title of the media from the tags, if available.
    
    Exceptions:
    -----------
    Returns `(0, None, None)` or `(0, "", "", "")` on failure or if the file does not exist.
    Prints an error message if `ffprobe` fails or if the file is not found.
    
    Example:
    --------
    # With metadata enabled (video-specific details)
    duration, qual, lang, subs = await get_media_info('/path/to/video.mp4', metadata=True)
    
    # Without metadata (audio details)
    duration, artist, title = await get_media_info('/path/to/audio.mp3', metadata=False)
    """
    try:
        result = await cmd_exec(["ffprobe", "-hide_banner", "-loglevel", "error", "-print_format",
                                 "json", "-show_format", "-show_streams", path])
        if res := result[1]:
            print(f'Media Info FF: {res}')
    except Exception as e:
        print(f'Media Info: {e}. Mostly File not found!')
        return (0, "", "", "") if metadata else (0, None, None)
    ffresult = eval(result[0])
    fields = ffresult.get('format')
    if fields is None:
        print(f"Media Info Sections: {result}")
        return (0, "", "", "") if metadata else (0, None, None)
    duration = round(float(fields.get('duration', 0)))
    if metadata:
        lang, qual, stitles = "", "", ""
        if (streams := ffresult.get('streams')) and streams[0].get('codec_type') == 'video':
            qual = int(streams[0].get('height'))
            qual = f"{144 if qual <= 144 else 240 if qual <= 240 else 360 if qual<= 360 else 480 if qual <= 480 else 540 if qual <= 540 else 720 if qual <= 720 else 1080 if qual <= 1080 else 2160 if qual <= 2160 else 4320 if qual <= 4320 else 8640}p"
            for stream in streams:
                if stream.get('codec_type') == 'audio' and (lc := stream.get('tags', {}).get('language')):
                    with suppress(Exception):
                        lc = Language.get(lc).display_name()
                    if lc not in lang:
                        lang += f"{lc}, "
                if stream.get('codec_type') == 'subtitle' and (st := stream.get('tags', {}).get('language')):
                    with suppress(Exception):
                        st = Language.get(st).display_name()
                    if st not in stitles:
                        stitles += f"{st}, "
        return duration, qual, lang[:-2], stitles[:-2]
    tags = fields.get('tags', {})
    artist = tags.get('artist') or tags.get('ARTIST') or tags.get("Artist")
    title = tags.get('title') or tags.get('TITLE') or tags.get("Title")
    return duration, artist, title


# dur, qual, lang, subs = get_media_info(up_path, True)
