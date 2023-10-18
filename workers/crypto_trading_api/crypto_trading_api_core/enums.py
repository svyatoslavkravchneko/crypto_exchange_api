from enum import Enum


class ExchangeNameEnum(Enum):
    BITFOREX = 'BITFOREX'


class OrderSideEnum(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class ExchangeOrderStatus(Enum):
    CLOSED = 'CLOSED'
    OPEN = 'OPEN'
    PENDING = 'PENDING'
    CANCELED = 'CANCELED'
    EXPIRED = 'EXPIRED'
    REJECTED = 'REJECTED'

    CHOICES = [(CLOSED, CLOSED),
               (OPEN, OPEN),
               (PENDING, PENDING),
               (CANCELED, CANCELED),
               (EXPIRED, EXPIRED),
               (REJECTED, REJECTED)]
