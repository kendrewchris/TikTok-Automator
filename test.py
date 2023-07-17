import os
import random
from moviepy.editor import *
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

# primary function: should take filepath of downloaded mp4 as input 
# and output a bundle of short-form clips into output directory on desktop in new folder
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

    #get duration for primary
    primary_video = VideoFileClip(video_file)
    total_duration = primary_video.duration
    
    # get duration for secondary
    gameplay_video = get_gameplay()
    secondary_video = VideoFileClip(gameplay_video)
    game_duration =  secondary_video.duration
    
    # Calculate the dimensions of the TikTok viewport
    tiktok_height = primary_video.size[1]
    tiktok_width = tiktok_height * 9 // 16

    # Resize and center gameplay video within the TikTok viewport
    gameplay_width = secondary_video.size[0]
    gameplay_height = secondary_video.size[1]
    gameplay_aspect_ratio = gameplay_width / gameplay_height

    if gameplay_aspect_ratio > 9 / 16:  # Gameplay video is wider
        gameplay_height = tiktok_height
        gameplay_width = int(tiktok_height * gameplay_aspect_ratio)
    else:  # Gameplay video is taller
        gameplay_width = tiktok_width
        gameplay_height = int(tiktok_width / gameplay_aspect_ratio)

    counter = 0

    # Determine the most reasonable time-duration
    chunk_duration = calculate_duration(total_duration)

    for i in range(0, int(total_duration), chunk_duration):
        start = i
        if i + chunk_duration <= total_duration:
            end = i + chunk_duration
        else:
            end = total_duration
        counter += 1
        
        #text_clip = TextClip(f'{clip_title} [Part {counter}]', fontsize = 30, color = 'black')
        #text_clip = text_clip.set_pos('center').set_duration(1)

        #calculate timestamps for gameplay
        game_start = random.uniform(0, game_duration-chunk_duration)

        # Load the video clips using moviepy's VideoFileClip
        primary_clip = VideoFileClip(video_file).subclip(start, end)
        gameplay_clip = VideoFileClip(gameplay_video).subclip(game_start, game_start + chunk_duration)

        #get audio from primary video
        audio = primary_clip.audio

        all_clips = [[primary_clip], [gameplay_clip]]
        final = clips_array(all_clips).resize((1080,1920)).set_audio(audio)
        #final = CompositeVideoClip([final, text_clip])

        # Write the stacked video to the output file
        output_path = os.path.join(output_dir, f"{video_title}-part{counter}.mp4")
        final.write_videofile(output_path, codec="libx264", audio_codec="aac")

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
