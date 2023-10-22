# README #

The main goal of this project - is implement one universal API to connect to crypto exchanges and make operations on it.
Instead of REST-API - this service use rabbitmq and all communications are done via RABBIT

The best way to use it.
1 exchange account = 1 VPS to deploy it on it and use, as in general each exchange account will have IP restrictions.
Only REST-API is implemented.
Service consists from 2 queues:
1. Public - ticker, orderbook, etc
2. Account Data - balance,orders, trades, etc


To deploy it you need to provide name of public data queue and account data queue to make API requests and start worker as part of compose file.
In this project you can add third-party wrappers and use it.

From my oponion, it's easier than CCXT
