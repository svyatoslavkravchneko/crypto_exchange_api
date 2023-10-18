#!/usr/bin/env bash

rsync /usr/src/crypto_trading_api/deploy/public_data/supervisor.conf  /etc/supervisor/conf.d/background.conf
/usr/bin/supervisord -n