from pathlib import Path

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
MAIN_DOC_URL = 'https://docs.python.org/3/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
MAIN_PEP_URL = 'https://peps.python.org/'
OUTPUT_MODES = ('pretty', 'file')
LOGS = 'logs'
PARSER_LOG = 'parser.log'
DOWNLOADS = 'downloads'
RESULTS = 'results'
PEP_STATUS = 'pep_status.csv'
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
