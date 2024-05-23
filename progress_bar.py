from collections.abc import MutableSequence

ESC = "\033"  # Escape
CSI = "["     # Control Sequence Introducer
CNL = "E"     # Cursor Next Line
CPL = "F"     # Cursor Previous Line
EL = "0K"     # Erase Line
SGR = "m"     # Select Graphic Rendition - set colors and style

RESET = "39;49"
BLACK_FG = "30"
BLACK_BG = "30"
RED_FG = "31"
RED_BG = "41"
BRIGHT_GREEN_FG = "92"
BRIGHT_GREEN_BG = "102"
BRIGHT_YELLOW_FG = "93"
BRIGHT_YELLOW_BG = "103"
BRIGHT_BLUE_FG = "94"
BRIGHT_BLUE_BG = "104"
BRIGHT_WHITE_FG = "97"
BRIGHT_WHITE_BG = "107"


class ProgressBar():
    def __init__(self, n_jobs: int, bar_width: int = 40, color: bool = True):
        self.n_jobs = n_jobs
        self.bar_width = bar_width
        self.color = color
        self.n_completed = 0
        self.completed = False
        self.message = ""

    def _bar_text(self):
        message = self.message
        percentage = self.n_completed * 100 / self.n_jobs
        bar = "█" * (self.n_completed * self.bar_width // self.n_jobs)
        bar += "-" * (self.bar_width - (self.n_completed * self.bar_width // self.n_jobs))
        complete_bar = f"Progress: |{bar}| {percentage:.2f}% ({self.n_completed}/{self.n_jobs}) {message}"
        return ESC + CSI + EL + complete_bar

    def update_message(self, message: str = ""):
        self.message = message

    def print(self):
        if not self.completed:
            bar_text = self._bar_text()
            if self.color:
                print(
                    ESC + CSI + BRIGHT_YELLOW_FG + SGR,
                    "\r", bar_text,
                    ESC + CSI + BRIGHT_WHITE_FG + SGR,
                    end="",
                    sep=""
                )
            else:
                print("\r", bar_text, end="", sep="")
            if self.n_jobs == self.n_completed:
                self.completed = True
                if self.color:
                    print(
                        ESC + CSI + BRIGHT_GREEN_FG + SGR,
                        "\r", bar_text,
                        ESC + CSI + BRIGHT_WHITE_FG + SGR,
                        end="\n",
                        sep=""
                    )
                else:
                    print("\r", bar_text, end="\n", sep="")

    def increment(self):
        if self.n_completed < self.n_jobs:
            self.n_completed += 1

    def set_value(self, i: int):
        if i <= self.n_jobs:
            self.n_completed = i


class NestedProgressBar(MutableSequence):
    def __init__(self, bars: list[ProgressBar] = None, color: bool = True):
        if bars:
            self.bars = bars
        else:
            self.bars = list()
        self.color = color

    def print(self):
        for bar in self.bars:
            if self.color:
                if bar.n_completed == bar.n_jobs:
                    print(
                        ESC + CSI + BRIGHT_GREEN_FG + SGR,
                        bar._bar_text(),
                        ESC + CSI + BRIGHT_WHITE_FG + SGR,
                        end="\n",
                        sep=""
                    )
                else:
                    print(
                        ESC + CSI + BRIGHT_YELLOW_FG + SGR,
                        bar._bar_text(),
                        ESC + CSI + BRIGHT_WHITE_FG + SGR,
                        end="\n",
                        sep=""
                    )

            else:
                print(bar._bar_text())
        print(
            ESC, CSI, len(self.bars), CPL,
            end="",
            sep=""
        )

    def finish(self):
        print(
            ESC, CSI, len(self.bars), CNL,
            end="",
            sep=""
        )

    def __getitem__(self, i: int) -> ProgressBar:
        return self.bars[i]

    def __setitem__(self, i: int, item: ProgressBar):
        self.bars[i] = item

    def __delitem__(self, i: int):
        del self.bars[i]

    def __len__(self):
        return len(self.bars)

    def insert(self, i: int, item: ProgressBar):
        self.finish()
        print()
        self.bars.insert(i, item)
        print(
            ESC, CSI, len(self.bars), CPL,
            end="",
            sep=""
        )

    def append(self, item: ProgressBar):
        self.insert(len(self), item)


if __name__ == "__main__":
    import time
    items = 10
    bar = ProgressBar(items)
    bar.update_message(f'0/{items}')
    bar.print()
    for i in range(1, items + 1):
        bar.increment()
        bar.update_message(f'{i}/{items}')
        bar.print()
        time.sleep(0.1)

    bar = ProgressBar(10)
    bar2 = ProgressBar(20)
    bars = NestedProgressBar([bar, bar2])
    for i in range(100):
        if i % 20 == 0:
            bars[1] = ProgressBar(20)
        if i % 10 == 0:
            bars[0].increment()
        if i == 50:
            bars.append(ProgressBar(25))
        bars[0].update_message(i)
        bars[1].update_message(i // 20)
        bars[1].increment()
        if len(bars) > 2:
            bars[2].increment()
        bars.print()
        time.sleep(.1)
    bars.finish()
