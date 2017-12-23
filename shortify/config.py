MAIN_PAGE = open('./index.html').read()
REDIS_HOST = 'redis'
RECORD_TTL = 60

try:
    from local_config import *
except ImportError:
    pass
