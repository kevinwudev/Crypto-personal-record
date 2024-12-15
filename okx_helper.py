import ccxt

def get_info_table(apikey, secret, password):
    # 初始化 OKX API
    exchange = ccxt.okx({
        'apiKey': apikey,
        'secret': secret,
        'password': password,
    })

    positions = exchange.privateGetAccountPositions()['data']
    return [
        {
            'symbol': pos['instId'],
            'size': round(float(pos['pos']), 3),
            'entry_price': round(float(pos['avgPx']), 3),
            'current_price': round(float(pos['last']), 3),
            'unrealized_pnl': round(float(pos['upl']), 3),
            'margin': round(float(pos['margin']), 3),
            'leverage': float(pos['lever'])
        }
        for pos in positions if float(pos['pos']) != 0
    ]
