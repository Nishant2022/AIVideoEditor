class ProgressBar():
    def __init__(self, n_jobs: int, bar_width: int = 40):
        self.n_jobs = n_jobs
        self.bar_width = bar_width
        self.n_completed = 0
        self.completed = False
        self.prev_bar_len = 0

    def print(self, message: str = ""):
        if not self.completed:
            percentage = self.n_completed * 100 / self.n_jobs
            bar = "█" * (self.n_completed * self.bar_width // self.n_jobs)
            bar += "-" * (self.bar_width - (self.n_completed * self.bar_width // self.n_jobs))
            complete_bar = f"\rProgress: |{bar}| {percentage:.2f}% ({self.n_completed}/{self.n_jobs}) {message}"
            bar_len = len(complete_bar)
            if len(complete_bar) < self.prev_bar_len:
                complete_bar += " " * (self.prev_bar_len - bar_len)
            self.prev_bar_len = bar_len
            print(complete_bar, end="")
            if self.n_jobs == self.n_completed:
                self.completed = True
                print()

    def increment(self):
        self.n_completed += 1
