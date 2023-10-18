from crypto_trading_api_core import enums
from crypto_trading_api_exchange_wrappers import bitforex


def get_all_pairs(exchange):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_all_pairs()


def get_ticker(exchange, common_pair):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_ticker(common_pair)


def get_order_book(exchange, common_pair, order_book_size=10):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_orderbook(common_pair, order_book_size)


def get_exchange_account_balance(exchange, api_key, secret):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_balance(api_key, secret)


def create_order_on_exchange(exchange, api_key, secret, pair, price, volume, side):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.create_order(api_key, secret, pair, price, volume, side)


def create_orders_on_exchange(exchange, api_key, secret, pair, orders_info):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.create_orders(api_key, secret, pair, orders_info)


def cancel_order_on_exchange(exchange, api_key, secret, pair, order_id):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.cancel_order(api_key, secret, pair, order_id)


def cancel_orders_on_exchange(exchange, api_key, secret, pair, order_ids):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.cancel_orders(api_key, secret, pair, order_ids)


def get_multi_cancel_orders_count(exchange):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_multi_cancel_orders_count()


def get_multi_orders_info_count(exchange):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_multi_orders_info_count()


def get_order_history(exchange, api_key, secret, pair, order_id):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_order_info(api_key, secret, pair, order_id)


def get_orders_history(exchange, api_key, secret, pair, order_ids):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_orders_info(api_key, secret, pair, order_ids)


def get_min_order_volume(exchange, pair):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_min_order_volume(pair)


def get_min_price_change(exchange, pair):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_min_price_change(pair)


def get_trades(exchange, pair, trades_count = 1):
    if exchange == enums.ExchangeNameEnum.BITFOREX.value:
        return bitforex.get_trades(pair, trades_count)
