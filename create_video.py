import os
import subprocess
from video_info import VideoInfo

def create_video(
        video_info: VideoInfo,
):
    render_intro(video_info.first_line, video_info.second_line)
    render_segments(video_info.path, video_info.segments)
    join_segments(video_info.output_file_name, video_info.segments)
    for i in range(len(video_info.segments)):
        try:
            os.remove(f"segment_{i}.mp4")
        except FileNotFoundError:
            pass


def cross_fade(
        video_1: str,
        audio_1: str,
        video_2: str,
        audio_2: str,
        out_name: str,
        offset: int
) -> str:
    """
    Creates filter to crossfade between two video streams and two audio streams.

    Parameters:
    video_1 (str): Name of first video stream
    audio_1 (str): Name of first audio stream
    video_2 (str): Name of second video stream
    audio_2 (str): Name of second audio stream
    out_name (str): Name for output streams
        - Output video will be named {out_name}v
        - Output audio will be named {out_name}a
    offset (int): Number of second into first video to start transition

    Returns:
    str containing filter to crossfade between clips
    """
    command = f"[{audio_1}][{audio_2}]acrossfade=d=1[{out_name}a];"
    command += f"[{video_1}]setpts=PTS-STARTPTS[{video_1}_pts];"
    command += f"[{video_2}]fade=in:st=0:d=1:alpha=1,setpts=PTS-STARTPTS+({offset}/TB)[{video_2}_pts];"
    command += f"[{video_1}_pts][{video_2}_pts]overlay[{out_name}v]"
    return command


def make_text_intro_video(
        fps: str,
        duration: int = 3,
        width: int = 1920,
        height: int = 1080,
        color: str = 'black'
) -> str:
    """
    Creates black video and null audio for use in making an intro.

    Parameters:
    fps (int): Desired fps
    duration (int): Duration of returned clip in seconds (default: 3)
    width (int): Width of returned clip in pixels (default: 1920)
    height (int): Height of returned clip in pixels (default: 1080)
    backgroundcolor (str): Background color (default: 'black')

    Returns:
    str containing inputs to be passed to ffmpeg
    """
    video = f'-f lavfi -t {duration} -r {fps} -i color={color}:{width}x{height}'
    audio = f'-f lavfi -t {duration} -i anullsrc'
    return ' '.join([video, audio])


def make_text_intro_filter(
        first_line: str,
        second_line: str,
        fontcolor: str = 'white',
        fontsize: int = 96
) -> str:
    """
    Takes two lines of text and returns filter to create background with that information over it.

    Parameters:
    first_line (str): first line of text
    second_line (str): second line of text
    fontcolor (str): Font color (default: 'white')
    fontsize (int): Font size (default: 96)

    Returns:
    str containing filter to create text intro
    """

    command = ""

    # Add name
    command += '[0]drawtext=' + ':'.join([
        f'text={first_line}',
        'x=(w-text_w)/2',
        'y=(h - 4 * text_h)/2',
        f'fontcolor={fontcolor}',
        f'fontsize={fontsize}',
    ]) + '[firstline];'

    # Add division
    command += '[firstline]drawtext=' + ':'.join([
        f'text={second_line}',
        'x=(w-text_w)/2',
        'y=(h - text_h)/2',
        f'fontcolor={fontcolor}',
        f'fontsize={fontsize}',
    ]) + '[introvid];'

    # Rename audio
    command += "[1:a]anull[introaudio]"

    return command


def render_intro(first_line: str, second_line: str):
    """
    Creates intro clip with name and division.
    Outputs video as segment_0.mp4.

    Parameters:
    first_line (str): first line of text
    second_line (str): second line of text
    """
    command = "ffmpeg " + make_text_intro_video("30")
    command += ' -filter_complex "' + make_text_intro_filter(first_line, second_line)
    command += '" -map [introvid] -map [introaudio] -y segment_0.mp4'
    subprocess.run(command, shell=True, capture_output=True)


def render_segments(video_path: str, segments: list):
    """
    Cuts video into multiple segments based on the times defined in segments.

    Parameters:
    video_path (str): path to source video
    segments (list): list of 2 int tuples containing start
        and end times for segments
    """
    for i, segment in enumerate(segments, start=1):
        start, stop = segment
        command = f'ffmpeg -hide_banner -ss {start} -i "{video_path}" -t {stop - start} -y -c copy segment_{i}.mp4'
        subprocess.run(command, shell=True, capture_output=True)


def join_segments(out_file_name: str, segments: list):
    """
    Joins segments produced in previous steps together with a crossfade

    Parameters:
    out_file_name (str): name of output file
    segments (list): list of 2 int tuples containing start
        and end times for segments
    """
    command = "ffmpeg -hide_banner "
    for i in range(0, len(segments) + 1):
        command += f"-i segment_{i}.mp4 "
    command += '-filter_complex "'
    for i in range(len(segments) + 1):
        command += f"[{i}:v]null[{i}v];[{i}:a]anull[{i}a];"

    prev_offset = 0
    segments.insert(0, (0, 3))
    for i in range(len(segments) - 1):
        start, stop = segments[i]
        prev_offset = stop - start + prev_offset - 1
        command += cross_fade(f"{i}v", f"{i}a", f"{i+1}v",
                              f"{i+1}a", f"{i+1}", prev_offset) + ";"
    command = command[:-1] + \
        f'" -map [{len(segments) - 1}v] -map [{len(segments) - 1}a] -y {out_file_name}.mp4'
    subprocess.run(command, shell=True, capture_output=True)


if __name__ == '__main__':
    segments = [(0, 98), (145, 233), (310, 395), (440, 470)]
    video_path = "IMG_1180.MOV"
    create_video(video_path, "Colin Gordon and Nishant Dash", "Mens A1", segments, "colin_and_nishant")
    segments = [(27, 95), (106, 112)]
    video_path = "nishant.MP4"
    create_video(video_path, "Nishant Dash", "PA1", segments, "nishant_poomsae")
    segments = [(0, 85), (125, 137), (175, 297), (336, 410)]
    video_path = "colin.MP4"
    create_video(video_path, "Colin Gordon", "Mens A1", segments, "colin_sparing")
