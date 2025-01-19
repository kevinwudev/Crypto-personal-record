from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import yaml
import ccxt
from okx_helper import get_info_table
import polars as pl
import pyarrow
from dotenv import load_dotenv
import os

# 加載 .env 文件中的環境變數
load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('app_secretkey')

USER_FILES_DIR = 'users'

def read_user_config(new_info: dict = None):
    '''讀取或更新 YAML 設定檔'''
    filepath = os.path.join(USER_FILES_DIR, "personal_setting.yaml")
    
    # 如果檔案不存在，初始化為空字典
    if not os.path.exists(filepath):
        user_info = {}
    else:
        with open(filepath, 'r') as file:
            user_info = yaml.safe_load(file) or {}

    # 如果提供了新資料，更新並儲存
    if new_info:
        user_info.update(new_info)
        with open(filepath, 'w') as file:
            yaml.safe_dump(user_info, file)

    return user_info

def generate_table():
    # 創建一個 Polars DataFrame
    df = pl.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"]
    })

    # 將 DataFrame 轉換為 HTML 表格
    html_table = df.to_pandas().to_html(classes='table table-striped table-hover table-bordered text-center', index=False)
    return html_table

@app.route('/')
def home():
    try:
        user_info = read_user_config()
        table = generate_table()
        if user_info is None:
            return render_template('index.html')
            
        if user_info is not None and 'OKX' in user_info:
            apikey = user_info['OKX']['apikey']
            secret = user_info['OKX']['secret']
            password = user_info['OKX']['password']
        
            assets_info, total_porfolio = get_info_table(apikey, secret, password)
            assets_info = assets_info.to_pandas().to_html(classes='table table-striped table-hover table-bordered text-center', 
                                                          index=False)

            return render_template('index.html', 
                                   assets_info = assets_info, 
                                   table = table, 
                                   total_porfolio = total_porfolio)

        else :
            # assets_info = None
            return render_template('index.html', assets_info=assets_info)

    except ccxt.BaseError as e:
        # 如果 API 鑰匙無效，回傳錯誤信息
        error_message = "Invalid API key or password. Please try again."
        return render_template('index.html', message=error_message)

    


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    
    OKX_user_config = {'OKX' :{}}
    if request.method == 'POST':
        api_key = request.form['apikey']
        secret = request.form['secret']
        password = request.form['password']
        
        OKX_user_config = {
            'OKX': {
                'apikey': api_key,
                'secret': secret,
                'password': password
            }
        }

        # 更新設定檔
        read_user_config(OKX_user_config)
        flash('Personal setting updated successfully！', 'success')
        return redirect(url_for('settings'))

    # GET 請求時，讀取 YAML 設定
    user_config = read_user_config()
    OKX_user_config = user_config.get('OKX', {'apikey': '', 'secret': '', 'password': ''})

    return render_template('settings.html', OKX_user_config=OKX_user_config)


if __name__ == '__main__':
    app.run(debug=True)
