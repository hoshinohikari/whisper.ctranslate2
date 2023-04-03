import datetime
import sys

system_encoding = sys.getdefaultencoding()

if system_encoding != "utf-8":
    def make_safe(string):
        return string.encode(system_encoding, errors="replace").decode(system_encoding)
else:
    def make_safe(string):
        return string


def format_timestamp(
        seconds: float  # , always_include_hours: bool = False, decimal_marker: str = "."
):
    time_str = str(datetime.timedelta(seconds=seconds))
    if len(time_str) > 7:
        return time_str[:-4]
    else:
        return time_str + '.00'


def _get_colored_text(words):
    k_colors = [
        "\033[38;5;196m",
        "\033[38;5;202m",
        "\033[38;5;208m",
        "\033[38;5;214m",
        "\033[38;5;220m",
        "\033[38;5;226m",
        "\033[38;5;190m",
        "\033[38;5;154m",
        "\033[38;5;118m",
        "\033[38;5;82m",
    ]

    text_words = ""

    n_colors = len(k_colors)
    for word in words:
        p = word.probability
        col = max(0, min(n_colors - 1, int(pow(p, 3) * n_colors)))
        end_mark = "\033[0m"
        text_words += f"{k_colors[col]}{word.word}{end_mark}"

    return text_words
