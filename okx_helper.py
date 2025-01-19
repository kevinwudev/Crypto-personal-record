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

    # data = {
    #     {
    #         'symbol': pos['instId'],
    #         'size': round(float(pos['pos']), 3),
    #         'entry_price': round(float(pos['avgPx']), 3),
    #         'current_price': round(float(pos['last']), 3),
    #         'unrealized_pnl': round(float(pos['upl']), 3),
    #         'margin': round(float(pos['margin']), 3),
    #         'leverage': float(pos['lever'])
    #     }
    #     for pos in positions if float(pos['pos']) != 0
    # }

    # df = pl.DataFrame(data)

    total_porfolio = df['unrealized_pnl'].sum()

    return df, total_porfolio


if __name__ == '__main__':
    apikey = '0e1a38a4-60f6-4f6d-89c6-a2030ffa3b58'
    password = 'Kuan-0725'
    secret = '27626941CD32624B05D0283DC8E01F9E'

    df = get_info_table(apikey, secret, password)
    print(df['unrealized_pnl'].sum())

