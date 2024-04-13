import ffmpeg


def get_text_intro(
        name: str,
        division: str,
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
    duration (int): Duration of returned clip in seconds (default: 3)
    width (int): Width of returned clip in pixels (default: 1920)
    height (int): Height of returned clip in pixels (default: 1080)
    backgroundcolor (str): Background color (default: 'black')
    fontcolor (str): Font color (default: 'white')
    fontsize (int): Font size (default: 96)

    Returns:
    ffmpeg.Stream
    """
    background = ffmpeg.input(f"color={backgroundcolor}:{width}x{height}", t=duration, f="lavfi")

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

    return background


if __name__ == '__main__':

    background = get_text_intro("Nishant Dash", "Black Belt Poomsae")
    temp = background.output('out.mp4').overwrite_output()
    # print(temp.compile())
    temp.run()
