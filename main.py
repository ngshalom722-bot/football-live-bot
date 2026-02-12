import requests
import time
def main():
    print("⚡️ Bot is running...")
    while True:
        print("🔍 Checking for matches...")
        # 這裡放你原本的比賽分析邏輯
        # 例如：
        # matches = get_live_matches()
        # for match in matches:
        #     if is_good_signal(match):
        #         send_telegram_message(match)
        time.sleep(60)  # 每 60 秒檢查一次
import os
# 讀取環境變數（Railway 會自動提供）
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
sent_signals = set()
# Telegram 發送訊息
def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)
# API-Football：抓取所有進行中的比賽
def get_live_matches():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": FOOTBALL_API_KEY}
    r = requests.get(url, headers=headers).json()
    return r.get("response", [])
# The Odds API：抓賠率
def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
    try:
        return requests.get(url).json()
    except:
        return None
# SofaScore：抓走地數據（xG、射門、角球等）
def get_sofascore_stats(event_id):
    try:
        url = f"https://api.sofascore.com/api/v1/event/{event_id}/statistics"
        r = requests.get(url).json()
        groups = r["statistics"][0]["groups"]
        stats = {
            "shots": groups[0]["statisticsItems"][0]["home"],
            "shots_on": groups[0]["statisticsItems"][1]["home"],
            "dangerous": groups[2]["statisticsItems"][2]["home"],
            "corners": groups[1]["statisticsItems"][2]["home"],
            "attacks": groups[2]["statisticsItems"][0]["home"],
            "xg": groups[3]["statisticsItems"][0]["home"],
        }
        return stats
    except:
        return None
# AI 分析（平衡模式）
def analyze(match, stats):
    minute = match["fixture"]["status"]["elapsed"]
    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]
    match_name = f"{home} vs {away}"
    if stats is None:
        return None
    pace = stats["attacks"] / max(minute, 1)
    score = 0
    if stats["xg"] < 0.6: score += 1
    if stats["shots_on"] <= 2: score += 1
    if stats["dangerous"] < 55: score += 1
    if pace < 0.6: score += 1

    if score >= 3:
        return f"""
📉【小球訊號】
比賽：{match_name}
時間：{minute}'
xG：{stats['xg']}
射正：{stats['shots_on']}
危險進攻：{stats['dangerous']}%
節奏：{pace:.2f} / 分鐘
符合 4 項中的 {score} 項
建議：小球有價值
"""
    return None
# 主程式
def main():
    while True:
        matches = get_live_matches()
        for m in matches:
            match_id = m["fixture"]["id"]
            if match_id in sent_signals:
                continue
            stats = get_sofascore_stats(match_id)
            signal = analyze(m, stats)
            if signal:
                send(signal)
                sent_signals.add(match_id)
        time.sleep(10)
if __name__ == "__main__":
    print("⚡️ Bot is starting...")
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
