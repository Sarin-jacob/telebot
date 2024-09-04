import asyncio
import subprocess
from info import PARALLEL_DOWNLOADS
from utils.funcs import stream_output
async def get_available_formats(video_url):
    process = await asyncio.create_subprocess_shell(
        f"yt-dlp -F {video_url}",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, serr = await process.communicate()
    print(stdout.decode(),serr.decode())
    return stdout.decode()

# def select_format(formats_output):
#     lines = formats_output.splitlines()
#     selected_format = None

#     for line in lines:
#         parts = line.split()
#         if len(parts) >= 3 and parts[-1].endswith('M'):
#             try:
#                 format_code = parts[0]
#                 filesize_mb = int(parts[-1].replace('M', ''))

#                 if filesize_mb < 4096:
#                     selected_format = format_code

#             except ValueError:
#                 continue
#     print(f"Selected format: {selected_format}")
#     return selected_format

def select_format(formats_output):
    if not formats_output:
        return None

    lines = formats_output.splitlines()
    selected_format = None

    for line in lines:
        parts = line.split('|')
        if len(parts) >= 2:
            size_info = parts[1].strip()
            size_str = size_info.split()[0]  # Get the size information
            
            if size_str.endswith('MiB') or size_str.endswith('GiB'):
                try:
                    format_code = parts[0].strip().split()[0]  # Get the format code
                    size_str = size_str.upper()

                    # Convert size to MB
                    if size_str.endswith('MIB'):
                        filesize_mb = float(size_str.replace('MIB', ''))
                    elif size_str.endswith('GIB'):
                        filesize_gb = float(size_str.replace('GIB', ''))
                        filesize_mb = filesize_gb * 1024  # Convert GiB to MB
                    else:
                        continue

                    if filesize_mb < 4096:
                        selected_format = format_code
                        break
                except ValueError:
                    continue

    print(f"Selected format: {selected_format}")
    return selected_format

async def download_video(video_url, format_code, dir,output_template):
    command = f"yt-dlp -f {format_code} -P '{dir}' -o '{output_template}' -N {PARALLEL_DOWNLOADS} {video_url}"
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()

async def yt_down(video_url,dir, output_template):
    formats_output = await get_available_formats(video_url)
    format_code = select_format(formats_output)

    if format_code:
        returncode, stdout, stderr = await download_video(video_url, format_code, dir,output_template)
        print(stdout)
        if returncode != 0:
            return False, stderr.strip()
        return True, None
    else:
        return False, "No format found under 4GB!"

async def p_links(playlist_url):
    try:
        process = await asyncio.create_subprocess_exec(
            'yt-dlp', '--flat-playlist', '--no-warnings', '--get-url', playlist_url,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # text=False
        )
        stdout_task = asyncio.create_task(stream_output(process.stdout, "stdout"))
        stderr_task = asyncio.create_task(stream_output(process.stderr, "stderr"))

        # Wait for the process to complete and the tasks to finish
        await process.wait()
        await stdout_task
        await stderr_task
        # Capture stdout and stderr
        stdout, stderr = await process.communicate()
        # Check if the process returned an error
        if process.returncode != 0:
            return f"Error fetching playlist: {stderr.strip()}"
        # Split the output into lines (each line is a video URL)
        links = stdout.decode().strip().split('\n')
        # Join the links into a single string
        return '\n'.join(links)
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"