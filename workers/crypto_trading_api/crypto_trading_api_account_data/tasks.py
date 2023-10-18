from crypto_trading_api.celery import app
from crypto_trading_api_core.utils import encrypt_utils
from crypto_trading_api_exchange_wrappers import get_exchange_account_balance as get_exchange_account_balance_from_api
from crypto_trading_api_exchange_wrappers import  create_order_on_exchange as create_order_on_exchange_api
from crypto_trading_api_exchange_wrappers import cancel_order_on_exchange as cancel_order_on_exchange_api
from crypto_trading_api_exchange_wrappers import get_multi_cancel_orders_count as get_multi_cancel_orders_count_from_api
from crypto_trading_api_exchange_wrappers import cancel_orders_on_exchange as cancel_orders_on_exchange_from_api
from crypto_trading_api_exchange_wrappers import get_multi_orders_info_count as get_multi_orders_info_count_from_api
from crypto_trading_api_exchange_wrappers import get_orders_history as get_orders_history_from_api
from crypto_trading_api_exchange_wrappers import create_orders_on_exchange as create_orders_on_exchange_from_api
from crypto_trading_api_exchange_wrappers import get_order_history as get_order_history_from_api


@app.task(name='get_exchange_account_balance',
          bind=True
          )
def get_exchange_account_balance(self, exchange, encrypted_api_key, encrypted_secret_key):
    api_key = encrypt_utils.decrypt_key(encrypted_api_key)
    api_secret = encrypt_utils.decrypt_key(encrypted_secret_key)
    if not api_key or not api_secret:
        return
    try:
        return get_exchange_account_balance_from_api(exchange, api_key, api_secret)
    except Exception as e:
        print(e)


@app.task(name='create_order_on_exchange',
          bind=True)
def create_order_on_exchange(self,
                             exchange,
                             encrypted_api_key,
                             encrypted_secret_key,
                             pair,
                             price,
                             volume,
                             side):
    api_key = encrypt_utils.decrypt_key(encrypted_api_key)
    api_secret = encrypt_utils.decrypt_key(encrypted_secret_key)
    if not api_key or not api_secret:
        return
    try:
        return create_order_on_exchange_api(exchange,
                                            api_key,
                                            api_secret,
                                            pair,
                                            price,
                                            volume,
                                            side
                                            )
    except Exception as e:
        print(e)


@app.task(name='cancel_order_on_exchange',
          bind=True
          )
def cancel_order_on_exchange(self,
                             exchange,
                             encrypted_api_key,
                             encrypted_secret_key,
                             pair,
                             order_id):
    api_key = encrypt_utils.decrypt_key(encrypted_api_key)
    api_secret = encrypt_utils.decrypt_key(encrypted_secret_key)
    if not api_key or not api_secret:
        return
    try:
        return cancel_order_on_exchange_api(exchange,
                                            api_key,
                                            api_secret,
                                            pair,
                                            order_id
                                            )
    except Exception as e:
        print(e)


@app.task(name='get_order_info_on_exchange',
          bind=True
          )
def get_order_info_on_exchange(self,
                               exchange,
                               encrypted_api_key,
                               encrypted_secret_key,
                               pair,
                               order_id):
    api_key = encrypt_utils.decrypt_key(encrypted_api_key)
    api_secret = encrypt_utils.decrypt_key(encrypted_secret_key)
    if not api_key or not api_secret:
        return
    try:
        return get_order_history_from_api(exchange,
                                          api_key,
                                          api_secret,
                                          pair,
                                          order_id
                                          )
    except Exception as e:
        print(e)


@app.task(name='create_orders_on_exchange',
          bind=True
          )
def create_orders_on_exchange(self,
                              exchange,
                              encrypted_api_key,
                              encrypted_secret_key,
                              pair,
                              orders_info):
    api_key = encrypt_utils.decrypt_key(encrypted_api_key)
    api_secret = encrypt_utils.decrypt_key(encrypted_secret_key)
    if not api_key or not api_secret:
        return
    try:
        return create_orders_on_exchange_from_api(exchange,
                                                  api_key,
                                                  api_secret,
                                                  pair,
                                                  orders_info
                                                  )
    except Exception as e:
        print(e)


@app.task(name='cancel_orders_on_exchange',
          bind=True
          )
def cancels_order_on_exchange(self,
                              exchange,
                              encrypted_api_key,
                              encrypted_secret_key,
                              pair,
                              order_ids):
    api_key = encrypt_utils.decrypt_key(encrypted_api_key)
    api_secret = encrypt_utils.decrypt_key(encrypted_secret_key)
    if not api_key or not api_secret:
        return
    try:
        return cancel_orders_on_exchange_from_api(exchange,
                                                  api_key,
                                                  api_secret,
                                                  pair,
                                                  order_ids
                                                  )
    except Exception as e:
        print(e)


@app.task(name='get_orders_info_on_exchange',
          bind=True
          )
def get_orders_info_on_exchange(self,
                                exchange,
                                encrypted_api_key,
                                encrypted_secret_key,
                                pair,
                                order_ids):
    api_key = encrypt_utils.decrypt_key(encrypted_api_key)
    api_secret = encrypt_utils.decrypt_key(encrypted_secret_key)
    if not api_key or not api_secret:
        return
    result = []
    orders_info_count_per_request = get_multi_orders_info_count_from_api(exchange)
    if orders_info_count_per_request:
        while order_ids:
            chunk = order_ids[0:orders_info_count_per_request]
            try:
                result.extend(get_orders_history_from_api(exchange, api_key, api_secret, pair, chunk))
            except Exception as e:
                print(e)
            for i in chunk:
                order_ids.remove(i)
    return result


