import csv
from pathlib import Path


class VideoInfo():
    def __init__(
            self,
            first_line: str,
            second_line: str,
            path: str,
            segments: list,
            output_file_name: str = None
    ):
        self.first_line = first_line
        self.second_line = second_line
        self.path = path
        self.segments = segments
        if output_file_name is None:
            combined = second_line + "_" + first_line
            self.output_file_name = combined.replace(" ", "_")
        else:
            self.output_file_name = output_file_name

    def __str__(self):
        ret = f"First Line: {self.first_line}\n"
        ret += f"Second Line: {self.second_line}\n"
        ret += f"Path: {self.path}\n"
        ret += f"Output File Name: {self.output_file_name}\n"
        ret += f"Segments: {str(self.segments)}\n"
        return ret


def read_config(config_file_path: str = "config.csv", parent_path: str = None):
    # Get parent path
    if parent_path is None:
        parent_path = Path.cwd()
    else:
        parent_path = Path(parent_path)

    # Get config file path
    config_file_path = Path(config_file_path)
    if not config_file_path.is_file():
        print(f"File: {config_file_path} does not exist. Please input a valid config file.")
        exit(1)

    # Read config
    config = []
    with config_file_path.open() as config_file:
        reader = csv.reader(config_file)
        header = True
        for row in reader:
            if header:
                header = False
                continue
            first_line = row[0]
            second_line = row[1]
            path = parent_path.joinpath(row[2])
            if not path.is_file():
                print(f"Path: [{path}] does not exist")
                exit(1)

            segments = []
            for i in range(3, len(row) - 1, 2):
                if i + 1 >= len(row):
                    break
                if len(row[i]) and len(row[i+1]):
                    segments.append((int(row[i]), int(row[i+1])))

            config.append(VideoInfo(first_line, second_line, path, segments))
    return config
