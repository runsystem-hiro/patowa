# 🚻 PATOWA --- トイレ・喫煙所混雑可視化モック

Raspberry Pi (Zero 2W / 4B) 上で動作する、FastAPI + Jinja2
によるシンプルな可視化モックです。\
男子トイレと喫煙所の「利用人数」をダミーデータで生成し、Web ブラウザに混雑度をリアルタイム表示します。\
PoC・デモ用途に適した構成で、社内 LAN からのアクセスを想定しています。

---

## 🎯 構成

- Raspberry Pi OS Bookworm (32bit)\
- Python 3.11 + FastAPI + Uvicorn\
- Jinja2 による HTML テンプレート\
- JavaScript によるフロントエンド更新（fetch）\
- systemd 管理による常駐運用

---

## 📂 ディレクトリ構成

```bash
/home/pi/patowa/
├── main.py                # FastAPI アプリ本体
├── templates/
│   ├── index.html          # 本番用UI
│   ├── dev.html            # UI検証用
└── .venv/                 # Python仮想環境
```

---

## 📦 依存パッケージ

仮想環境内で以下をインストールします：

```bash
pip install fastapi uvicorn jinja2
```

---

## 🚀 初回セットアップ手順

```bash
# 1) ディレクトリ作成
mkdir -p /home/pi/patowa && cd /home/pi/patowa

# 2) 仮想環境構築
python3 -m venv .venv
source .venv/bin/activate

# 3) 依存インストール
pip install fastapi uvicorn jinja2

# 4) サービス起動 (開発時)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔄 systemd サービス運用

`/etc/systemd/system/patowa.service` を作成：

```ini
[Unit]
Description=FastAPI patowa app
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/patowa
ExecStart=/home/pi/patowa/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 操作コマンド

動作 コマンド

---

起動 `sudo systemctl start patowa`
停止 `sudo systemctl stop patowa`
再起動 `sudo systemctl restart patowa`
ステータス `systemctl status patowa`

---

## 🖥️ 表示 UI の特徴

- 定員と利用人数をもとに混雑度を計算\
- 混雑度に応じて色とアイコン（😃／😐／😫）を切り替え\
- 履歴スパークライン（直近 30 点の推移）を描画\
- `/docs` で Swagger UI, `/redoc` で ReDoc 表示\
- `/healthz` で死活確認

---

## 🧪 テスト手順

1.  `http://raspi-dev.local:8000/` にブラウザでアクセス\
2.  利用人数が 5 秒ごとにランダムで変動することを確認\
3.  `/dev` にアクセスして UI 改良版を検証\
4.  `/healthz` が `{"ok": true, "time": ...}` を返すことを確認

---

## 📝 ライセンス

MIT License\
社内 PoC・デモ用途での利用を想定

---

Powered by hiro
