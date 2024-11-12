from flask import Flask, request, render_template, redirect, url_for
import yaml
import ccxt

app = Flask(__name__)

# 根路徑的處理，返回登錄頁面
@app.route('/')
def index():
    return render_template('index.html')

# 儲存表單數據
@app.route('/save', methods=['POST'])
def save_data():
    apiKey = request.form['apiKey']
    secret = request.form['secret']
    password = request.form['password']

    # 將數據寫入 YAML 文件
    data = {'okx': {'apiKey': apiKey, 'secret': secret, 'password': password}}
    with open('data.yaml', 'w') as file:
        yaml.dump(data, file)

    return redirect(url_for('portfolio'))

# 讀取 YAML 並顯示持倉資訊

@app.route('/portfolio')
def portfolio():
    with open('data.yaml', 'r') as file:
        data = yaml.safe_load(file)
        data = data['okx']

    try :                                                                                                                                     # 初始化 OKX API
        exchange = ccxt.okx({
            'apiKey': data['apiKey'],
            'secret': data['secret'],
            'password': data['password']
        })

        exchange.load_markets()
    
        # exchange = ccxt.okx({
        #     'apiKey': '0e1a38a4-60f6-4f6d-89c6-a2030ffa3b58',
        #     'secret': '27626941CD32624B05D0283DC8E01F9E',
        #     'password': 'Kuan-0725'
        # })
    
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
    
    
        # 傳遞表格到 HTML
        return render_template('index.html', table=table)

    except ccxt.BaseError as e:
        # 如果 API 鑰匙無效，回傳錯誤信息
        error_message = "Invalid API key or password. Please try again."
        return render_template('index.html', message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
