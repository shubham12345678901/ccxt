# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
import hashlib
from ccxt.base.errors import ExchangeError
from ccxt.base.precise import Precise


class mixcoins(Exchange):

    def describe(self):
        return self.deep_extend(super(mixcoins, self).describe(), {
            'id': 'mixcoins',
            'name': 'MixCoins',
            'countries': ['GB', 'HK'],
            'rateLimit': 1500,
            'version': 'v1',
            'userAgent': self.userAgents['chrome'],
            'has': {
                'cancelOrder': True,
                'CORS': False,
                'createOrder': True,
                'fetchBalance': True,
                'fetchOrderBook': True,
                'fetchTicker': True,
                'fetchTrades': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/51840849/87460810-1dd06c00-c616-11ea-9276-956f400d6ffa.jpg',
                'api': 'https://mixcoins.com/api',
                'www': 'https://mixcoins.com',
                'doc': 'https://mixcoins.com/help/api/',
            },
            'api': {
                'public': {
                    'get': [
                        'ticker/',
                        'trades/',
                        'depth/',
                    ],
                },
                'private': {
                    'post': [
                        'cancel',
                        'info',
                        'orders',
                        'order',
                        'transactions',
                        'trade',
                    ],
                },
            },
            'markets': {
                'BTC/USDT': {'id': 'btc_usdt', 'symbol': 'BTC/USDT', 'base': 'BTC', 'quote': 'USDT', 'baseId': 'btc', 'quoteId': 'usdt', 'maker': 0.0015, 'taker': 0.0025},
                'ETH/BTC': {'id': 'eth_btc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC', 'baseId': 'eth', 'quoteId': 'btc', 'maker': 0.001, 'taker': 0.0015},
                'BCH/BTC': {'id': 'bch_btc', 'symbol': 'BCH/BTC', 'base': 'BCH', 'quote': 'BTC', 'baseId': 'bch', 'quoteId': 'btc', 'maker': 0.001, 'taker': 0.0015},
                'LSK/BTC': {'id': 'lsk_btc', 'symbol': 'LSK/BTC', 'base': 'LSK', 'quote': 'BTC', 'baseId': 'lsk', 'quoteId': 'btc', 'maker': 0.0015, 'taker': 0.0025},
                'BCH/USDT': {'id': 'bch_usdt', 'symbol': 'BCH/USDT', 'base': 'BCH', 'quote': 'USDT', 'baseId': 'bch', 'quoteId': 'usdt', 'maker': 0.001, 'taker': 0.0015},
                'ETH/USDT': {'id': 'eth_usdt', 'symbol': 'ETH/USDT', 'base': 'ETH', 'quote': 'USDT', 'baseId': 'eth', 'quoteId': 'usdt', 'maker': 0.001, 'taker': 0.0015},
            },
        })

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privatePostInfo(params)
        balances = self.safe_value(response['result'], 'wallet')
        result = {'info': response}
        currencyIds = list(balances.keys())
        for i in range(0, len(currencyIds)):
            currencyId = currencyIds[i]
            code = self.safe_currency_code(currencyId)
            balance = self.safe_value(balances, currencyId, {})
            account = self.account()
            account['free'] = self.safe_string(balance, 'avail')
            account['used'] = self.safe_string(balance, 'lock')
            result[code] = account
        return self.parse_balance(result, False)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        request = {
            'market': self.market_id(symbol),
        }
        response = await self.publicGetDepth(self.extend(request, params))
        return self.parse_order_book(response['result'])

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        request = {
            'market': self.market_id(symbol),
        }
        response = await self.publicGetTicker(self.extend(request, params))
        ticker = self.safe_value(response, 'result')
        timestamp = self.milliseconds()
        last = self.safe_number(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_number(ticker, 'high'),
            'low': self.safe_number(ticker, 'low'),
            'bid': self.safe_number(ticker, 'buy'),
            'bidVolume': None,
            'ask': self.safe_number(ticker, 'sell'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_number(ticker, 'vol'),
            'quoteVolume': None,
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        timestamp = self.safe_timestamp(trade, 'date')
        symbol = None
        if market is not None:
            symbol = market['symbol']
        id = self.safe_string(trade, 'id')
        priceString = self.safe_string(trade, 'price')
        amountString = self.safe_string(trade, 'amount')
        price = self.parse_number(priceString)
        amount = self.parse_number(amountString)
        cost = self.parse_number(Precise.string_mul(priceString, amountString))
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': None,
            'side': None,
            'order': None,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'market': market['id'],
        }
        response = await self.publicGetTrades(self.extend(request, params))
        return self.parse_trades(response['result'], market, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        request = {
            'market': self.market_id(symbol),
            'op': side,
            'amount': amount,
        }
        if type == 'market':
            request['order_type'] = 1
            request['price'] = price
        else:
            request['order_type'] = 0
        response = await self.privatePostTrade(self.extend(request, params))
        return {
            'info': response,
            'id': str(response['result']['id']),
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        request = {
            'id': id,
        }
        return await self.privatePostCancel(self.extend(request, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            body = self.urlencode(self.extend({
                'nonce': nonce,
            }, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': self.hmac(self.encode(body), self.secret, hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    async def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = await self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            #
            # todo add a unified standard handleErrors with self.exceptions in describe()
            #
            #     {"status":503,"message":"Maintenancing, try again later","result":null}
            #
            if response['status'] == 200:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))
