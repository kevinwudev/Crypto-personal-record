import ccxt
import polars as pl



def get_info_table(apikey, secret, password) -> pl.DataFrame():
    # 初始化 OKX API
    exchange = ccxt.okx({
        'apiKey': apikey,
        'secret': secret,
        'password': password,
    })

    positions = exchange.privateGetAccountPositions()['data']

    data = {}
    data['symbol'] = []
    data['size'] = []
    data['entry_price'] = []
    data['current_price'] = []
    data['unrealized_pnl'] = []
    data['margin'] = []
    data['leverage'] = []



    for pos in positions:
        if float(pos['pos']) != 0 :
            data['symbol'].append(pos['instId'])
            data['size'].append(round(float(pos['pos']), 3))
            data['entry_price'].append(float(pos['avgPx']))
            data['current_price'].append(float(pos['last']))
            data['unrealized_pnl'].append(round(float(pos['upl']), 3))
            data['margin'].append(round(float(pos['margin']), 3))
            data['leverage'].append(float(pos['lever']))

    df = pl.DataFrame(data)

    total_porfolio = df['unrealized_pnl'].sum()

    return df, total_porfolio


