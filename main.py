from video_info import read_config
from create_video import create_video
from progress_bar import ProgressBar


if __name__ == "__main__":
    config = read_config()
    bar = ProgressBar(len(config))
    for c in config:
        bar.print(f"Creating: {c.output_file_name}.mp4")
        create_video(c)
        bar.increment()
    bar.print()
