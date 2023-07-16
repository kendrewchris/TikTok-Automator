import os
import random
import ffmpeg 
from pytube import YouTube
 
"""
there should be three options in the processing of a video
1) entirety of video is retained and scaled down to fit mobile viewport
2) same as one but instead of being centered, video is vertically stacked with gameplay
3) video is cropped such that viewport is maximally covered
"""

def get_gameplay():
    #filepath
    secondary_folder = "secondary"
    mp4_files = [file for file in os.listdir(secondary_folder) if file.endswith('.mp4')]

    if not mp4_files:
        print("No MP4 files found in the 'secondary' folder.")
        return None

    random_file = random.choice(mp4_files)
    random_filepath = os.path.join(secondary_folder, random_file)

    return random_filepath

#checks validity of URL // start of video processing pipeline
def validate_url(url):
    if url.startswith('https://www.youtube.com'):
        download_video(url)

#downloads YouTube Video
def download_video(url):
    youtube = YouTube(url,
                use_oauth=True,
                allow_oauth_cache=True)
    youtube.streams.filter(progressive=True, file_extension='mp4').first()

    file_name = input("Enter a file name for the downloaded video: ")
    if not file_name.endswith('.mp4'):
        file_name += '.mp4'

    stream = youtube.streams.get_by_itag(22)

    stream.download(output_path='primary', filename=file_name)
    crop_video(f'primary/{file_name}')

# primary function: should take a downloaded mp4 as input from my project folder
# and output a bundle of short-form clips into a new directory with proper labeling
def crop_video(video_file):

    desktop_path = os.path.join(os.path.join(os.environ['HOME']), 'Desktop')
    short_path = os.path.join(desktop_path, 'short form videos')

    # String manipulation to get video title and create output folder name
    firstChar, lastChar = video_file.rfind('/') + 1, video_file.rfind('.') 
    video_title = video_file[firstChar:lastChar]
    output_dir = os.path.join(short_path, video_title + '-clips')
    clip_title = video_file[firstChar:lastChar].replace("-", " ").title()
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    else:
        print(f"The directory '{output_dir}' already exists. Skipping creation.")

    probe = ffmpeg.probe(video_file)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream is None:
        print("No video stream found in the input file.")
        return
    total_duration = float(probe['format']['duration'])

    # Determine the most reasonable time-duration
    chunk_duration = calculate_duration(total_duration)

    video_width = int(video_stream['width'])
    video_height = int(video_stream['height'])
    
    # Calculate the dimensions of the TikTok viewport
    tiktok_height = video_height
    tiktok_width = tiktok_height * 9 // 16

    # Calculate the cropping coordinates to center the TikTok viewport
    x_offset = (video_width - tiktok_width) // 2
    y_offset = (video_height - tiktok_height) // 2

    counter = 0

    for i in range(0, int(total_duration), chunk_duration):
        start = i
        if i + chunk_duration <= total_duration:
            end = i + chunk_duration
        else:
            end = total_duration
        counter += 1
        text = f'{clip_title} [Part {counter}]'

        input = ffmpeg.input(video_file, ss=start, t=end-start)
        #application of font type argumentation doesnt work
        video = (input.filter('scale', 1080, -1)  # Scale video to 1080 width, preserving aspect ratio
                .filter('pad', 1080, 1920, -1, -1, color='black')  # Add black bars to fill 1080x1920 viewport
                .filter('format', 'yuv420p')
                .filter('drawtext', text=text, x='(w-text_w)/2', y='(h/2-text_h)/2', fontfile='/Poppins/Poppins-ExtraBoldItalic.ttf', fontcolor='black', fontsize=60, box=1, boxcolor='white', boxborderw=10))

        audio = input.audio
        output = ffmpeg.output(audio, video, os.path.join(output_dir, f"{video_file[firstChar:lastChar]}-part{counter}.mp4")).run()
        
        if counter == 1:
            break

#calculates optimal short-form clip duration
def calculate_duration(total_duration):
    target_duration = 120  
    num_clips = total_duration // target_duration
    last_clip_duration = total_duration - (num_clips - 1) * target_duration

    while abs(last_clip_duration - target_duration) > 10:  # Adjust the threshold as needed
        if last_clip_duration > target_duration:
            target_duration += 1
        else:
            target_duration -= 1

        num_clips = total_duration // target_duration
        last_clip_duration = total_duration - (num_clips - 1) * target_duration
    return target_duration

if __name__ == "__main__":
    yt_url = input("Enter the URL of the YouTube video you want to process: ")
    validate_url(yt_url)

