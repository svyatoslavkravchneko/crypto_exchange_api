import asyncio
import time

import aiohttp
import traceback

from aiohttp.http_websocket import WS_CLOSED_MESSAGE
from django.core.management import BaseCommand
from django.utils import timezone
from django.core.cache import cache

from crypto_trading_api_exchange_wrappers.bitforex import (from_common_to_specific,
                                                           from_specific_to_common)
from crypto_trading_api.celery import app
from crypto_trading_api_core.utils import ws_utils


def get_all_required_pairs_for_ws_depth_subscribe(exchange):
    cache_name = "all_required_pairs_for_{0}_ws_depth_subscribe".format(exchange)
    cache_value = cache.get(cache_name, {})
    return cache_value


def update_subscription_data(exchange, subscription_data):
    is_subscription_data_updated = False
    all_pairs_cache_name = "all_required_pairs_for_{0}_ws_depth_subscribe".format(exchange)
    all_required_pairs = subscription_data["all_required_pairs"]

    added_pairs_cache_name = "new_pairs_for_{0}_ws_depth_subscribe".format(exchange)
    pairs_requested_to_add = cache.get(added_pairs_cache_name, {})
    for pair, pair_data in pairs_requested_to_add.items():
        if pair not in all_required_pairs:
            all_required_pairs[pair] = pair_data
            subscription_data["pairs_requested_to_add"][pair] = pair_data
            is_subscription_data_updated = True

    removed_pairs_cache_name = "new_pairs_for_{0}_ws_depth_unsubscribe".format(exchange)
    pairs_requested_to_remove = cache.get(removed_pairs_cache_name, [])
    for pair in pairs_requested_to_remove:
        if pair in all_required_pairs:
            del all_required_pairs[pair]
            subscription_data["pairs_requested_to_remove"].append(pair)
            is_subscription_data_updated = True
    if pairs_requested_to_add:
        cache.delete(added_pairs_cache_name)
    if pairs_requested_to_remove:
        cache.delete(removed_pairs_cache_name)
    if is_subscription_data_updated:
        print("{0} Subscription data is updated: {1}".format(timezone.now(), subscription_data))
        cache.set(all_pairs_cache_name, all_required_pairs)


@asyncio.coroutine
def run_periodic_subscription_data_update(exchange, subscription_data):
    while True:
        loop = asyncio.get_event_loop()
        yield from loop.run_in_executor(None, update_subscription_data, exchange, subscription_data)
        yield from loop.run_in_executor(None, time.sleep, 1)


async def subscribe_to_updates(ws, pairs_to_subscribe, depth_event, depth_type):
    for common_pair in pairs_to_subscribe:
        specific_pair = from_common_to_specific(common_pair)
        await ws.send_json([{"type": "subHq",
                             "event": depth_event,
                             "param": {"businessType": specific_pair, "dType": depth_type}}])


# should not be used, as "subHq_cancel" doesn't work as described in docs
async def unsubscribe_from_updates(ws, pairs_to_unsubscribe, depth_event):
    for common_pair in pairs_to_unsubscribe:
        specific_pair = from_common_to_specific(common_pair)
        await ws.send_json([{"type": "subHq_cancel",
                             "event": depth_event,
                             "symbol": specific_pair}])


async def restart_ws_client(session, subscription_data):
    print("{time} Restarting client websocket...".format(time=timezone.now()))
    await session.close()
    await run_depth_ws(subscription_data)


async def run_depth_ws(subscription_data):
    exchange = "BITFOREX"
    url = "wss://www.bitforex.com/mkapi/coinGroup1/ws"
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(url)
    try:
        print(timezone.now(), "Started {0} depth websocket client".format(exchange))
        depth_event = "depth10"
        depth_type = 0
        await subscribe_to_updates(ws, subscription_data["all_required_pairs"], depth_event, depth_type)
        while True:
            new_pairs_to_subscribe = subscription_data["pairs_requested_to_add"]
            subscription_data["pairs_requested_to_add"] = {}
            await subscribe_to_updates(ws, new_pairs_to_subscribe, depth_event, depth_type)
            new_pairs_to_unsubscribe = subscription_data["pairs_requested_to_remove"]
            if new_pairs_to_unsubscribe:
                print("{0} Received unsubscribe request for {1}".format(timezone.now(), new_pairs_to_unsubscribe))   # important note, because we will restart client
                subscription_data["pairs_requested_to_remove"] = []
                await restart_ws_client(session, subscription_data)   # unsubscribe described in docs did not work
                return
            try:
                message = await ws.receive(3)
            except asyncio.TimeoutError:
                await ws.send_str("ping_p")
                try:
                    message = await ws.receive(4)
                except asyncio.TimeoutError:
                    await restart_ws_client(session, subscription_data)
                    return
            print(timezone.now(), message)
            if message is WS_CLOSED_MESSAGE:
                await restart_ws_client(session, subscription_data)
                return
            if message.data == "pong_p":
                continue
            message = ws_utils.load_msg_data(message)
            event = message.get("event")
            if event == depth_event:
                specific_pair = message.get("param", {}).get("businessType")
                common_pair = from_specific_to_common(specific_pair)
                order_book_data = message.get("data", {})
                print(timezone.now(), "{0}: {1}".format(common_pair, order_book_data))
                if order_book_data:
                    routing_key = get_all_required_pairs_for_ws_depth_subscribe(exchange).get(
                        common_pair, {}).get("routing_key_send_updates_to")
                    app.send_task("process_order_book_update",
                                  kwargs={'exchange': exchange,
                                          'pair': common_pair,
                                          'order_book_data': order_book_data},
                                  queue=routing_key)

    except Exception as exc:
        print(timezone.now(), "Exception on {0} websocket: '{1}'".format(exchange, traceback.format_exc()))
        await restart_ws_client(session, subscription_data)


class Command(BaseCommand):
    help = 'Run BITFOREX websocket depth parser'

    def handle(self, *args, **options):
        exchange = "BITFOREX"
        subscription_data = {
            "all_required_pairs": get_all_required_pairs_for_ws_depth_subscribe(exchange),
            "pairs_requested_to_add": {},
            "pairs_requested_to_remove": []
        }
        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            run_depth_ws(subscription_data),
            run_periodic_subscription_data_update(exchange, subscription_data)
        ))
