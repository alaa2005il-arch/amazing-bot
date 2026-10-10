import os
import json
import requests

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "").strip().strip('"')
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip().strip('"')

def upstash_command(*args):
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        print("⚠️ Upstash URL/TOKEN missing", flush=True)
        return None
    try:
        # Upstash REST API expects JSON array: ["GET", "key"] etc
        res = requests.post(
            UPSTASH_URL,
            headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"},
            json=list(args),
            timeout=8
        )
        data = res.json()
        if "result" in data:
            return data["result"]
        else:
            print(f"Upstash error: {data}", flush=True)
            return None
    except Exception as e:
        print(f"Upstash exception: {e}", flush=True)
        return None

def load_data():
    """يحمل الداتا من Upstash Frankfurt - للأبد"""
    print("📥 Loading data from Upstash...", flush=True)
    result = upstash_command("GET", "bsf_data")
    if result:
        try:
            loaded = json.loads(result)
            print(f"✅ Loaded {len(loaded)} users from Upstash", flush=True)
            return loaded
        except Exception as e:
            print(f"❌ JSON parse error: {e}", flush=True)
            return {}
    else:
        print("ℹ️ No data in Upstash yet, starting empty", flush=True)
        # جرب يحمل من الملف المحلي القديم كـ backup مرة وحدة
        try:
            if os.path.exists("bsf_data.json"):
                with open("bsf_data.json", "r", encoding="utf-8") as f:
                    old = json.load(f)
                    print(f"📂 Found old local file with {len(old)} users, migrating to Upstash...", flush=True)
                    save_data(old)
                    return old
        except:
            pass
        return {}

def save_data(data):
    """يحفظ الداتا في Upstash للأبد + ملف محلي مؤقت"""
    try:
        json_str = json.dumps(data, ensure_ascii=False)
        # احفظ في Upstash
        upstash_command("SET", "bsf_data", json_str)
        print(f"💾 Saved {len(data)} users to Upstash", flush=True)
    except Exception as e:
        print(f"❌ Upstash save failed: {e}", flush=True)

    # احتياط محلي عشان Render ما يزعل
    try:
        with open("bsf_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass
