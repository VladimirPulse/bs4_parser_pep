from pathlib import Path

'''Константы для формирования имён файлов'''
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

'''Константы сайтов для парсеров'''
MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'

'''Константы для загрузок'''
BASE_DIR = Path(__file__).parent
LOGS = 'logs'
LOG_DIR = BASE_DIR / LOGS
PARSER_LOG = 'parser.log'
LOG_FILE = LOG_DIR / PARSER_LOG
DOWNLOADS = 'downloads'
RESULTS = 'results'
PEP_STATUS = 'pep_status.csv'

'''Константы для функций'''
OUTPUT_MODES = ('pretty', 'file')
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
