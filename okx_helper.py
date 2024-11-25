import ccxt

def get_info_table(apikey, secret, password):
    # 初始化 OKX API
    exchange = ccxt.okx({
        'apiKey': apikey,
        'secret': secret,
        'password': password,
    })

    exchange.load_markets()

    # 獲取持倉數據
    positions = exchange.fetch_positions()

    # 將持倉數據轉換為表格
    table = [
        {
            'asset': pos['symbol'],
            'position': pos['contracts'],
            'entry_price': pos['entryPrice'],
            'current_price': pos['markPrice'],
            'profit_loss': pos['unrealizedPnl']
        }
        for pos in positions if float(pos['info']['pos']) != 0
    ]

    return table