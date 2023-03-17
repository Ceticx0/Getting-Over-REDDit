from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.fx.resize import resize
from imgResolution import img_res
import screenshotGrabber
import random


# full video is 626 seconds - 60 for max video length is 566
# -- get random clip from full video --
def get_sub_video(input_video, output_video="media/subclip.mp4", video_length=60, input_video_length=566):
    start_time = random.randint(0, input_video_length)
    # img_width, img_height = img_res(img_file)
    ffmpeg_extract_subclip(input_video, start_time, start_time + video_length,
                           targetname=output_video)


# -- overlay reddit post on top of image --
# (filename, duration, audiofile)
def create_video(comments: list, input_video: str = "media/subclip.mp4", output: str = "media/outputVideo.mp4", end_time=60):
    start_time = 0
    video = VideoFileClip(input_video)
    final_clips = [video]
    audio_clips = []
    for comment in comments:
        img_width, img_height = img_res(comment[0])
        final_clips.append(resize(ImageClip(comment[0])  # [0] = img file
                           .set_start(start_time)
                           .set_duration(comment[1])
                           .set_pos(("center", "center"))
                           , 925/img_width))
        audio_clips.append(AudioFileClip(comment[2]).set_start(start_time))
        # TODO: Add if to check for between comment time in tuple, to be used to differentiate replies to top level
        start_time += (float(comment[1]) + 1)  # 1 second in between comments
    final = CompositeVideoClip(final_clips)
    audio_final = final.set_audio(CompositeAudioClip(audio_clips)).set_end(end_time)
    audio_final.write_videofile(output)


if __name__ == '__main__':
    print("main executed")
    get_sub_video("D:/obs-videos/bgfootage.mp4")
    create_video(
        [("media/post.png", 4.358821, "media/audio.mp3"), ("media/comments/comment0.png", 3, "media/audio2.mp3"), ("media/comments/comment1.png", 5, "media/audio3.mp3")],
        output="testOutputVideo.mp4"
    )
