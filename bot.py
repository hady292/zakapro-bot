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

# يدعم الاسمين: TELEGRAM_TOKEN أو BOT_TOKEN
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")

CHANNEL_ID = os.getenv("CHANNEL_ID")
BLOG_ID = os.getenv("BLOG_ID")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

POST_INTERVAL_SECONDS = 10800  # كل 3 ساعات
POSTED_FILE = Path("posted_titles.json")


TOPICS = [
    "أفضل أدوات الذكاء الاصطناعي المجانية للمبتدئين في 2026",
    "كيف تستخدم الذكاء الاصطناعي لزيادة الإنتاجية والعمل أسرع",
    "طرق الربح من الإنترنت باستخدام أدوات الذكاء الاصطناعي",
    "كيف تكتب محتوى احترافي بمساعدة الذكاء الاصطناعي خطوة بخطوة",
    "أفضل أدوات AI للطلاب وصناع المحتوى والمسوقين",
    "كيف تبدأ مشروع رقمي صغير باستخدام الذكاء الاصطناعي",
    "أفضل استخدامات الذكاء الاصطناعي في التعليم والعمل",
    "كيف تساعدك أدوات AI في التسويق الإلكتروني وزيادة المبيعات",
    "مستقبل العمل الحر مع الذكاء الاصطناعي وأهم المهارات المطلوبة",
    "أخطاء يجب تجنبها عند استخدام أدوات الذكاء الاصطناعي",
    "أفضل مواقع الذكاء الاصطناعي لصناعة الصور والفيديو",
    "كيف تستخدم ChatGPT لإنشاء خطة محتوى كاملة",
    "أفضل أدوات الذكاء الاصطناعي لأصحاب المشاريع الصغيرة",
    "كيف تبني مصدر دخل رقمي باستخدام أدوات AI",
    "دليل المبتدئين لاستخدام الذكاء الاصطناعي في العمل اليومي",
]


def get_access_token():
    """
    يجلب Google Access Token جديد باستخدام Refresh Token.
    لا نحتاج BLOGGER_ACCESS_TOKEN بعد الآن.
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
        "grant_type": "refresh_token",
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
        encoding="utf-8",
    )


def make_article():
    posted = load_posted_titles()
    available = [t for t in TOPICS if t not in posted]

    if not available:
        posted = set()
        available = TOPICS[:]

    title = random.choice(available)

    intro = random.choice([
        "أصبح الذكاء الاصطناعي من أهم الأدوات التي تغيّر طريقة العمل والتعلم والربح من الإنترنت، ولم يعد استخدامه مقتصرًا على الخبراء فقط.",
        "في السنوات الأخيرة أصبحت أدوات الذكاء الاصطناعي فرصة حقيقية لكل شخص يريد تطوير مهاراته وزيادة إنتاجيته وبناء مشروع رقمي ناجح.",
        "لم يعد الذكاء الاصطناعي تقنية بعيدة أو معقدة، بل أصبح وسيلة عملية تساعد الأفراد والشركات على إنجاز المهام بسرعة وجودة أعلى."
    ])

    content = f"""
<h2>{title}</h2>

<p>{intro}</p>

<h3>مقدمة</h3>
<p>
يشهد العالم اليوم تحولًا كبيرًا بسبب انتشار أدوات الذكاء الاصطناعي في مجالات متعددة مثل التعليم،
التسويق، صناعة المحتوى، البرمجة، التصميم، إدارة الأعمال، والعمل الحر. هذا التحول فتح فرصًا جديدة
للمبتدئين والمحترفين على حد سواء، خصوصًا لمن يتعلم استخدام هذه الأدوات بطريقة صحيحة ومنظمة.
</p>

<p>
في هذا المقال سنشرح الفكرة بطريقة عملية، ونوضح لماذا هذا الموضوع مهم، وكيف يمكن الاستفادة منه
في الحياة اليومية أو في العمل أو في بناء مشروع رقمي صغير قابل للنمو.
</p>

<h3>لماذا هذا الموضوع مهم؟</h3>
<p>
أهمية الذكاء الاصطناعي لا تأتي فقط من كونه تقنية حديثة، بل من قدرته على تقليل الوقت والجهد وتحسين
جودة النتائج. فبدلًا من قضاء ساعات في البحث أو الكتابة أو التخطيط، يمكن استخدام أدوات AI للحصول
على أفكار أولية، مسودات محتوى، خطط تسويق، اقتراحات مشاريع، وتحليلات تساعدك على اتخاذ قرارات أفضل.
</p>

<h3>أهم الفوائد العملية</h3>
<ul>
<li>توفير الوقت في تنفيذ المهام اليومية والمتكررة.</li>
<li>تحسين جودة الكتابة والتسويق وصناعة المحتوى.</li>
<li>مساعدة المبتدئين على التعلم بشكل أسرع.</li>
<li>توليد أفكار جديدة للمشاريع والمقالات والمنشورات.</li>
<li>رفع الإنتاجية بدون الحاجة إلى فريق كبير.</li>
<li>فتح فرص جديدة في العمل الحر والربح من الإنترنت.</li>
</ul>

<h3>كيف تبدأ بطريقة صحيحة؟</h3>
<p>
ابدأ باختيار هدف واضح. هل تريد استخدام الذكاء الاصطناعي لكتابة مقالات؟ أم لتصميم صور؟ أم لإدارة
مشروع صغير؟ عندما تحدد الهدف، يصبح اختيار الأداة المناسبة أسهل بكثير.
</p>

<p>
بعد ذلك جرّب الأدوات المجانية أولًا، وتعلم كيف تكتب أوامر واضحة. كلما كان طلبك محددًا، كانت النتيجة
أفضل. لا تكتب طلبًا عامًا مثل: "اكتب مقالًا"، بل اكتب طلبًا واضحًا مثل: "اكتب مقالًا عربيًا منظمًا
عن أفضل أدوات الذكاء الاصطناعي للمبتدئين مع مقدمة وعناوين فرعية ونصائح عملية".
</p>

<h3>أمثلة عملية على الاستخدام</h3>
<ul>
<li>استخدام ChatGPT لتوليد أفكار مقالات أو منشورات سوشيال ميديا.</li>
<li>استخدام أدوات التصميم بالذكاء الاصطناعي لإنشاء صور مصغرة أو شعارات بسيطة.</li>
<li>استخدام أدوات التلخيص لفهم مقالات طويلة بسرعة.</li>
<li>استخدام أدوات الترجمة لتحسين المحتوى العربي والإنجليزي.</li>
<li>استخدام أدوات الجدولة لإدارة النشر على المدونة أو القنوات الاجتماعية.</li>
</ul>

<h3>نصائح مهمة للحصول على نتائج أفضل</h3>
<ol>
<li>اكتب طلبات واضحة ومفصلة.</li>
<li>راجع النتائج دائمًا قبل نشرها.</li>
<li>أضف خبرتك ولمستك الشخصية إلى أي محتوى يتم توليده.</li>
<li>لا تنشر محتوى مكررًا أو قصيرًا جدًا.</li>
<li>احرص على أن يكون المقال مفيدًا للقارئ وليس مجرد نص عام.</li>
</ol>

<h3>أخطاء يجب تجنبها</h3>
<p>
من أكبر الأخطاء الاعتماد الكامل على الذكاء الاصطناعي بدون مراجعة. أحيانًا قد تكون المعلومات عامة أو
غير دقيقة أو تحتاج إلى تعديل. كذلك من الأخطاء نشر عدد كبير من المقالات المتشابهة، لأن ذلك قد يضعف
جودة المدونة ويؤثر على فرص القبول في الإعلانات أو الظهور في نتائج البحث.
</p>

<h3>كيف تستفيد ماديًا من هذا المجال؟</h3>
<p>
يمكن الاستفادة من الذكاء الاصطناعي بطرق متعددة، مثل إنشاء مدونة متخصصة، تقديم خدمات كتابة محتوى،
إدارة صفحات تواصل اجتماعي، تصميم صور بسيطة، إعداد خطط تسويق، أو بناء تطبيقات رقمية بسيطة. لكن
الربح يحتاج صبرًا وجودة واستمرارية، وليس مجرد نشر عشوائي.
</p>

<h3>الخلاصة</h3>
<p>
الذكاء الاصطناعي فرصة قوية لمن يتعلم استخدامه بذكاء. البداية الصحيحة تكون بفهم الأدوات، اختيار هدف
واضح، إنتاج محتوى مفيد، وتطوير العمل تدريجيًا. كلما ركزت على الجودة وتقديم قيمة حقيقية للزائر،
زادت فرص نجاحك في بناء حضور رقمي وربح مستقبلي.
</p>

<p><strong>نصيحة أخيرة:</strong> استخدم الذكاء الاصطناعي كمساعد، وليس كبديل كامل عن تفكيرك وخبرتك.</p>
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

        response = requests.post(url, headers=headers, json=data, timeout=25)
        return response.status_code, response.text

    except Exception as e:
        logger.exception("Blogger request failed")
        return 500, str(e)


def publish_to_facebook(title, blogger_url=""):
    """
    ينشر رابط المقال على صفحة فيسبوك.
    يحتاج:
    FB_PAGE_ID
    FB_PAGE_ACCESS_TOKEN
    وصلاحية pages_manage_posts
    """
    if not FB_PAGE_ID or not FB_PAGE_ACCESS_TOKEN:
        return False, "FB_PAGE_ID أو FB_PAGE_ACCESS_TOKEN غير موجود في Render"

    message = f"🚀 مقال جديد على ZakaPro AI\n\n📝 {title}\n\n"
    if blogger_url:
        message += f"🔗 اقرأ المقال كاملًا:\n{blogger_url}\n\n"
    message += "تابعنا للمزيد من أدوات الذكاء الاصطناعي والتسويق الرقمي."

    url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/feed"

    try:
        response = requests.post(
            url,
            data={
                "message": message,
                "access_token": FB_PAGE_ACCESS_TOKEN,
            },
            timeout=25,
        )

        if response.status_code in (200, 201):
            return True, response.text

        return False, response.text

    except Exception as e:
        logger.exception("Facebook publish failed")
        return False, str(e)


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

        messages = []
        messages.append("✅ تم النشر في Blogger")

        if blogger_url:
            messages.append(f"🔗 رابط المقال:\n{blogger_url}")

        # نشر على Facebook
        fb_ok, fb_result = publish_to_facebook(title, blogger_url)
        if fb_ok:
            messages.append("✅ تم النشر على Facebook Page")
            logger.info("Facebook published: %s", fb_result)
        else:
            messages.append(f"⚠️ لم يتم النشر على Facebook:\n{str(fb_result)[:700]}")
            logger.error("Facebook publish error: %s", fb_result)

        # إرسال إلى Telegram Channel
        if CHANNEL_ID:
            telegram_text = f"🚀 تم نشر مقال جديد\n\n📝 {title}"
            if blogger_url:
                telegram_text += f"\n\n🔗 {blogger_url}"

            try:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=telegram_text,
                )
                messages.append("✅ تم الإرسال إلى قناة Telegram")
            except Exception as e:
                logger.exception("Telegram channel send failed")
                messages.append(f"⚠️ فشل الإرسال إلى قناة Telegram:\n{str(e)[:700]}")

        if reply_func:
            await reply_func("\n\n".join(messages))

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
        "🔑 Blogger يعمل بنظام Refresh Token\n"
        "📘 Facebook Page مضاف إذا كانت المتغيرات صحيحة\n"
        "📝 جودة المقال: طويلة ومطورة"
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
        f"📘 FB_PAGE_ID: {'موجود ✅' if FB_PAGE_ID else 'غير موجود ❌'}\n"
        f"📘 FB_PAGE_ACCESS_TOKEN: {'موجود ✅' if FB_PAGE_ACCESS_TOKEN else 'غير موجود ❌'}\n"
        f"🗂 عدد العناوين المحفوظة: {posted_count}\n"
        "⏱ النشر التلقائي: كل 3 ساعات\n"
        "📝 قالب المقال: طويل ومطور ✅"
    )


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري توليد ونشر مقال طويل وعالي الجودة...")
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
        first=60,
    )

    logger.info("✅ ZakaPro AI Bot is running...")
    logger.info("⏱ Auto post every 3 hours enabled")
    logger.info("🔑 Blogger Auth uses Refresh Token")
    logger.info("📘 Facebook Page publishing enabled if token is valid")

    app.run_polling()


if __name__ == "__main__":
    main()
