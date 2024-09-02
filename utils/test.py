import subprocess
import json

def get_media_info_ffprobe(url):
    command = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
        '-show_format', '-show_streams', url
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return json.loads(result.stdout)

# url = "https://example.com/path/to/media/file.mp4"
media_info = get_media_info_ffprobe(url)
print(json.dumps(media_info, indent=2))
