from crypto_trading_api.celery import app
from crypto_trading_api_exchange_wrappers import get_all_pairs as get_all_pairs_from_api
from crypto_trading_api_exchange_wrappers import get_ticker as get_ticker_from_api
from crypto_trading_api_exchange_wrappers import get_order_book as get_order_book_from_api
from crypto_trading_api_exchange_wrappers import get_min_order_volume as get_min_order_volume_from_api
from crypto_trading_api_exchange_wrappers import get_min_price_change as get_min_price_change_from_api
from crypto_trading_api_exchange_wrappers import get_trades as get_trades_from_api
from django.core.cache import cache


@app.task(name='get_all_pairs',
          bind=True)
def get_all_pairs(self, exchange):
    return get_all_pairs_from_api(exchange)


@app.task(name='get_min_order_volume',
          bind=True)
def get_min_order_volume(self, exchange, pair):
    return get_min_order_volume_from_api(exchange, pair)


@app.task(name='get_min_price_change',
          bind=True)
def get_min_price_change(self, exchange, pair):
    return get_min_price_change_from_api(exchange, pair)


@app.task(name='get_ticker',
          bind=True)
def get_ticker(self, exchange, common_pair):
    return get_ticker_from_api(exchange, common_pair)


@app.task(name='get_order_book',
          bind=True)
def get_order_book(self, exchange, common_pair, size=5):
    return get_order_book_from_api(exchange, common_pair)


@app.task(name='get_trades',
          bind=True)   # why is bound?
def get_trades(self, exchange, common_pair, trade_count=1):
    return get_trades_from_api(exchange, common_pair, trade_count)


@app.task(name='subscribe_to_order_book',
          bind=True)
def subscribe_to_order_book(self, exchange, pair, routing_key):
    cache_name = "new_pairs_for_{0}_ws_depth_subscribe".format(exchange)
    cache_value = cache.get(cache_name, {})
    if pair not in cache_value:
        cache_value[pair] = {"routing_key_send_updates_to": routing_key}
    cache.set(cache_name, cache_value)
    return True   # Or what?


@app.task(name='unsubscribe_from_order_book',
          bind=True)
def unsubscribe_from_order_book(self, exchange, pair):
    cache_name = "new_pairs_for_{0}_ws_depth_unsubscribe".format(exchange)
    cache_value = cache.get(cache_name, [])
    if pair not in cache_value:
        cache_value.append(pair)
    cache.set(cache_name, cache_value)
    return True  # Or what?

