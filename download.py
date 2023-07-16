import os
from pytube import YouTube

#checks validity of URL // start of video processing pipeline
def validate_url(url):
    if url.startswith('https://www.youtube.com'):
        download_video(url)

#downloads YouTube Video
def download_video(url):
    youtube = YouTube(url,
                use_oauth=True,
                allow_oauth_cache=True)
    youtube.streams.filter(progressive=True, file_extension='mp4', only_video=True).first()

    file_name = input("Enter a file name for the downloaded video: ")
    if not file_name.endswith('.mp4'):
        file_name += '.mp4'

    stream = youtube.streams.get_by_itag(22)
    desktop_path = os.path.join(os.path.join(os.environ['HOME']), 'Desktop')
    stream.download(output_path=desktop_path, filename=file_name)

if __name__ == "__main__":
    yt_url = input("Enter the URL of the YouTube video you want to process: ")
    validate_url(yt_url)
