import os
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import yt_dlp as youtube_dl
import sys
from pytube import YouTube
# Function to download a single video using yt-dlp


def download_video_no_cred(video_url, download_path):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        stream.download(output_path=download_path)
    except Exception as e:
        print(f"Error downloading {video_url}: {e}")

def download_video(video_info, download_path, ydl_opts):
    try:
        ydl_opts['outtmpl'] = os.path.join(download_path, video_info['name'])
        if os.path.exists(ydl_opts['outtmpl']):
            return 
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_info['webpage_url']])
    except Exception as e:
        download_video_no_cred(video_info['webpage_url'], download_path)
        print(f"Error downloading {video_info['name']}: {e}")

# Main function to download playlist


def get_name(ep, title, ext):
    return f"{title.strip()}{ep}.{ext.strip()}"

def download_playlist(playlist_url, download_path='downloads', max_workers=8):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    ydl_opts = {
        'format': 'best',
        'username': None,
        'password': None,
        'verbose': False,
    }

    # Read credentials from file
    try:
        with open('.cred', 'r') as file:
            lines = file.readlines()
            ydl_opts['username'] = lines[0].strip().split(':')[1]
            ydl_opts['password'] = lines[1].strip().split(':')[1]
    except FileNotFoundError:
        print("Credentials file not found. Make sure '.cred' exists and is formatted correctly.")
        return

    # Extract video URLs from the playlist
    try:
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        result = ydl.extract_info(playlist_url, download=False)
        video_urls = [{'name': get_name(i+1, e['title'], e['video_ext']), 'webpage_url': e['webpage_url']}
                                for i, e in enumerate(result['entries'])]
    except Exception as e:
        print(f"Error extracting playlist information: {e}")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(tqdm(executor.map(lambda url: download_video(
            url, download_path, ydl_opts), video_urls), total=len(video_urls)))


# Example usage
if __name__ == "__main__":
    playlist_url = sys.argv[1]
    download_playlist(playlist_url)
