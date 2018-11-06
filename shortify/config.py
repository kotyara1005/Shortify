MAIN_PAGE = open('./index.html').read()
REDIS_URL = 'redis://127.0.0.1:6666/0'
RECORD_TTL = 60

try:
    from local_config import *
except ImportError:
    pass
