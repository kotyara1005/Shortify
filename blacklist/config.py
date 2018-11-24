BLACKLIST_URL = 'https://hosts-file.net/download/hosts.txt'
REDIS_URL = 'redis://127.0.0.1:6666/0'

try:
    from local_config import *
except ImportError:
    pass
