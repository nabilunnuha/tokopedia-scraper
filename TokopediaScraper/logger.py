from colorama import Fore, Style, init
import logging, sys

init()
class ColoredFormatter(logging.Formatter):
    _level_colors = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
    }
    _reset_color = Style.RESET_ALL

    def format(self, record):
        if record.levelno in self._level_colors:
            record.levelname = f"{self._level_colors[record.levelno]}{record.levelname}{self._reset_color}"
        return super().format(record)

def create_logger(log_path='./log/logger.log', logger_name=__name__) -> logging.Logger:
    if logger_name not in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        file_handler = create_file_handler(log_path)
        console_handler = create_console_handler()

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    else:
        logger = logging.getLogger(logger_name)

    return logger

def create_file_handler(log_path):
    file_handler = logging.FileHandler(log_path)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    return file_handler

def create_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    return console_handler

if __name__ == "__main__":
    logger = create_logger(logger_name=__name__)
    logger.debug("Ini adalah pesan debug")
    logger.info("Ini adalah pesan info")
    logger.warning("Ini adalah pesan peringatan")
    logger.error("Ini adalah pesan error")
    logger.critical("Ini adalah pesan kritis")