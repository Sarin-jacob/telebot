import asyncio
import subprocess
async def get_available_formats(video_url):
    process = await asyncio.create_subprocess_shell(
        f"yt-dlp -F {video_url}",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    print(stdout.decode())
    return stdout.decode()

def select_format(formats_output):
    lines = formats_output.splitlines()
    selected_format = None

    for line in lines:
        parts = line.split()
        if len(parts) >= 3 and parts[-1].endswith('M'):
            try:
                format_code = parts[0]
                filesize_mb = int(parts[-1].replace('M', ''))

                if filesize_mb < 4096:
                    selected_format = format_code

            except ValueError:
                continue
    print(f"Selected format: {selected_format}")
    return selected_format

async def download_video(video_url, format_code, output_template):
    command = f"yt-dlp -f {format_code} -o '{output_template}' {video_url}"
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()

async def yt_down(video_url, output_template):
    formats_output = await get_available_formats(video_url)
    format_code = select_format(formats_output)

    if format_code:
        returncode, stdout, stderr = await download_video(video_url, format_code, output_template)
        print(stdout)
        if returncode != 0:
            return False, stderr.strip()
        return True, None
    else:
        return False, "No format found under 4GB!"
