import hmac
import json
import hashlib
from decimal import Decimal
from collections import OrderedDict
from django.core.cache import cache
from crypto_trading_api_core.utils import http_utils, nonce_utils
from crypto_trading_api_core import enums as core_enums

BITFOREX_API_URL = "https://api.bitforex.com/api/v1"


def get_multi_cancel_orders_count():
    return 50


def get_multi_orders_info_count():
    return 50


def from_common_to_specific(common_pair):
    splitted_common_pair = common_pair.split('_')
    if splitted_common_pair[0].lower() == 'usd':
        splitted_common_pair[0] = 'usdt'
    if splitted_common_pair[1].lower() == 'usd':
        splitted_common_pair[1] = 'usdt'
    return "coin-{0}-{1}".format(splitted_common_pair[1].lower(),
                                 splitted_common_pair[0].lower())


def from_specific_to_common(specific_pair):
    splitted_specific_pair = specific_pair.split('-')
    if splitted_specific_pair[2] == 'usdt':
        splitted_specific_pair[2] = 'usd'
    if splitted_specific_pair[1] == 'usdt':
        splitted_specific_pair[1] = 'usd'
    return "{0}_{1}".format(splitted_specific_pair[2].upper(),
                            splitted_specific_pair[1].upper())


def get_market_data():
    cached_value = cache.get('bitforex_market_data')
    result = {}
    if cached_value is None:
        decoded_response = http_utils.execute_http_request(url='{0}/market/symbols'.format(BITFOREX_API_URL),
                                                           method='GET',
                                                           raise_exception=True)
        if not decoded_response['result']['success']:
            return
        for item in decoded_response['result']['data']:
            specific_pair = item['symbol']
            common_pair = from_specific_to_common(specific_pair)
            result[common_pair] = item
            result[common_pair]['specific_pair'] = specific_pair
        cache.set('bitforex_market_data', result, 3600)
        return result
    return cached_value


def get_all_pairs():
    market_data = get_market_data()
    return list(market_data)


def get_pair_setting(pair):
    market_data = get_market_data()
    if pair in market_data:
        return market_data[pair]


def get_price_precision(pair):
    pair_setting = get_pair_setting(pair)
    if not pair_setting:
        return
    return pair_setting['pricePrecision']


def get_volume_precision(pair):
    pair_setting = get_pair_setting(pair)
    if not pair_setting:
        return
    return pair_setting['amountPrecision']


def get_min_order_volume(pair):
    pair_setting = get_pair_setting(pair)
    if not pair_setting:
        return
    return pair_setting['minOrderAmount']


def get_min_price_change(pair):
    pair_setting = get_pair_setting(pair)
    if not pair_setting:
        return
    return pow(10, pair_setting['pricePrecision'] * -1)


def get_ticker(common_pair):
    specific_pair = from_common_to_specific(common_pair)
    if not specific_pair:
        return
    decoded_response = http_utils.execute_http_request(url='{0}/market/ticker?symbol={1}'.format(BITFOREX_API_URL,
                                                                                                 specific_pair),
                                                       method='GET',
                                                       raise_exception=True)
    if not decoded_response['result']['success']:
        return
    return {'buy': decoded_response['result']['data']['buy'],
            'sell': decoded_response['result']['data']['sell']}


def get_orderbook(common_pair, limit=5):
    specific_pair = from_common_to_specific(common_pair)
    if not specific_pair:
        return
    decoded_response = http_utils.execute_http_request(url='{0}/market/depth?symbol={1}&size={2}'.format(BITFOREX_API_URL,
                                                                                                         specific_pair,
                                                                                                         limit),
                                                       method='GET',
                                                       raise_exception=True)
    if not decoded_response['result']['success']:
        return
    result = {'asks': [],
              'bids': []}
    for ask_item in decoded_response['result']['data']['asks']:
        result['asks'].append({'price': ask_item['price'],
                               'volume': ask_item['amount']})

    for bid_item in decoded_response['result']['data']['bids']:
        result['bids'].append({'price': bid_item['price'],
                               'volume': bid_item['amount']})
    return result


def generate_signature(url, api_secret, params):
    query_string = '&'.join(["{}={}".format(d, params[d]) for d in params])
    content = url +"?"+ query_string
    m = hmac.new(api_secret, content.encode('utf-8'), hashlib.sha256)
    return m.hexdigest()


def check_response_for_success(decoded_response):
    if not decoded_response['result']['success']:
        raise Exception("Response = {0} is not success".format(decoded_response))


def get_base_params_for_auth_request(api_key):
    return {'nonce': nonce_utils.generate_nonce(),
            'accessKey': api_key}


def sign_request(url, api_key, secret, params=None):
    base_params = get_base_params_for_auth_request(api_key)
    if params is not None:
        for key, val in params.items():
            base_params[key] = val
    base_params = OrderedDict(sorted(base_params.items(), key=lambda t: t[0]))
    signature = generate_signature(url, secret.encode('utf-8'), base_params)
    base_params['signData'] = signature
    return base_params


def get_balance(api_key, secret):
    url = "{0}/fund/allAccount".format(BITFOREX_API_URL)
    params = sign_request("/api/v1/fund/allAccount", api_key, secret, None)
    decoded_response = http_utils.execute_http_request(method='POST',
                                                       url=url,
                                                       params=params,
                                                       raise_exception=True)
    check_response_for_success(decoded_response)

    result = {}
    for item in decoded_response['result']['data']:
        currency = item['currency'].upper()
        free = round(float(item['active']), 8)
        locked = round(float(item['frozen']), 8)
        total = round(float(item['fix']), 8)
        if total > 0:
            result[currency.upper()] = {'total': total,
                                        'reserved': locked,
                                        'available': free}

    return result


def get_order_creation_params(pair, price, volume, side):
    specific_pair = from_common_to_specific(pair)
    if not specific_pair:
        return {'error': 'specific pair not extracted for common pair = {0}'.format(pair)}
    volume_precision = get_volume_precision(pair)
    price_precision = get_price_precision(pair)
    if not volume_precision:
        return {'error': 'volume_precision is not extracted for pair = {0}'.format(pair)}
    if not price_precision:
        return {'error': 'price_precision is not extracted for pair = {0}'.format(pair)}
    min_order_volume = get_min_order_volume(pair)
    if not min_order_volume:
        return {'error': 'min_order_volume not extracted for pair = {0}'.format(pair)}
    if volume < min_order_volume:
        return {'error': 'volume = {0} is less than min_volume = {1} for pair'.format(volume, min_order_volume)}
    order_price = (round(price, price_precision))
    order_volume = (round(volume, volume_precision))
    order_side = 1
    if side == core_enums.OrderSideEnum.SELL.value:
        order_side = 2
    return {'symbol': specific_pair,
            'price': order_price,
            'amount': order_volume,
            'tradeType': order_side}


def create_order(api_key, secret, pair, price, volume, side):
    order_creation_params = get_order_creation_params(pair, price, volume, side)
    if order_creation_params.get('error'):
        return order_creation_params
    url = "{0}/trade/placeOrder".format(BITFOREX_API_URL)
    params = sign_request("/api/v1/trade/placeOrder", api_key, secret, order_creation_params)
    print(params)
    decoded_response = http_utils.execute_http_request(method='POST',
                                                       url=url,
                                                       data=params,
                                                       raise_exception=True)
    check_response_for_success(decoded_response)
    return {'pair': pair,
            'price': order_creation_params['price'],
            'volume': order_creation_params['amount'],
            'side': side,
            'order_id': decoded_response['result']['data']['orderId']}


def create_orders(api_key, secret, pair, orders_data):
    orders_creation_params = list()
    result = []
    for order_item in orders_data:
        creation_params = get_order_creation_params(pair,
                                                    order_item['price'],
                                                    order_item['volume'],
                                                    order_item['side'])
        if creation_params.get('error'):
            continue
        del creation_params['symbol']
        orders_creation_params.append(creation_params)
        result.append({'order_id': None,
                       'price': creation_params['price'],
                       'volume': creation_params['amount'],
                       'pair': pair,
                       'side': order_item['side']})
    if not orders_creation_params:
        return {'error': 'No one order extracted to put it on exchange. Pair = {0} OrderData = {1}'.format(pair,
                                                                                                           orders_data)}
    url = "{0}/trade/placeMultiOrder".format(BITFOREX_API_URL)
    params = sign_request("/api/v1/trade/placeMultiOrder", api_key, secret, {'symbol': from_common_to_specific(pair),
                                                                             'ordersData': json.dumps(orders_creation_params)})
    decoded_response = http_utils.execute_http_request(method='POST',
                                                       url=url,
                                                       params=params
                                                       )
    for created_order_item in decoded_response['result']['data']:
        if created_order_item.get('orderId'):
            order_id = created_order_item['orderId']
            if order_id != '-1':
                result[decoded_response['result']['data'].index(created_order_item)]['order_id'] = order_id
    return result


def cancel_order(api_key, secret, pair, order_id):
    specific_pair = from_common_to_specific(pair)
    url = "{0}/trade/cancelOrder".format(BITFOREX_API_URL)
    params = sign_request("/api/v1/trade/cancelOrder", api_key, secret, {'symbol': specific_pair,
                                                                         'orderId': order_id})
    decoded_response = http_utils.execute_http_request(method='POST',
                                                       url=url,
                                                       data=params,
                                                       raise_exception=True)
    check_response_for_success(decoded_response)
    if decoded_response['result']['data'] and decoded_response['result']['success']:
        return {'order_id': order_id,
                'is_success': True}
    else:
        return {'order_id': order_id,
                'is_success': False}


def cancel_orders(api_key, secret, pair, order_ids):
    result = []
    specific_pair = from_common_to_specific(pair)
    url = "{0}/trade/cancelMultiOrder".format(BITFOREX_API_URL)
    params = sign_request("/api/v1/trade/cancelMultiOrder", api_key, secret, {'symbol': specific_pair,
                                                                              'orderIds': ",".join(order_ids)})
    decoded_response = http_utils.execute_http_request(method='POST',
                                                       url=url,
                                                       data=params,
                                                       raise_exception=True)
    cancelled_orders = decoded_response['result']['data']['success']
    if cancelled_orders:
        result.extend(decoded_response['result']['data']['success'].split(','))
    return result


def parse_order_info(data):
    order_status = None
    if data['orderState'] == 2:
        order_status = core_enums.ExchangeOrderStatus.CLOSED.value
    if data['orderState'] == 4:
        order_status = core_enums.ExchangeOrderStatus.CANCELED.value
    if data['orderState'] == 3:
        order_status = core_enums.ExchangeOrderStatus.CLOSED.value
    return {'pair': from_specific_to_common(data['symbol']),
            'volume': data['orderAmount'],
            'executed_volume': data['dealAmount'],
            'price': data['orderPrice'],
            'avgPrice': data['avgPrice'],
            'order_id': data['orderId'],
            'order_status': order_status}


def get_order_info(api_key, secret, pair, order_id):
    specific_pair = from_common_to_specific(pair)
    url = "{0}/trade/orderInfo".format(BITFOREX_API_URL)
    params = sign_request("/api/v1/trade/orderInfo", api_key, secret, {'symbol': specific_pair,
                                                                       'orderId': order_id})
    decoded_response = http_utils.execute_http_request(method='POST',
                                                       url=url,
                                                       data=params,
                                                       raise_exception=True)
    check_response_for_success(decoded_response)
    return parse_order_info(decoded_response['result']['data'])


def get_orders_info(api_key, secret, pair, order_ids):
    specific_pair = from_common_to_specific(pair)
    url = "{0}/trade/multiOrderInfo".format(BITFOREX_API_URL)
    params = sign_request("/api/v1/trade/multiOrderInfo", api_key, secret, {'symbol': specific_pair,
                                                                            'orderIds': ','.join(order_ids)})
    decoded_response = http_utils.execute_http_request(method='POST',
                                                       url=url,
                                                       data=params,
                                                       raise_exception=True)
    check_response_for_success(decoded_response)
    result = []
    for item in decoded_response['result']['data']:
        result.append(parse_order_info(item))
    return result


def get_trades(pair, size=1):
    specific_pair = from_common_to_specific(pair)
    url = "{0}/market/trades?symbol={1}&size={2}".format(BITFOREX_API_URL, specific_pair, size)
    decoded_response = http_utils.execute_http_request(method='GET',
                                                       url=url,
                                                       raise_exception=True)
    check_response_for_success(decoded_response)
    result = []
    for item in decoded_response['result']['data']:
        tid = int(item['tid'])
        volume = item['amount']
        price = item['price']
        time = item['time']
        side = 'BUY'
        if item['direction'] == '2':
            side = 'SELL'
        result.append({'tid': tid,
                       'price': price,
                       'volume': volume,
                       'side': side,
                       'time': time})
    return result






