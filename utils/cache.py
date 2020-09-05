from cachetools import TTLCache, cached
from . import common
Cache = TTLCache(maxsize = 128, ttl = 30)
logger = common.getLogger('bot')
@cached(cache = Cache)
def cachedRun(func, *args, **kwargs):
    logger.debug(f'记录了{func.__name__}的一条缓存')
    return func(*args, **kwargs)