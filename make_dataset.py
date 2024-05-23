import io
import re
import subprocess
from pathlib import Path
from progress_bar import NestedProgressBar, ProgressBar
from video_info import read_config, get_fps, get_frame_count


def create_dataset(config_file: str, parent_path=None):
    temp_data_folder = Path("temp_data")
    temp_data_folder.mkdir(exist_ok=True)

    parent_folder = Path("data")
    include_folder = parent_folder / "include"
    exclude_folder = parent_folder / "exclude"

    config = read_config(config_file, parent_path)
    bars = NestedProgressBar([ProgressBar(len(config)), None])

    for i, video in enumerate(config):
        # Create Folders
        data_include_folder = include_folder / f"{video.output_file_name}_{i}"
        data_exclude_folder = exclude_folder / f"{video.output_file_name}_{i}"

        data_include_folder.mkdir(parents=True, exist_ok=True)
        data_exclude_folder.mkdir(parents=True, exist_ok=True)

        # Extract Frames
        extract_frames_text = f"Extracting Frames of {video.path.name}"
        frame_count = get_frame_count(str(video.path))
        bars[1] = ProgressBar(frame_count)
        bars[1].update_message(extract_frames_text)
        bars.print()
        command = [
            "ffmpeg",
            "-loglevel", "error",
            "-progress", "-",
            "-nostats",
            "-i", str(video.path),
            "-s", "320x180",
            f"temp_data/{video.output_file_name}_%06d.jpg"
        ]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            if 'frame=' in line:
                progress = int(line.strip()[6:])
                bars[1].set_value(progress)
                bars.print()
        bars.print()

        # Get frames
        p = temp_data_folder.glob("**/*")
        files = [x for x in p if x.is_file()]

        fps = get_fps(str(video.path))
        frame_segments = [(round(x * fps), round(y * fps))
                          for x, y in video.segments]

        # Move Frames
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
        bars[0].increment()
    bars.print()
    bars.finish()

    temp_data_folder.rmdir()


if __name__ == "__main__":
    create_dataset("dataset_config.csv", "/media/nishant/Hard Drive/TKD Videos")
