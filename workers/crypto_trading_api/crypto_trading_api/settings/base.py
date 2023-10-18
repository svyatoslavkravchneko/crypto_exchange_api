import os
from kombu.serialization import registry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SECRET_KEY = None

DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'crypto_trading_api',
    'crypto_trading_api_core',
    'crypto_trading_api_public_data',
    'crypto_trading_api_exchange_wrappers',
    'crypto_trading_api_account_data',
)


TIME_ZONE = 'Europe/Kiev'
USE_TZ = False

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

BROKER_URL = "amqp://myuser:mypassword@localhost:5672/myvhost/"

CELERY_RESULT_BACKEND = 'amqp://myuser:mypassword@localhost:5672'
CELERY_ACCEPT_CONTENT = ['json', 'application/text', 'application/data', 'application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_MAX_TASKS_PER_CHILD = 100
CELERY_TASK_RESULT_EXPIRES = 60


registry.enable('json')
registry.enable('application/text')
registry.enable('application/data')
registry.enable('application/json')

CELERY_QUEUES = (
)

CELERY_IMPORTS = ()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
	    'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
	    'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'loggers': {
        'zeep.xsd': {
            'level': 'INFO',
            'propagate': False,
            'handlers': []
        },
        'zeep.wsdl': {
            'level': 'INFO',
            'propagate': False,
            'handlers': []
        },
        'zeep.cache': {
            'level': 'INFO',
            'propagate': False,
            'handlers': []
        },
        'chardet.charsetprober' : {
            'level': 'INFO',
            'propagate': False,
            'handlers': []
        }
    }
    # 'filters': {
    #     'require_debug_true': {
    #         '()': 'django.utils.log.RequireDebugTrue',
    #     }
    # },
    # 'handlers': {
    #     'console': {
    #         'level': 'DEBUG',
    #         'filters': ['require_debug_true'],
    #         'class': 'logging.StreamHandler',
    #     }
    # },
    # 'loggers': {
    #     'django.db.backends': {
    #         'level': 'DEBUG',
    #         'handlers': ['console'],
    #     }
    # }
}
ENV = 'base'


from django.utils.timezone import activate
import pytz

activate(pytz.timezone(TIME_ZONE))

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        'TIMEOUT': None,
        "KEY_PREFIX": "crypto_trading_api"
    }
}

EXCHANGE_ACCOUNT_ENCRYPT_KEY = b'K1cUDHxRKLAPLDrq3SfOw6u-E9rrFsAeRUOUmgBIHQ8='