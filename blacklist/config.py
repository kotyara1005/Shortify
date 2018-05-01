BLACKLIST_URL = 'https://hosts-file.net/download/hosts.txt'
REDIS_URL = 'redis://127.0.0.1:6379/0'
LINE_START = '127.0.0.1\t'

try:
    from local_config import *
except ImportError:
    pass
