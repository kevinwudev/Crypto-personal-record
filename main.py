import ccxt
import polars as pl
from typing import Dict, List
import os
from datetime import datetime

def get_okx_client(api_key: str, secret: str, password: str) -> ccxt.okx:
    """初始化OKX API客戶端"""
    return ccxt.okx({
        'apiKey': api_key,
        'secret': secret,
        'password': password,
        'enableRateLimit': True
    })

def fetch_positions(exchange: ccxt.okx) -> List[Dict]:
    """獲取持倉信息"""
    positions = exchange.privateGetAccountPositions()['data']
    return [
        {
            'symbol': pos['instId'],
            'size': float(pos['pos']),
            'entry_price': float(pos['avgPx']),
            'current_price': float(pos['last']),
            'unrealized_pnl': float(pos['upl']),
            'margin': float(pos['margin']),
            'leverage': float(pos['lever'])
        }
        for pos in positions if float(pos['pos']) != 0
    ]

def create_portfolio_df(positions: List[Dict]) -> pl.DataFrame:
    """將持倉數據轉換為Polars DataFrame並計算關鍵指標"""
    if not positions:
        return pl.DataFrame()
    
    df = pl.DataFrame(positions)
    
    return df.with_columns([
        (pl.col('unrealized_pnl') / pl.col('margin') * 100).alias('pnl_percentage'),
        (pl.col('current_price') - pl.col('entry_price')).alias('price_change'),
        ((pl.col('current_price') - pl.col('entry_price')) / pl.col('entry_price') * 100).alias('price_change_percentage')
    ]).sort('pnl_percentage', descending=True)

def main():
    # 從環境變量讀取API憑證
    api_key = os.getenv('OKX_API_KEY')
    secret = os.getenv('OKX_SECRET')
    password = os.getenv('OKX_PASSWORD')
    
    # 初始化交易所客戶端
    exchange = get_okx_client(api_key, secret, password)
    
    # 獲取持倉數據
    positions = fetch_positions(exchange)
    
    # 創建DataFrame並顯示結果
    df = create_portfolio_df(positions)
    if not df.is_empty():
        print("\n=== Portfolio Analysis ===")
        print(df.select([
            'symbol',
            'size',
            'entry_price',
            'current_price',
            'unrealized_pnl',
            'pnl_percentage',
            'leverage'
        ]))
    else:
        print("No active positions found.")

if __name__ == "__main__":
    main()