# TikTok Live to Firebase 24/7 Cloud Bridge
import time
import requests
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import GiftEvent, CommentEvent

FIREBASE_URL = "https://hexlak-default-rtdb.firebaseio.com/"

print("=== HEXOL CLOUD 24/7 BRIDGE STARTED ===")

def get_active_streamer():
    try:
        res = requests.get(f"{FIREBASE_URL}/active_streamer.json")
        return res.json()
    except Exception as e:
        print("Yayıncı alınamadı:", e)
        return None

if __name__ == '__main__':
    current_streamer = None
    while True:
        streamer = get_active_streamer()
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
