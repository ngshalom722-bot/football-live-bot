import os
import time
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print(f"📤 Sent message: {response.status_code}")

def analyze_match(match):
    # 模擬條件判斷：如果射正數 <= 1 且 xG <= 0.5，就發訊號
    if match["shots_on_target"] <= 1 and match["xg"] <= 0.5:
        return True
    return False

def get_live_matches():
    # 模擬 API 回傳的比賽資料（你可以改成實際 API）
    print("📡 Fetching live matches...")
    return [
        {
            "home_team": "Team A",
            "away_team": "Team B",
            "minute": 27,
            "xg": 0.42,
            "shots_on_target": 1,
            "dangerous_attacks_pct": 48,
            "pace": 0.55
        }
    ]

def main():
    print("⚡️ Bot is running...")

    while True:
        try:
            matches = get_live_matches()
            for match in matches:
                if analyze_match(match):
                    message = (
                        f"📉 *小球訊號*\n"
                        f"比賽：{match['home_team']} vs {match['away_team']}\n"
                        f"時間：{match['minute']}'\n"
                        f"xG：{match['xg']}\n"
                        f"射正：{match['shots_on_target']}\n"
                        f"危險進攻：{match['dangerous_attacks_pct']}%\n"
                        f"節奏：{match['pace']} / 分鐘\n"
                        f"建議：小球有價值"
                    )
                    send_telegram_message(message)
                else:
                    print("⏭ 無符合條件的比賽")
        except Exception as e:
            print(f"❌ Error during match check: {e}")

        time.sleep(60)

if __name__ == "__main__":
    print("⚡️ Bot is starting...")
    try:
        main()
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
