import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# بياناتك
TELEGRAM_TOKEN = "حط_توكن_تيليجرام_هنا"
CHANNEL_ID = "@zakapro_channel"

# Blogger
BLOG_ID = "3446663962857726908"  # حط رقم مدونتك
ACCESS_TOKEN = os.getenv("BLOGGER_ACCESS_TOKEN")

# نشر مقال في بلوجر
def publish_to_blogger(title, content):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "kind": "blogger#post",
        "title": title,
        "content": content
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()

# أمر /generate
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = "مقال جديد 🔥"
    content = "<p>هذا مقال تجريبي تم إنشاؤه تلقائيًا.</p>"

    # نشر في Blogger
    post = publish_to_blogger(title, content)

    # نشر في تيليجرام
    await context.bot.send_message(chat_id=CHANNEL_ID, text=f"{title}\nتم النشر ✅")

    await update.message.reply_text("تم النشر في Blogger والقناة 🚀")

# تشغيل البوت
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("generate", generate))

print("Bot running...")
app.run_polling()
