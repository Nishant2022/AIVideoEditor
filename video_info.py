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
