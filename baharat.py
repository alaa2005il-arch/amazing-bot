def load_real_questions():
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE,"r",encoding="utf-8") as f:
                raw=json.load(f)
                out=[]
                for q in raw:
                    d={}
                    d["id"]=q.get("id",0)
                    d["q"]=q["q"]
                    d["options"]=q["options"]
                    d["answer"]=q["correct"]
                    d["level"]=(q.get("id",1)-1)//5
                    d["type"]="عام"
                    d["info"]=q.get("info","")
                    out.append(d)
                return out
        except:
            pass
    return []

QUESTIONS = load_real_questions()
if not QUESTIONS:
    QUESTIONS=[{"id":1,"q":"عاصمة فلسطين؟","options":["القدس","رام الله","غزة","نابلس"],"answer":0,"level":0,"type":"عام","info":"القدس"}]
