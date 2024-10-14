from flask import Flask, render_template
import requests
#TinyDBライブラリ
from tinydb import TinyDB, Query
#loggingを使うライブラリ
import logging
#時刻の取得ライブラリ
import time

# ログレベルを DEBUG に変更。
# logger.logにログを出力する。
logging.basicConfig(filename='logger.log', level=logging.DEBUG)
# logを出力しない場合は、この下の行のコメントを外す
#logging.disable(logging.CRITICAL)
logging.debug('プログラム開始。')

# WebAPIを取得しに行く関数
# 取得したWebAPIのデータ（tenki_data）をDBに書き込む
def get_api():
  logging.debug('get_api() の開始')
  #現時刻を取得。time.time()は小数点以下の値も返す。
  unix_time_now = int(time.time())

  # WebAPIを取得しに行く
  url = "https://weather.tsukumijima.net/api/forecast"
  payload = {"city":"130010"}
  tenki_data = requests.get(url, params=payload).json()

  # DBの中身をすべて削除
  db.truncate()

  # 取得したWebAPIのデータ（tenki_data）をDBに書き込む
  db.insert({"id":1, "tenki_data_org":tenki_data, "unix_time":unix_time_now})

  logging.debug('get_api() の終了')

  return tenki_data


#データベースの作成
db = TinyDB('sample.json')

app = Flask(__name__)

@app.route('/')
def index():
    #現時刻を取得。time.time()は小数点以下の値も返す。
    unix_time_now = int(time.time())

    # DBから以前のWebAPIのデータをtenki_dataに読み込む
    # Queryオブジェクトを作成
    que = Query()

    # DBから以前のWebAPIのデータの時刻を読み込む
    try:
        #エラーが起きなかったら
        unix_time_db = db.get(que.id==1)["unix_time"]
        logging.debug('unix_time_dbを取得 ： {}'.format(unix_time_db))

        logging.debug('nowとdbの時間差 ： {}'.format(unix_time_now - unix_time_db))

        # DBにある時刻と1時間（3600秒）以内の差ならばDBから取得
        if unix_time_now - unix_time_db <= 3600:
          logging.debug('DBにある時刻と1時間（3600秒）以内')
          tenki_data = db.get(que.id==1)["tenki_data_org"]
          logging.debug('3600秒以内のDBのtenki_data_orgを取得')
        else:
          # WebAPIを取得しに行く
          # 取得したWebAPIのデータ（tenki_data）をDBに書き込む
          logging.debug('DBにある時刻と1時間（3600秒）を超えているとき')
          tenki_data = get_api()
          logging.debug('WebAPIからのtenki_dataを取得') # : {}'.format(tenki_data))
    except:
        #エラーが起きたら（DBから取得できなかったら）
        #WebAPIを取得しに行く関数
        tenki_data = get_api()

    return render_template("template.html",
                          tenki_data=tenki_data)

app.run(host='0.0.0.0')
