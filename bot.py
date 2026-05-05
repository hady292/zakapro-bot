import os
import json
import logging
import re
import html
import feedparser
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

RSS_URL = os.getenv("RSS_URL", "")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "3600"))
DATA_FILE = "sent_articles.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_sent():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_sent(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f, ensure_ascii=False, indent=2)


sent_articles = load_sent()


def is_admin(update: Update):
    return update.effective_user and update.effective_user.id == ADMIN_ID


def clean_text(text):
    text = html.unescape(text or "")
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def rewrite_free(title, summary):
    title = clean_text(title)
    summary = clean_text(summary)

    if len(summary) > 350:
        summary = summary[:350].rsplit(" ", 1)[0] + "..."

    if not summary:
        summary = "مقال جديد ومفيد تم اختياره تلقائياً."

    return f"""🔥 {title}

📌 ملخص:
{summary}

💡 التفاصيل في الرابط 👇
"""


def generate_article():
    titles = [
        "أفضل طرق الربح من الإنترنت 2026",
        "كيف تبدأ مشروع ناجح من الصفر",
        "دليل الذكاء الاصطناعي للمبتدئين",
        "أسرار النجاح في العمل الحر",
        "كيف تحقق دخل يومي ثابت"
    ]

    tips = [
        "ابدأ بخطة واضحة",
        "تعلم مهارات جديدة",
        "استمر ولا تستسلم",
        "استثمر وقتك بذكاء",
        "تابع التطور التقني"
    ]

    title = random.choice(titles)

    content = f"🔥 {title}\n\n"
    content += "📌 أهم النقاط:\n\n"

    for tip in random.sample(tips, 3):
        content += f"✔️ {tip}\n"

    content += "\n💡 استمر بالتعلم وستنجح.\n"
    content += "\n#ZakaPro #نجاح #ربح"

    return content


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("❌ غير مصرح")
        return

    article = generate_article()

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=article
    )

    await update.message.reply_text("🚀 تم توليد ونشر مقال في القناة")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 البوت يعمل\n\n/status\n/run\n/generate")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"✅ البوت يعمل\n📊 مقالات محفوظة: {len(sent_articles)}"
    )


async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("❌ غير مصرح")
        return

    await update.message.reply_text("⏳ جاري النشر...")
    count = await post_latest(context)

    if count:
        await update.message.reply_text(f"🚀 تم نشر {count} مقال")
    else:
        await update.message.reply_text("ℹ️ لا توجد مقالات جديدة")


async def post_latest(context):
    posted = 0

    if not RSS_URL:
        return 0

    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries[:5]:
        link = entry.get("link")
        title = entry.get("title", "")
        summary = entry.get("summary", "")

        if not link or link in sent_articles:
            continue

        text = rewrite_free(title, summary)

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
        posted += 1

    return posted


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("run", run))
    app.add_handler(CommandHandler("generate", generate))

    app.run_polling()


if __name__ == "__main__":
    main()
