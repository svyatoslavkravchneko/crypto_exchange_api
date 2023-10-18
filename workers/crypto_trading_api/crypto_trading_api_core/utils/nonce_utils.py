import time


def generate_nonce():
    return int(time.time() * 1000)