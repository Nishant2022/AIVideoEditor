import csv
import pathlib
from video_info import VideoInfo
from create_video import create_video
from progress_bar import ProgressBar


def read_config(config_file_path: str = "config.csv"):
    if not pathlib.Path(config_file_path).is_file():
        print(f"File: {config_file_path} does not exist. Please input a valid config file.")
        exit(1)

    config = []
    with open(config_file_path) as config_file:
        reader = csv.reader(config_file)
        header = True
        for row in reader:
            if header:
                header = False
                continue
            first_line = row[0]
            second_line = row[1]
            path = row[2]

            segments = []
            for i in range(3, len(row) - 1, 2):
                if i + 1 >= len(row):
                    break
                if len(row[i]) and len(row[i+1]):
                    segments.append((int(row[i]), int(row[i+1])))

            config.append(VideoInfo(first_line, second_line, path, segments))
    return config


if __name__ == "__main__":
    config = read_config()
    bar = ProgressBar(len(config))
    for c in config:
        bar.print(f"Creating: {c.output_file_name}.mp4")
        create_video(c)
        bar.increment()
    bar.print()
