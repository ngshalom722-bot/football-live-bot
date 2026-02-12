import os
import time
import requests
import asyncio
from sofascore_wrapper.api import SofascoreAPI

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

import requests

def get_live_matches():
    print("📡 Fetching live matches...")

    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    response = requests.get(url)
    data = response.json()

    result = []
    for event in data.get("events", []):
        try:
            home = event["homeTeam"]["name"]
            away = event["awayTeam"]["name"]
            minute = event["time"]["minute"]
            stats = event.get("statistics", {}).get("summary", {})
            xg_home = stats.get("expectedGoals", {}).get("home", 0)
            xg_away = stats.get("expectedGoals", {}).get("away", 0)
            shots_home = stats.get("shotsOnTarget", {}).get("home", 0)
            shots_away = stats.get("shotsOnTarget", {}).get("away", 0)

            result.append({
                "home_team": home,
                "away_team": away,
                "minute": minute,
                "xg": round(xg_home + xg_away, 2),
                "shots_on_target": shots_home + shots_away,
                "dangerous_attacks_pct": 50,
                "pace": 0.5
            })
        except Exception as e:
            print(f"⚠️ Error parsing match: {e}")
    return result


def main():
    print("⚡️ Bot is running...")

    while True:
        try:
            matches = get_live_matches()
            for match in matches:
                if match["shots_on_target"] <= 1 and match["xg"] <= 0.5:
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
                    print(f"⏭ {match['home_team']} vs {match['away_team']} 不符合條件")
        except Exception as e:
            print(f"❌ Error during match check: {e}")
        time.sleep(60)
if __name__ == "__main__":
    print("⚡️ Bot is starting...")
    try:
        main()
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
