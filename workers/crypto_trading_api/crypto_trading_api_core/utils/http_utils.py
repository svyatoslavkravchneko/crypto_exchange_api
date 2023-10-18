import requests
import requests
from crypto_trading_api_core.utils import logger_utils
from crypto_trading_api_core.exceptions.third_party_api_exception import ThirdPartyApiException

SESSION = requests.Session()


def check_response(response, content_type_format='json'):
    request = response.request
    url = request.url
    headers = request.headers._store
    body = request.body
    method = request.method
    is_error = False
    error_desc = None
    text = response.text

    log_msg = 'Receiving response. URl = {0} Headers = {1} Body = {2} Method = {3} Response = {4} Status Code = {5}'.format(
        url,
        headers,
        body,
        method,
        text[:1000],
        response.status_code)
    log_details = {'action': 'log_http_response',
                   'url': url,
                   'headers': headers,
                   'body': body,
                   'method': method,
                   'response': text[:1000],
                   'is_error': False,
                   'status_code': response.status_code}
    if response.status_code >= 400:
        is_error = True
        error_desc = 'Status Code >= 400'
    decoded_response = response.text
    try:
        if content_type_format == 'json':
            decoded_response = response.json()
    except:
        if response.status_code < 400:
            return {'result': [],
                    'is_error': False}
        logger_utils.log_error(log_msg, log_details)
        raise ThirdPartyApiException("Request failed. Url = {0} Response = {1} Status Code = {2}".format(url,
                                                                                                         response.text,
                                                                                                         response.status_code),
                                         status_code=response.status_code,
                                         response=[])
    if 'error' in decoded_response:
        is_error = True
        error_desc = decoded_response['error']
    if 'errors' in decoded_response:
        is_error = True
        error_desc = decoded_response['errors']
    if is_error and error_desc:
        log_details['is_error'] = True
        log_details['error_msg'] = error_desc
        logger_utils.log_error(log_msg, log_details)
        raise ThirdPartyApiException("Request failed. Url = {0} Response = {1} Status Code = {2}".format(url,
                                                                                                         decoded_response,
                                                                                                         response.status_code),
                                     status_code=response.status_code,
                                     response=decoded_response)
    logger_utils.log_info(log_msg, log_details)
    return {'result': decoded_response,
            'is_error': False}


def execute_http_request(content_type_format="json", **kwargs):
    log_msg = 'Prepare http request. Request Data = {0}'.format(kwargs)
    log_details = {'action': 'log_http_request'}
    for key, value in kwargs.items():
        log_details['http_param_{}'.format(key)] = value
    logger_utils.log_info(log_msg, log_details)
    if 'proxy_url' in kwargs:
        proxy_url = kwargs['proxy_url']
        if proxy_url:
            kwargs['proxies'] = {"http": "http://{0}".format(proxy_url),
                                 "https": "https://{0}".format(proxy_url)}
        del kwargs['proxy_url']
    if not kwargs.get('timeout'):
        kwargs['timeout'] = 60
    raise_exception = kwargs.get('raise_exception')
    if not kwargs.get('raise_exception'):
        try:
            response = SESSION.request(**kwargs)
            return check_response(response, content_type_format)
        except Exception as e:
            pass
    if raise_exception is True:
        del kwargs['raise_exception']
        response = SESSION.request(**kwargs)
        return check_response(response, content_type_format)
