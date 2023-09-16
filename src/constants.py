from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
BASE_DIR = Path(__file__).parent
LOG_DIR_POSTFIX = 'logs'
LOG_FILE_POSTFIX = 'parser.log'
RESULTS_DIR_POSTFIX = 'results'
DOWNLOADS_POSTFIX = 'downloads'
# Регулярка, чтобы достать только версию Питона и её статус из левого меню.
REGULAR_FOR_PYTHON = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
LXML = 'lxml'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
PEP_URL = 'https://peps.python.org/'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
