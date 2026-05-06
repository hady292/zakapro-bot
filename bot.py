import os
import json
import random
import logging
import requests
from pathlib import Path

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# يدعم الاسمين:
# TELEGRAM_TOKEN أو BOT_TOKEN
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")

CHANNEL_ID = os.getenv("CHANNEL_ID")
BLOG_ID = os.getenv("BLOG_ID")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

POST_INTERVAL_SECONDS = 10800  # كل 3 ساعات
POSTED_FILE = Path("posted_titles.json")

TOPICS = [
    "أفضل أدوات الذكاء الاصطناعي للمبتدئين",
    "كيف تستخدم الذكاء الاصطناعي لزيادة الإنتاجية",
    "طرق الربح من الإنترنت باستخدام أدوات AI",
    "كيف تكتب محتوى احترافي بمساعدة الذكاء الاصطناعي",
    "أهم مهارات المستقبل في عصر الذكاء الاصطناعي",
    "كيف تبدأ مشروع رقمي صغير باستخدام AI",
    "أفضل استخدامات الذكاء الاصطناعي في التعليم",
    "كيف تساعدك أدوات AI في التسويق الإلكتروني",
    "مستقبل العمل الحر مع الذكاء الاصطناعي",
    "أخطاء يجب تجنبها عند استخدام أدوات الذكاء الاصطناعي",
]


def get_access_token():
    """
    يجلب Access Token جديد من Google باستخدام Refresh Token.
    لا تحتاج BLOGGER_ACCESS_TOKEN بعد الآن.

    المطلوب في Render Environment:
    CLIENT_ID
    CLIENT_SECRET
    REFRESH_TOKEN
    """
    if not CLIENT_ID:
        raise ValueError("CLIENT_ID غير موجود في Render Environment")
    if not CLIENT_SECRET:
        raise ValueError("CLIENT_SECRET غير موجود في Render Environment")
    if not REFRESH_TOKEN:
        raise ValueError("REFRESH_TOKEN غير موجود في Render Environment")

    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    response = requests.post(url, data=data, timeout=15)

    if response.status_code != 200:
        raise RuntimeError(
            f"فشل جلب Google Access Token\n"
            f"Status: {response.status_code}\n"
            f"Response: {response.text[:900]}"
        )

    token_data = response.json()
    token = token_data.get("access_token")

    if not token:
        raise RuntimeError(f"لم يتم العثور على access_token في الرد: {token_data}")

    return token


def load_posted_titles():
    if POSTED_FILE.exists():
        try:
            return set(json.loads(POSTED_FILE.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_posted_titles(titles):
    POSTED_FILE.write_text(
        json.dumps(list(titles), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def make_article():
    posted = load_posted_titles()
    available = [t for t in TOPICS if t not in posted]

    if not available:
        posted = set()
        available = TOPICS[:]

    title = random.choice(available)

    intro = random.choice([
        "أصبح الذكاء الاصطناعي من أهم الأدوات التي تغيّر طريقة العمل والتعلم والربح من الإنترنت.",
        "أدوات الذكاء الاصطناعي أصبحت فرصة حقيقية لكل شخص يريد تطوير مهاراته وزيادة إنتاجيته.",
        "لم يعد الذكاء الاصطناعي تقنية بعيدة، بل أصبح وسيلة عملية تساعدك على إنجاز المهام بسرعة وجودة أعلى."
    ])

    content = f"""
<h2>{title}</h2>

<p>{intro}</p>

<h3>لماذا هذا الموضوع مهم؟</h3>
<p>
يساعدك فهم هذا المجال على استغلال الفرص الرقمية بشكل أفضل، سواء كنت تريد تطوير مهاراتك،
أو تحسين عملك، أو إنشاء مشروع رقمي يعتمد على أدوات حديثة وسهلة الاستخدام.
</p>

<h3>أهم الفوائد العملية</h3>
<ul>
<li>توفير الوقت في إنجاز المهام اليومية.</li>
<li>تحسين جودة المحتوى والأفكار.</li>
<li>زيادة الإنتاجية بدون الحاجة إلى خبرة تقنية كبيرة.</li>
<li>فتح فرص جديدة في العمل الحر والربح من الإنترنت.</li>
</ul>

<h3>كيف تبدأ؟</h3>
<p>
ابدأ بتجربة الأدوات المجانية، ثم تعلّم كتابة أوامر واضحة ومحددة. كلما كان طلبك دقيقًا،
كانت النتائج أفضل. جرّب أكثر من أسلوب، وقارن النتائج، ثم طوّر طريقتك تدريجيًا.
</p>

<h3>نصيحة مهمة</h3>
<p>
لا تعتمد على الذكاء الاصطناعي وحده بشكل كامل. استخدمه كمساعد ذكي، ثم راجع النتائج وعدّلها
بأسلوبك الخاص حتى تحصل على محتوى موثوق ومميز.
</p>

<p><strong>الخلاصة:</strong> الذكاء الاصطناعي فرصة قوية لمن يتعلم استخدامه بذكاء، وكلما بدأت مبكرًا زادت فرصك في النجاح الرقمي.</p>

<p>تم نشر هذا المقال تلقائيًا بواسطة بوت ZakaPro AI.</p>
"""

    posted.add(title)
    save_posted_titles(posted)
    return title, content


def publish_to_blogger(title, content):
    try:
        access_token = get_access_token()

        url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        data = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
        }

        response = requests.post(url, headers=headers, json=data, timeout=20)
        return response.status_code, response.text

    except Exception as e:
        logger.exception("Blogger request failed")
        return 500, str(e)


async def publish_article(context: ContextTypes.DEFAULT_TYPE, reply_func=None):
    if not BLOG_ID:
        if reply_func:
            await reply_func("❌ BLOG_ID غير موجود في Render Environment")
        return

    if not CLIENT_ID:
        if reply_func:
            await reply_func("❌ CLIENT_ID غير موجود في Render Environment")
        return

    if not CLIENT_SECRET:
        if reply_func:
            await reply_func("❌ CLIENT_SECRET غير موجود في Render Environment")
        return

    if not REFRESH_TOKEN:
        if reply_func:
            await reply_func("❌ REFRESH_TOKEN غير موجود في Render Environment")
        return

    title, content = make_article()
    status_code, result = publish_to_blogger(title, content)

    if status_code in (200, 201):
        try:
            result_json = json.loads(result)
            blogger_url = result_json.get("url", "")
        except Exception:
            blogger_url = ""

        if CHANNEL_ID:
            telegram_text = f"🚀 تم نشر مقال جديد في Blogger\n\n📝 {title}"
            if blogger_url:
                telegram_text += f"\n\n🔗 رابط المقال:\n{blogger_url}"

            try:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=telegram_text
                )
            except Exception as e:
                logger.exception("Telegram channel send failed")
                if reply_func:
                    await reply_func(
                        "✅ تم النشر في Blogger\n"
                        f"⚠️ لكن فشل الإرسال للقناة:\n{str(e)[:700]}"
                    )
                    return

        if reply_func:
            msg = "✅ تم النشر في Blogger والقناة"
            if blogger_url:
                msg += f"\n\n🔗 رابط المقال:\n{blogger_url}"
            await reply_func(msg)

        logger.info("Published successfully: %s", title)

    else:
        error_msg = f"❌ فشل النشر في Blogger\nStatus: {status_code}\n{result[:900]}"
        if reply_func:
            await reply_func(error_msg)
        logger.error(error_msg)


async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    await publish_article(context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ البوت شغال\n\n"
        "/status - فحص الحالة\n"
        "/generate - نشر مقال الآن\n"
        "/run - تشغيل يدوي\n\n"
        "⏱ النشر التلقائي: كل 3 ساعات\n"
        "🛡 منع التكرار: مفعل\n"
        "🔑 Blogger يعمل الآن بنظام Refresh Token"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    posted_count = len(load_posted_titles())

    await update.message.reply_text(
        "✅ حالة البوت:\n\n"
        f"📢 CHANNEL_ID: {CHANNEL_ID or 'غير موجود ❌'}\n"
        f"📝 BLOG_ID: {BLOG_ID or 'غير موجود ❌'}\n"
        f"🔑 Telegram Token: {'موجود ✅' if TELEGRAM_TOKEN else 'غير موجود ❌'}\n"
        f"🔑 CLIENT_ID: {'موجود ✅' if CLIENT_ID else 'غير موجود ❌'}\n"
        f"🔑 CLIENT_SECRET: {'موجود ✅' if CLIENT_SECRET else 'غير موجود ❌'}\n"
        f"🔑 REFRESH_TOKEN: {'موجود ✅' if REFRESH_TOKEN else 'غير موجود ❌'}\n"
        f"🗂 عدد العناوين المحفوظة: {posted_count}\n"
        "⏱ النشر التلقائي: كل 3 ساعات"
    )


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري توليد ونشر مقال...")
    await publish_article(context, reply_func=update.message.reply_text)


async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate(update, context)


def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN أو BOT_TOKEN غير موجود في Render Environment")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("run", run))

    if app.job_queue is None:
        raise RuntimeError(
            "JobQueue غير مثبت. عدّل requirements.txt واستخدم:\n"
            "python-telegram-bot[job-queue]==20.7"
        )

    app.job_queue.run_repeating(
        auto_post,
        interval=POST_INTERVAL_SECONDS,
        first=60
    )

    logger.info("✅ ZakaPro AI Bot is running...")
    logger.info("⏱ Auto post every 3 hours enabled")
    logger.info("🔑 Blogger Auth uses Refresh Token")

    app.run_polling()


if __name__ == "__main__":
    main()
