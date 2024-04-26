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
        offset: int,
        filter: list[str]
):
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
    filter (list): list of complex filters

    Modifies:
    filter: adds cross fade filters to filter
    """
    filter += [
        f"[{audio_1}][{audio_2}]acrossfade=d=1[{out_name}a]",
        f"[{video_1}]setpts=PTS-STARTPTS[{video_1}_pts]",
        f"[{video_2}]fade=in:st=0:d=1:alpha=1,setpts=PTS-STARTPTS+({offset}/TB)[{video_2}_pts]",
        f"[{video_1}_pts][{video_2}_pts]overlay[{out_name}v]"
        ]


def make_text_intro_video(
        fps: str,
        duration: int = 3,
        width: int = 1920,
        height: int = 1080,
        color: str = 'black'
) -> list[str]:
    """
    Creates black video and null audio for use in making an intro.

    Parameters:
    fps (int): Desired fps
    command (list): list of ffmpeg commands
    duration (int): Duration of returned clip in seconds (default: 3)
    width (int): Width of returned clip in pixels (default: 1920)
    height (int): Height of returned clip in pixels (default: 1080)
    backgroundcolor (str): Background color (default: 'black')

    Returns:
    command: adds commands to list
    """

    # video
    command = [
            '-f', 'lavfi',
            '-t', str(duration),
            '-r', fps,
            '-i', f'color={color}:{width}x{height}'
            ]

    # audio
    command += [
            '-f', 'lavfi',
            '-t', str(duration),
            '-i', 'anullsrc'
            ]
    return command


def make_text_intro_filter(
        first_line: str,
        second_line: str,
        filter: list[str],
        fontcolor: str = 'white',
        fontsize: int = 96
):
    """
    Takes two lines of text and returns filter to create background with that information over it.

    Parameters:
    first_line (str): first line of text
    second_line (str): second line of text
    filter (list): list of filters
    fontcolor (str): Font color (default: 'white')
    fontsize (int): Font size (default: 96)

    Modifies:
    filter: adds filters
    """

    # Add name
    filter.append('[0]drawtext=' + ':'.join([
        f'text={first_line}',
        'x=(w-text_w)/2',
        'y=(h - 4 * text_h)/2',
        f'fontcolor={fontcolor}',
        f'fontsize={fontsize}',
    ]) + '[firstline]')

    # Add division
    filter.append('[firstline]drawtext=' + ':'.join([
        f'text={second_line}',
        'x=(w-text_w)/2',
        'y=(h - text_h)/2',
        f'fontcolor={fontcolor}',
        f'fontsize={fontsize}',
    ]) + '[introvid]')

    # Rename audio
    filter.append("[1:a]anull[introaudio]")


def render_intro(first_line: str, second_line: str):
    """
    Creates intro clip with name and division.
    Outputs video as segment_0.mp4.

    Parameters:
    first_line (str): first line of text
    second_line (str): second line of text
    """
    filter = list()
    make_text_intro_filter(first_line, second_line, filter)

    command = ["ffmpeg",
               *make_text_intro_video("30"),
               '-filter_complex',
               f'"{";".join(filter)}"',
               '-map', '[introvid]',
               '-map', '[introaudio]',
               '-y',
               'segment_0.mp4']
    subprocess.run(' '.join(command), shell=True, capture_output=True)


def render_segments(video_path: str, segments: list[tuple[int]]):
    """
    Cuts video into multiple segments based on the times defined in segments.

    Parameters:
    video_path (str): path to source video
    segments (list[tuple[int]]): list of 2 int tuples containing start
        and end times for segments
    """
    for i, segment in enumerate(segments, start=1):
        start, stop = segment
        command = ['ffmpeg',
                   '-hide_banner',
                   '-ss', str(start),
                   '-i', f'"{video_path}"',
                   '-t', str(stop - start),
                   '-c', 'copy',
                   '-y',
                   f'segment_{i}.mp4']
        subprocess.run(' '.join(command), shell=True, capture_output=True)


def join_segments(out_file_name: str, segments: list[tuple[int]]):
    """
    Joins segments produced in previous steps together with a crossfade

    Parameters:
    out_file_name (str): name of output file
    segments (list[tuple[int]]): list of 2 int tuples containing start
        and end times for segments
    """
    command = ["ffmpeg", "-hide_banner"]
    for i in range(0, len(segments) + 1):
        command += ["-i", f"segment_{i}.mp4"]
    command.append('-filter_complex')
    filter = list()
    for i in range(len(segments) + 1):
        filter += [f"[{i}:v]null[{i}v]", f"[{i}:a]anull[{i}a]"]

    prev_offset = 0
    segments.insert(0, (0, 3))
    for i in range(len(segments) - 1):
        start, stop = segments[i]
        prev_offset = stop - start + prev_offset - 1
        cross_fade(f"{i}v", f"{i}a", f"{i+1}v",
                   f"{i+1}a", f"{i+1}", prev_offset, filter)
    command += [
        f'"{";".join(filter)}"',
        '-map', f'[{len(segments) - 1}v]',
        '-map', f'[{len(segments) - 1}a]',
        '-y', f'{out_file_name}.mp4'
        ]
    subprocess.run(' '.join(command), shell=True, capture_output=True)


if __name__ == '__main__':
    segments = [(27, 95), (106, 112)]
    video_path = "nishant.MP4"
    info = VideoInfo("Nishant Dash", "PA1", video_path, segments)
    create_video(info)
