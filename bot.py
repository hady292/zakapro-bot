
import os
import json
import logging
import re
import html
import feedparser
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

RSS_URL = os.getenv("RSS_URL", "")
RSS_URLS = os.getenv("RSS_URLS", RSS_URL)

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
        summary = "مقال جديد ومفيد تم اختياره تلقائياً من مصادر ZakaPro."

    return f"""🔥 {title}

📌 ملخص سريع:
{summary}

💡 تابع التفاصيل الكاملة من الرابط بالأسفل.

#ZakaPro #ذكاء_اصطناعي #تقنية"""


def get_rss_list():
    return [url.strip() for url in RSS_URLS.split(",") if url.strip()]


async def notify_admin(context, message):
    if ADMIN_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=message)
        except Exception as e:
            logger.error(f"Admin notify failed: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ZakaPro Bot V5 Free يعمل بنجاح\n\n"
        "الأوامر:\n"
        "/status\n"
        "/run\n"
        "/stats\n"
        "/help"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 أوامر البوت:\n\n"
        "/status - حالة البوت\n"
        "/run - نشر يدوي آخر المقالات\n"
        "/stats - عدد المقالات المنشورة\n"
        "/help - المساعدة"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rss_count = len(get_rss_list())
    await update.message.reply_text(
        "✅ البوت يعمل\n"
        f"📡 عدد مصادر RSS: {rss_count}\n"
        f"🗂 المقالات المحفوظة: {len(sent_articles)}\n"
        f"⏱ الفحص كل: {CHECK_INTERVAL} ثانية"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 إحصائيات ZakaPro:\n\n"
        f"✅ عدد المقالات المنشورة سابقاً: {len(sent_articles)}"
    )


async def post_latest(context, manual=False):
    posted_count = 0
    rss_list = get_rss_list()

    if not rss_list:
        await notify_admin(context, "⚠️ لا يوجد RSS_URL أو RSS_URLS في الإعدادات.")
        return 0

    for rss_url in rss_list:
        try:
            feed = feedparser.parse(rss_url)

            if getattr(feed, "bozo", False):
                logger.warning(f"RSS parse warning: {rss_url}")

            for entry in feed.entries[:5]:
                link = entry.get("link")
                title = entry.get("title", "مقال جديد")
                summary = (
                    entry.get("summary")
                    or entry.get("description")
                    or entry.get("subtitle")
                    or ""
                )

                if not link or link in sent_articles:
                    continue

                text = rewrite_free(title, summary)

                button = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📖 اقرأ المقال", url=link)]
                ])

                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=text,
                    reply_markup=button,
                    disable_web_page_preview=False
                )

                sent_articles.add(link)
                save_sent(sent_articles)
                posted_count += 1

        except Exception as e:
            logger.error(f"Error processing RSS {rss_url}: {e}")
            await notify_admin(context, f"⚠️ خطأ في RSS:\n{rss_url}\n\n{e}")

    return posted_count


async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("❌ غير مصرح لك")
        return

    await update.message.reply_text("⏳ جاري فحص RSS والنشر...")
    count = await post_latest(context, manual=True)

    if count:
        await update.message.reply_text(f"🚀 تم نشر {count} مقال جديد")
    else:
        await update.message.reply_text("ℹ️ لا توجد مقالات جديدة للنشر")


async def auto(context: ContextTypes.DEFAULT_TYPE):
    await post_latest(context)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN غير موجود")
    if not CHANNEL_ID:
        raise ValueError("CHANNEL_ID غير موجود")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("run", run))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_cmd))

    app.job_queue.run_repeating(auto, interval=CHECK_INTERVAL, first=10)

    logger.info("ZakaPro Bot V5 Free started")
    app.run_polling()


if __name__ == "__main__":
    main()
