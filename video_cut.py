import subprocess


def video_segment_filter(segments: list):
    command = ""
    for i, (start, end) in enumerate(segments):
        command += f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[{i}v];"
        command += f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[{i}a];"

    prev_offset = 0
    if len(segments) > 1:
        start, stop = segments[0]
        command += cross_fade("0v", "0a", "1v", "1a", "fade1", stop - start + prev_offset - 1) + ";"
        prev_offset = stop - start + prev_offset - 1

    for i in range(1, len(segments) - 1):
        start, stop = segments[i]
        command += cross_fade(f"fade{i}v", f"fade{i}a", f"{i+1}v", f"{i+1}a", f"fade{i+1}", stop - start + prev_offset - 1) + ";"
        prev_offset = stop - start + prev_offset - 1

    if len(segments) > 1:
        command += f'[fade{len(segments) - 1}v]settb=AVTB[outvtb];'
        command += f'[fade{len(segments) - 1}a]anull[outa]'
    else:
        command += '[0v]settb=AVTB[outvtb];'
        command += '[0a]anull[outa]'
    return command


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
    command += '[1]drawtext=' + ':'.join([
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
    ]) + '[secondline];'

    # Set timebase
    command += '[secondline]settb=AVTB[introvid]'

    return command


def cross_fade(video_1: str, audio_1: str, video_2: str, audio_2: str, out_name: str, offset: int):
    command = f"[{audio_1}][{audio_2}]acrossfade=d=1[{out_name}a];"
    # command += f"[{video_1}][{video_2}]xfade=offset={offset}:transition=fade[{out_name}v]"
    command += f"[{video_1}]setpts=PTS-STARTPTS[{video_1}_pts];"
    command += f"[{video_2}]fade=in:st=0:d=1:alpha=1,setpts=PTS-STARTPTS+({offset}/TB)[{video_2}_pts];"
    command += f"[{video_1}_pts][{video_2}_pts]overlay[{out_name}v]"
    return command


if __name__ == '__main__':
    # segments = [(0, 98), (145, 233), (310, 395), (440, 470)]
    # video_path = "IMG_1180.MOV"
    # segments = [(27, 95), (106, 112)]
    # video_path = "nishant.MP4"
    segments = [(0, 85), (125, 137), (175, 297), (336, 410)]
    video_path = "colin.MP4"
    cuts = video_segment_filter(segments)
    name = "Nishant Dash"
    division = "A1 Sparing"
    command = f'ffmpeg -hide_banner -loglevel warning -i {video_path} {make_text_intro_video("30")} -filter_complex "{make_text_intro_filter(name, division)};{cuts};{cross_fade("introvid", "2", "outvtb", "outa", "final", 2)}" -map [finalv] -map [finala] -y -avoid_negative_ts make_zero out.mp4'
    print(command)
    subprocess.call(command, shell=True)
