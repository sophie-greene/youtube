from pytube import Playlist
from pytube import YouTube
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Function to download a single video


def download_video(video_url, download_path):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        stream.download(output_path=download_path)
    except Exception as e:
        print(f"Error downloading {video_url}: {e}")

# Main function to download playlist


def download_playlist(playlist_url, download_path='downloads', max_workers=4):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    playlist = Playlist(playlist_url)
    print(playlist)
    video_urls = playlist.video_urls

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(tqdm(executor.map(lambda url: download_video(
            url, download_path), video_urls), total=len(video_urls)))


# Example usage
if __name__ == "__main__":
    playlist_url = sys.argv[1]
    download_playlist(playlist_url)
