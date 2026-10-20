# TikTok Live to Firebase 24/7 Cloud Bridge (Flask Web Service Edition)
import os
import threading
import time
import requests
from flask import Flask
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import GiftEvent, CommentEvent

app = Flask(__name__)
FIREBASE_URL = "https://hexlak-default-rtdb.firebaseio.com/"

@app.route('/')
def home():
    return "Hexol TikTok Bridge is running 24/7!"

def run_tiktok_bot():
    current_streamer = None
    while True:
        try:
            res = requests.get(f"{FIREBASE_URL}/active_streamer.json")
            streamer = res.json()
        except:
            streamer = None

        if streamer and streamer != current_streamer:
            current_streamer = streamer
            print(f"🔄 Yeni aktif yayıncıya bağlanılıyor: @{current_streamer}")
            
            client = TikTokLiveClient(unique_id=current_streamer)

            @client.on("comment")
            async def on_comment(event: CommentEvent):
                msg_data = {
                    "senderId": str(event.user.user_id),
                    "senderName": event.user.nickname,
                    "message": event.comment,
                    "timestamp": 1700000000000
                }
                try:
                    requests.post(f"{FIREBASE_URL}/global_chat.json", json=msg_data)
                except:
                    pass

            @client.on("gift")
            async def on_gift(event: GiftEvent):
                if event.gift.streakable and not event.gift.repeat_end:
                    return
                gift_data = {
                    "senderName": event.user.nickname,
                    "giftName": event.gift.name,
                    "count": event.gift.repeat_count,
                    "diamonds": event.gift.diamond_count * event.gift.repeat_count
                }
                try:
                    requests.put(f"{FIREBASE_URL}/live_events/latest_gift.json", json=gift_data)
                except:
                    pass

            try:
                client.run()
            except Exception as e:
                print("Yayın akışı kesildi:", e)
                current_streamer = None
        
        time.sleep(10)

if __name__ == '__main__':
    t = threading.Thread(target=run_tiktok_bot)
    t.daemon = True
    t.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
