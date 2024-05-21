import re
import subprocess
from pathlib import Path
from progress_bar import ProgressBar
from video_info import read_config, get_fps


def create_dataset(config_file: str, parent_path=None):
    temp_data_folder = Path("temp_data")
    temp_data_folder.mkdir(exist_ok=True)

    parent_folder = Path("dataset")
    include_folder = parent_folder / "include"
    exclude_folder = parent_folder / "exclude"

    config = read_config(config_file, parent_path)
    bar = ProgressBar(len(config))

    for i, video in enumerate(config):
        # Create Folders
        data_include_folder = include_folder / f"{video.output_file_name}_{i}"
        data_exclude_folder = exclude_folder / f"{video.output_file_name}_{i}"

        data_include_folder.mkdir(parents=True, exist_ok=True)
        data_exclude_folder.mkdir(parents=True, exist_ok=True)

        # Extract Frames
        bar.print(f"Extracting Frames of {video.path.name}")
        command = [
            "ffmpeg",
            "-i", str(video.path),
            "-s", "320x180",
            f"temp_data/{video.output_file_name}_%06d.jpg"
        ]
        subprocess.run(command, capture_output=True)

        # Get frames
        bar.print(f"Gathering Frames of {video.path.name}")
        p = temp_data_folder.glob("**/*")
        files = [x for x in p if x.is_file()]

        fps = get_fps(str(video.path))
        frame_segments = [(round(x * fps), round(y * fps))
                          for x, y in video.segments]

        bar.print(f"Classifying Frames of {video.path.name}")
        for file in files:
            frame_number = int(re.findall(r'\d{6}', file.name)[0])
            include = False
            for segment in frame_segments:
                if segment[0] <= frame_number and frame_number <= segment[1]:
                    file.rename(data_include_folder / file.name)
                    include = True
                    break
            if not include:
                file.rename(data_exclude_folder / file.name)
        bar.increment()

    bar.print()
    temp_data_folder.rmdir()


if __name__ == "__main__":
    create_dataset("dataset_config.csv", "/media/nishant/Hard Drive/TKD Videos")
