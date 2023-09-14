import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import DATETIME_FORMAT, RESULTS_DIR_POSTFIX, BASE_DIR
from enums import Func


def control_output(results: list[tuple[str]], cli_args: list[str]) -> None:
    output = cli_args.output
    output_vars = {
        Func.pretty.value: [pretty_output, results],
        Func.file.value: [file_output, results, cli_args],
        None: [default_output, results]
    }
    func = output_vars[output][0]
    func(*output_vars[output][1:])


def default_output(results: list[tuple[str]]) -> None:
    for row in results:
        print(*row)


def pretty_output(results: list[tuple[str]]) -> None:
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results: list[tuple[str]], cli_args: list[str]):
    results_dir = BASE_DIR / RESULTS_DIR_POSTFIX
    try:
        results_dir.mkdir(exist_ok=True)
    except Exception as exc:
        logging.critical(exc)
        return
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
