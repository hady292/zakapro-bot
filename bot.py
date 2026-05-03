import os
import json
import logging
import feedparser
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# تحميل المتغيرات من .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RSS_URL = os.getenv("RSS_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

CHECK_INTERVAL = 3600
DATA_FILE = "sent_articles.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل المقالات المرسلة سابقًا
def load_sent():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# حفظ المقالات
def save_sent(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f, ensure_ascii=False, indent=2)

sent_articles = load_sent()

# تحقق من الأدمن
def is_admin(update: Update):
    return update.effective_user and update.effective_user.id == ADMIN_ID

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ZakaPro Bot يعمل بنجاح")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت يعمل\n📡 RSS مفعل")

# نشر المقالات
async def post_latest(context):
    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries[:3]:
        link = entry.get("link")
        title = entry.get("title", "مقال جديد")

        if link and link not in sent_articles:
            text = f"📌 {title}\n\n🔗 {link}"

            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 اقرأ المقال", url=link)]
            ])

            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                reply_markup=button
            )

            sent_articles.add(link)
            save_sent(sent_articles)

# تشغيل يدوي
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("❌ غير مصرح لك")
        return

    await post_latest(context)
    await update.message.reply_text("🚀 تم النشر")

# تشغيل تلقائي
async def auto(context: ContextTypes.DEFAULT_TYPE):
    await post_latest(context)

# تشغيل البوت
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("run", run))

    app.job_queue.run_repeating(auto, interval=CHECK_INTERVAL, first=10)

    app.run_polling()

if __name__ == "__main__":
    main()
