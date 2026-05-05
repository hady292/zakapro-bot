import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@zakapro_channel")
BLOG_ID = os.getenv("BLOG_ID", "3446663962857726908")
BLOGGER_ACCESS_TOKEN = os.getenv("BLOGGER_ACCESS_TOKEN")

def publish_to_blogger(title, content):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {
        "Authorization": f"Bearer {BLOGGER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "kind": "blogger#post",
        "title": title,
        "content": content
    }
    r = requests.post(url, headers=headers, json=data, timeout=30)
    return r.status_code, r.text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ البوت شغال\n\n"
        "الأوامر:\n"
        "/status - فحص الحالة\n"
        "/generate - توليد ونشر مقال\n"
        "/run - تشغيل يدوي"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "✅ البوت يعمل\n"
    msg += f"📢 القناة: {CHANNEL_ID}\n"
    msg += f"📝 BLOG_ID: {BLOG_ID}\n"

    if BLOGGER_ACCESS_TOKEN:
        msg += "🔑 Blogger Token: موجود ✅"
    else:
        msg += "🔑 Blogger Token: غير موجود ❌"

    await update.message.reply_text(msg)

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = "مقال جديد عن الذكاء الاصطناعي 🚀"
    content = """
    <h2>كيف يساعدك الذكاء الاصطناعي؟</h2>
    <p>الذكاء الاصطناعي أصبح أداة قوية تساعد في كتابة المقالات، تنظيم العمل، إنشاء الأفكار، وتحسين الإنتاجية.</p>
    <p>هذا المقال تم توليده ونشره تلقائيًا بواسطة بوت ZakaPro AI.</p>
    """

    await update.message.reply_text("⏳ جاري توليد ونشر المقال...")

    if not BLOGGER_ACCESS_TOKEN:
        await update.message.reply_text("❌ BLOGGER_ACCESS_TOKEN غير موجود في Render")
        return

    status_code, result = publish_to_blogger(title, content)

    if status_code in [200, 201]:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"🚀 تم نشر مقال جديد\n\n{title}"
        )
        await update.message.reply_text("✅ تم النشر في Blogger والقناة")
    else:
        await update.message.reply_text(
            f"❌ فشل النشر في Blogger\n\nStatus: {status_code}\n{result[:700]}"
        )

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate(update, context)

def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN غير موجود في Render Environment")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("run", run))

    print("✅ ZakaPro AI Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
