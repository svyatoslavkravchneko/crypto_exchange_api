import os
from celery import Celery, signals
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_trading_api.settings.local')


@signals.task_failure.connect
def on_task_failure(**kwargs):
    from crypto_trading_api_core.utils import logger_utils
    error_msg = "Celery task failed. Start Trace = {0}".format(kwargs.get('einfo'))
    logger_utils.log_error(error_msg)


app = Celery('crypto_trading_api_background')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)