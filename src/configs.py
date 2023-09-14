import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR, LOG_DIR_POSTFIX, LOG_FILE_POSTFIX
from enums import Func

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


def configure_argument_parser(
        available_modes: list[str]
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=tuple(e.value for e in Func),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging() -> None:
    log_dir = BASE_DIR / LOG_DIR_POSTFIX
    try:
        log_dir.mkdir(exist_ok=True)
    except Exception as exc:
        logging.critical(exc)
        return
    log_file = BASE_DIR / LOG_FILE_POSTFIX
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5, encoding='utf-8'
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
