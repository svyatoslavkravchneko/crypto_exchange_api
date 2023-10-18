import os
import subprocess
import time

from django.core.management import BaseCommand


def run_health_check():
    active_exchanges_to_monitor = ['BITFOREX']
    for exchange in active_exchanges_to_monitor:
        process = "run_{0}_depth_update_ws".format(exchange)
        output = subprocess.check_output('supervisorctl status {0}'.format(process).
                                         split()).decode('ascii').strip()
        process_state = output.split()[1]
        if process_state in ('BACKOFF', 'ERROR', 'EXITED', 'FATAL', 'UNKNOWN'):
            print("Account websocket process has entered '{0}' state. Will try to start".format(process_state))
            os.system('supervisorctl restart {0}'.format(process))


class Command(BaseCommand):
    help = 'Run process to monitor depth websocket state'

    def handle(self, *args, **options):

        while 1:
            time.sleep(60)
            run_health_check()

