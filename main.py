from youtubeApi import ascii_sanitize, top_level_comment, upload_video
from videoOverlay import create_video, get_sub_video
from playwright.sync_api import sync_playwright
from textToSpeech import text_to_speech
from screenshotGrabber import run
from redditApi import request
import shutil
import shelve
import ffmpeg
import re
import os
import json

regex = r"[^a-zA-Z0-9 .]"
pending_uploads = []

if __name__ == '__main__':
    with open("options.json", 'r') as options_file:
        options_json = json.load(options_file)
        background_footage_directory = options_json['background_footage_directory']
        subreddit = options_json['subreddit']
        time = options_json['time']
        video_count = options_json['video_count']
    # get the top posts of x sub for x time
    posts = request(subreddit, limit=video_count,  # TODO: Number of videos, sub, and time from command line argument
                    time=time)  # 6 videos is about youtube quota limit TODO: can easily request more
    print("Posts grabbed")
    with sync_playwright() as playwright_instance:
        for post_index, post in enumerate(posts):
            print("Playwright loaded")
            # ignores post if nsfw, should change later cuz doesn't really matter if it's just the tag, depending on sub
            if post.nsfw_tag is True or post.nsfw_img is True:
                continue

            responses = run(playwright_instance, post.post_url)
            video_images = []
            current_vid_length = 0

            # --- creating video file ---
            # put the post to go first in the video
            text_to_speech(post.post_title.replace(r'[\n]', ', '), "media/audio_tracks/postaudio.mp3")
            duration = ffmpeg.probe("media/audio_tracks/postaudio.mp3")['format']['duration']
            video_images.append(("media/post.png", duration, "media/audio_tracks/postaudio.mp3"))
            current_vid_length += (float(duration) + 1)
            # iterate through the comments and add all the comments that aren't replies to the video
            prev_comment_skipped = False
            for index, (path, text, indentation, upvote_count) in enumerate(responses):
                audio_file = "media/audio_tracks/comment{}audio.mp3".format(index)
                if prev_comment_skipped is True and len(text) * 0.05952 > float(duration):  # TODO: wow this is stupid
                    # 0.05 is a bad estimate of time / char
                    # if an estimate of the audios time is longer than file that was too long, skip this comment
                    # The dodgy estimate is an attempt to not have to make an entire audio file for an unused comment
                    continue
                if indentation == '1':
                    print("Running text to speech on text: {}".format(text.replace(r'[\n]', ', ')))
                    text_to_speech(text.replace(r'[\n]', ', '), audio_file)
                    duration = ffmpeg.probe(audio_file.format(index))['format']['duration']
                    if current_vid_length + float(duration) < 55:
                        video_images.append(("media/comments/comment{}.png".format(index), float(duration), audio_file))
                        current_vid_length += (float(duration) + 1)
                        prev_comment_skipped = False
                    else:
                        prev_comment_skipped = True
                        continue
                elif prev_comment_skipped is False:
                    pass
                # else:  # TODO: if upvote count is higher than top level comment and indentation is add duration to0
                # last comment to keep it on screen, then show second comment below the top one
            print(f"--- all {len(responses)} comments finished ---")
            video_file_name = re.sub(regex, '', post.post_title[:15])
            get_sub_video(background_footage_directory, input_video_length=566)  # vid length in seconds
            video_path = "media/createdVideos/{}.mp4".format(video_file_name)
            create_video(video_images, "media/subclip.mp4", video_path,
                         end_time=current_vid_length + 1)
            # --- uploading video to YouTube ---
            video_title = ascii_sanitize(post.post_title)[:100]
            video_desc = "Link to post: {}\n".format(post.post_url)
            print(video_title, video_path)
            response = upload_video(video_path, video_title, video_desc)
            print(response)
            with shelve.open("shelve/usedPosts.db") as db:
                db[post.post_id] = True  # Mark video as uploaded

            # --- clearing comment and audio files ---
            shutil.rmtree("media/audio_tracks")
            shutil.rmtree("media/comments")
            os.mkdir("media/audio_tracks")
            os.mkdir("media/comments")
            print(f"Video successfully uploaded at at length of {current_vid_length} with the title: {video_title}")
