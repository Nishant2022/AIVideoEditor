import ffmpeg
import cv2


def get_text_intro(
        name: str,
        division: str,
        fps: int,
        duration: int = 3,
        width: int = 1920,
        height: int = 1080,
        backgroundcolor: str = 'black',
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
    background = ffmpeg.input(f"color={backgroundcolor}:{width}x{height}", t=duration, f="lavfi", r=fps)

    # Add name
    background = background.drawtext(
        text=name,
        x='(w-text_w)/2',
        y='(h - 4 * text_h)/2',
        fontcolor=fontcolor,
        fontsize=fontsize,
    )

    # Add division
    background = background.drawtext(
        text=division,
        x='(w-text_w)/2',
        y='(h - text_h)/2',
        fontcolor=fontcolor,
        fontsize=fontsize
    )

    # Set timebase
    background = background.filter("settb", "AVTB")

    # Create Audio
    background_audio = ffmpeg.input("anullsrc", t=duration, f="lavfi")

    return background, background_audio


if __name__ == '__main__':

    input_video = "IMG_1180.MOV"
    # Get source fps
    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fps = ffmpeg.probe(input_video)["streams"][0]["r_frame_rate"]

    match = ffmpeg.input(input_video, vsync=2)

    match_video = match.video
    match_audio = match.audio

    # Get intro video
    intro, intro_audio = get_text_intro("Nishant Dash", "Black Belt Poomsae", fps=fps)

    video = ffmpeg.filter([intro, match_video.filter("settb", "AVTB")], "xfade", transition="fade", offset=2)
    audio = ffmpeg.filter([intro_audio, match_audio], "acrossfade", d=1)
    output = ffmpeg.output(audio, video, 'out.mp4').overwrite_output()
    print(output.compile())
    # output.run()
