import os
import subprocess


def make_text_intro_video(
        fps: str,
        duration: int = 3,
        width: int = 1920,
        height: int = 1080,
        color: str = 'black'
):
    video = f'-f lavfi -t {duration} -r {fps} -i color={color}:{width}x{height}'
    audio = f'-f lavfi -t {duration} -i anullsrc'
    return ' '.join([video, audio])


def make_text_intro_filter(
        name: str,
        division: str,
        fontcolor: str = 'white',
        fontsize: int = 96
):
    """
    Takes competitor name and divsion and returns background with that information over it.

    Parameters:
    name (str): Name of competitor
    division (str): Division of competitor
    fps (int): Desired fps
    duration (int): Duration of returned clip in seconds (default: 3)
    width (int): Width of returned clip in pixels (default: 1920)
    height (int): Height of returned clip in pixels (default: 1080)
    backgroundcolor (str): Background color (default: 'black')
    fontcolor (str): Font color (default: 'white')
    fontsize (int): Font size (default: 96)

    Returns:
    ffmpeg.Stream
    """

    command = ""
    # Add name
    command += '[0]drawtext=' + ':'.join([
        f'text={name}',
        'x=(w-text_w)/2',
        'y=(h - 4 * text_h)/2',
        f'fontcolor={fontcolor}',
        f'fontsize={fontsize}',
    ]) + '[firstline];'

    # Add division
    command += '[firstline]drawtext=' + ':'.join([
        f'text={division}',
        'x=(w-text_w)/2',
        'y=(h - text_h)/2',
        f'fontcolor={fontcolor}',
        f'fontsize={fontsize}',
    ]) + '[introvid];'

    # Rename audio
    command += "[1:a]anull[introaudio]"

    return command


def cross_fade(video_1: str, audio_1: str, video_2: str, audio_2: str, out_name: str, offset: int):
    command = f"[{audio_1}][{audio_2}]acrossfade=d=1[{out_name}a];"
    command += f"[{video_1}]setpts=PTS-STARTPTS[{video_1}_pts];"
    command += f"[{video_2}]fade=in:st=0:d=1:alpha=1,setpts=PTS-STARTPTS+({offset}/TB)[{video_2}_pts];"
    command += f"[{video_1}_pts][{video_2}_pts]overlay[{out_name}v]"
    return command


def render_intro(name, division):
    command = "ffmpeg " + make_text_intro_video("30")
    command += ' -filter_complex "' + make_text_intro_filter(name, division)
    command += '" -map [introvid] -map [introaudio] -y segment_0.mp4'
    subprocess.run(command, shell=True)


def render_segments(video_path: str, segments: list):
    for i, segment in enumerate(segments, start=1):
        start, stop = segment
        command = f"ffmpeg -hide_banner -ss {start} -i {video_path} -t {stop - start} -y -c copy segment_{i}.mp4"
        subprocess.run(command, shell=True)


def join_segments(segments: list):
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
        command += cross_fade(f"{i}v", f"{i}a", f"{i+1}v", f"{i+1}a", f"{i+1}", prev_offset) + ";"
    command = command[:-1] + f'" -map [{len(segments) - 1}v] -map [{len(segments) - 1}a] -y out.mp4'
    subprocess.run(command, shell=True)

if __name__ == '__main__':
    # segments = [(0, 98), (145, 233), (310, 395), (440, 470)]
    # video_path = "IMG_1180.MOV"
    # segments = [(27, 95), (106, 112)]
    # video_path = "nishant.MP4"
    segments = [(0, 85), (125, 137), (175, 297), (336, 410)]
    video_path = "colin.MP4"
    render_intro("Nishant Dash", "A1 Poomsae")
    render_segments(video_path, segments)
    join_segments(segments)
    for i in range(len(segments)):
        os.remove(f"segment_{i}.mp4")
