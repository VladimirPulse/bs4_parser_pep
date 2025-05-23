import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (DT_FORMAT, FILE, LOG_DIR, LOG_FILE, LOG_FORMAT,
                       PRETTY)


def configure_argument_parser(available_modes):
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
        choices=(PRETTY, FILE),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    log_dir = LOG_DIR
    log_dir.mkdir(exist_ok=True)
    log_file = LOG_FILE
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5, encoding='utf-8'
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )


def pep_status_logging(mismatched_statuses):
    logging.info("Несовпадающие статусы:")
    for mismatch in mismatched_statuses:
        logging.info(f"PEP: {mismatch['PEP']}")
        logging.info(f"Статус в карточке: {mismatch['Page Status']}")
        logging.info(f"Ожидаемые статусы: {mismatch['Expected Statuses']}")
        logging.info("")
