from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import yaml
import ccxt
from okx_helper import get_info_table

app = Flask(__name__)
app.secret_key = b'\xa3\x1b5\xf7\x84\x7f\xe6*\xec\x8d\xb6*\xfe\xc5\xd3\x99\xad\x85\x1e\x91\x97\xd9\xfc\x0e'

# 使用者資料存儲 (模擬資料庫)
users = {}
USER_FILES_DIR = 'users'

# 確保使用者設定檔資料夾存在
os.makedirs(USER_FILES_DIR, exist_ok=True)

def update_user_config(email : str, new_info : dict):
    '''讀取 YAML 設定檔'''
    filepath = os.path.join(USER_FILES_DIR, f"{email}.yaml")
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            user_info = yaml.safe_load(file) or {}
        user_info.update(new_info)

        with open(filepath, 'w') as file:
            yaml.safe_dump(user_info, file)

def get_user_info(email : str) -> dict:
    '''取得 USER info'''
    filepath = os.path.join(USER_FILES_DIR, f"{email}.yaml")
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            user_info = yaml.safe_load(file) or {}

        return user_info


def get_user_account() -> list:
    user_files_dir = 'users'
    
    if not os.path.exists(user_files_dir):
        return []
    
    account_list = [
        os.path.splitext(f)[0] 
        for f in os.listdir(user_files_dir)
        if f.endswith('.yaml')
    ]

    return account_list
    
def check_password(email : str, password : str) -> bool :
    filepath = os.path.join(USER_FILES_DIR, f"{email}.yaml")
    with open(filepath, 'r') as file:
        user_info = yaml.safe_load(file)
        
        return password ==  user_info['user_password']
    
def check_all_keys_in_dict(setting_info : list, user_info : dict) -> bool:
    return all(item in user_info for item in setting_info)
    
@app.route('/')
def home():
    if 'email' not in session:
        return redirect(url_for('login'))

    try:
        user_info = get_user_info(session['email'])
        if check_all_keys_in_dict(['OKX'], user_info):
            apikey = user_info['OKX']['apikey']
            secret = user_info['OKX']['secret']
            password = user_info['OKX']['password']

            assets_info = get_info_table(apikey, secret, password)

        else :
            assets_info = None
        return render_template('index.html', assets_info=assets_info)

    except ccxt.BaseError as e:
        # 如果 API 鑰匙無效，回傳錯誤信息
        error_message = "Invalid API key or password. Please try again."
        return render_template('index.html', message=error_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_account : list = get_user_account()

        if email in user_account and check_password(email, password):
            session['email'] = email
            flash('Successful login！', 'success')
            return redirect(url_for('home'))

        else:
            test = check_password(email=email, password=password)
            flash(f'Wrong email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_account : list = get_user_account()

        if '@gmail.com' not in email:
            flash('Please input available Gmail address！', 'warning')
            return redirect(url_for('register'))

        if email in user_account:
            flash('This account has been registered.', 'danger')
        else:
            users['user_password'] = password
            filepath = os.path.join(USER_FILES_DIR, f"{email}.yaml")
            with open(filepath, 'w') as file:
                yaml.safe_dump(users, file)
        
            flash('Successfully registered, please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'email' not in session:
        return redirect(url_for('login')) 

    user_config = {'OKX' :{}}
    if request.method == 'POST':
        api_key = request.form['apikey']
        secret = request.form['secret']
        password = request.form['password']
        
        user_config['OKX']['apikey'] = api_key
        user_config['OKX']['secret'] = secret
        user_config['OKX']['password'] = password

        update_user_config(session['email'], user_config)
        flash('Personal setting updated successfully！', 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html', user_config=user_config)


@app.route('/logout')
def logout():
    session.clear()
    session.pop('email', None)
    flash('Successfully log out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
