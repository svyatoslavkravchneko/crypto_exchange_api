from django.core.cache import cache
from crypto_trading_api_core.utils import logger_utils


def acquire_lock(lock_name, expiry=None):
    is_lock = is_lock_present(lock_name)
    if is_lock:
        raise Exception("Lock = {0} could not be acquired".format(lock_name))
    if expiry is not None:
        cache.set(lock_name, 'locked', expiry)
    elif expiry is None:
        cache.set(lock_name, 'locked')
    logger_utils.log_info('Lock={0} acquired for {1}'.format(lock_name, expiry))


def is_lock_present(lock_name):
    if cache.get(lock_name) is None:
        return False
    return True


def release_lock(lock_name):
    is_lock = is_lock_present(lock_name)
    if not is_lock:
        raise Exception("Lock = {0} can not be released".format(lock_name))
    cache.delete(lock_name)
    logger_utils.log_info('Lock={0} released'.format(lock_name))