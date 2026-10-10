import 【entity-discord¦canonical_name=Discord】
from 【entity-discord¦canonical_name=Discord】.ext import commands
import os, json, random, time, traceback, requests
from 【entity-discord¦canonical_name=Discord】 import app_commands
from flask import Flask
from threading import Thread

# ==================== موقع وهمي عشان Render ====================
app = Flask('')
@app.route('/')
def home(): return "👑 BSF Bot Live - ابو عيسى 28 دودة ♾️"
def run(): app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
Thread(target=run, daemon=True).start()

# ==================== Upstash ====================
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "").strip('\"\'')
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip('\"\'')
def upstash_command(*args):
    if not UPSTASH_URL or not UPSTASH_TOKEN: return None
    try:
        r = requests.post(UPSTASH_URL, headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}, json=list(args), timeout=10)
        return r.json().get("result")
    except: return None

DATA_FILE = "bsf_data.json"
def load_data():
    res = upstash_command("GET", "bsf_data")
    if res:
        try: return json.loads(res)
        except: pass
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: pass
    return {}
def save_data(data):
    try: upstash_command("SET", "bsf_data", json.dumps(data, ensure_ascii=False))
    except: pass
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass
