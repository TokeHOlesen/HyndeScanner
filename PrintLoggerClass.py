from datetime import datetime
from CushionClass import Cushion


class PrintLogger:
    """Writes each print job details to a log file."""
    path = "Data/log.txt"

    @classmethod
    def write_to_log_file(cls, cushion: Cushion, number: int, mode: str) -> None:
        log_file_line = str(datetime.now())[:-7]
        log_file_line += f": {number} x "
        log_file_line += f"{cushion.item_name}, {cushion.color}, {cushion.old_number}, {cushion.new_number}"
        log_file_line += f" ({mode})\n"

        try:
            with open(cls.path, "a+") as log_file:
                log_file.write(log_file_line)
        except OSError:
            pass
