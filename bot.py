import json
from telethon import TelegramClient, events, Button
from supabase import create_client
from fastapi import FastAPI

# Hardcoded credentials
API_ID = "24335549"
API_HASH = "90c0e5492eff63ebf4aa43b9ec005422"
PHONE_NUMBER = "+6285784572602"
SUPABASE_URL = "https://qzkueoaoogwdikwcslzi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6a3Vlb2Fvb2d3ZGlrd2NzbHppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMzMDExMzUsImV4cCI6MjA1ODg3NzEzNX0.SDvAdmhMEwllKMiSnC1GFRxY0mX3_fBqYeALbNyUX_8"

# Initialize Telegram client (akun biasa, bukan bot)
client = TelegramClient('user', API_ID, API_HASH)

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI()

def get_keywords():
    response = supabase.table("settings").select("keywords").single().execute()
    return response.data["keywords"] if response.data else []

def get_channels():
    response = supabase.table("settings").select("channels").single().execute()
    return response.data["channels"] if response.data else []

def get_admin_channel():
    response = supabase.table("settings").select("admin_channel").single().execute()
    return int(response.data["admin_channel"]) if response.data and response.data["admin_channel"] else None

@client.on(events.NewMessage)
async def handler(event):
    if event.is_channel and event.chat.username:
        chat_username = event.chat.username.lower()
        message_text = event.raw_text.lower()
        keywords = get_keywords()
        admin_channel = get_admin_channel()
        allowed_channels = [channel.lower() for channel in get_channels()]
        
        print(f"📩 Menerima pesan dari: {chat_username}")
        print(f"🔍 Menfess terdeteksi? {'Ya' if any(keyword in message_text for keyword in keywords) else 'Tidak'}")
        
        if chat_username in allowed_channels and any(keyword in message_text for keyword in keywords):
            if not admin_channel:
                print("⚠️ Channel admin belum diatur!")
                return
            
            menfess_link = f"https://t.me/{chat_username}/{event.message.id}"
            buttons = [[Button.url("Lihat Menfess", menfess_link)]]
            try:
                await client.send_message(
                    admin_channel, 
                    f"Menfess ditemukan: {event.raw_text}\n🔗 [Klik untuk melihat]({menfess_link})", 
                    buttons=buttons,
                    link_preview=False
                )
                print("✅ Menfess berhasil dikirim ke channel admin")
            except Exception as e:
                print(f"❌ Gagal mengirim menfess: {e}")

@client.on(events.NewMessage(pattern='/setkeyword (.+)'))
async def set_keyword(event):
    new_keywords = event.pattern_match.group(1).split(', ')
    response = supabase.table("settings").update({"keywords": new_keywords}).eq("id", 1).execute()
    if response.data is None:
        await event.reply(f"❌ Gagal memperbarui keyword: {response.error}")
    else:
        await event.reply("✅ Keywords berhasil diperbarui!")

@client.on(events.NewMessage(pattern='/setchannel (.+)'))
async def set_channel(event):
    new_channels = event.pattern_match.group(1).split(', ')
    response = supabase.table("settings").update({"channels": new_channels}).eq("id", 1).execute()
    if response.data is None:
        await event.reply(f"❌ Gagal memperbarui channel: {response.error}")
    else:
        await event.reply("✅ Channel berhasil diperbarui!")

@client.on(events.NewMessage(pattern='/getidchannel'))
async def get_id_channel(event):
    await event.reply(f"ID channel ini: {event.chat_id}")

@client.on(events.NewMessage(pattern='/setidchannel (.+)'))
async def set_id_channel(event):
    new_channel = event.pattern_match.group(1)
    response = supabase.table("settings").update({"admin_channel": new_channel}).eq("id", 1).execute()
    if response.data is None:
        await event.reply(f"❌ Gagal memperbarui channel admin: {response.error}")
    else:
        await event.reply("✅ Channel admin berhasil diperbarui!")

@app.get("/")
def read_root():
    return {"message": "Bot berjalan!"}

print("Client berjalan... Login dengan akun biasa.")
client.start(phone=PHONE_NUMBER)
client.run_until_disconnected()
