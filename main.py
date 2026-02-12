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

async def get_live_matches():
    print("📡 Fetching live matches...")
    api = SofascoreAPI()
    matches = await api.get_live_matches()
    await api.close()

    result = []
    for match in matches:
        try:
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            minute = match['time']['minute']
            stats = match['statistics']
            xg_home = stats['expectedGoals']['home']
            xg_away = stats['expectedGoals']['away']
            shots_home = stats['shotsOnTarget']['home']
            shots_away = stats['shotsOnTarget']['away']

            result.append({
                "home_team": home,
                "away_team": away,
                "minute": minute,
                "xg": round(xg_home + xg_away, 2),
                "shots_on_target": shots_home + shots_away,
                "dangerous_attacks_pct": 50,  # 可根據需要補上
                "pace": 0.5  # 可根據 possession 或其他數據估算
            })
        except Exception as e:
            print(f"⚠️ Error parsing match: {e}")
    return result

async def main():
    print("⚡️ Bot is running...")

    while True:
        try:
            matches = await get_live_matches()
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

        await asyncio.sleep(60)

if __name__ == "__main__":
    print("⚡️ Bot is starting...")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
