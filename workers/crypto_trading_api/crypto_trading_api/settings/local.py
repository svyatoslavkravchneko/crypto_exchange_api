from .base import *
DEBUG = True
TEMPLATE_DEBUG = False


SECRET_KEY = 'local_key'

BROKER_URL = "amqp://root:root@172.17.0.1:5672/"
CELERY_RESULT_BACKEND = "amqp://root:root@172.17.0.1:5672"
ENV = 'local'
CACHES['default']['LOCATION'] = 'redis://crypto_trading_api_redis:6379/1'

