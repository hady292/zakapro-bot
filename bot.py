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

# يدعم الاسمين في Render:
# TELEGRAM_TOKEN أو BOT_TOKEN
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")

CHANNEL_ID = os.getenv("CHANNEL_ID")
BLOG_ID = os.getenv("BLOG_ID")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

# كل 3 ساعات
POST_INTERVAL_SECONDS = 10800

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
    "كيف تستفيد من الذكاء الاصطناعي في العمل الحر",
    "أفضل طرق استخدام الذكاء الاصطناعي لصناعة المحتوى",
    "كيف تبني مشروعًا رقميًا بمساعدة الذكاء الاصطناعي",
    "أدوات ذكاء اصطناعي تساعدك في التسويق والكتابة",
    "دليل المبتدئين لاستخدام الذكاء الاصطناعي بذكاء",
]


def get_access_token():
    """
    يجلب Access Token جديد من Google باستخدام Refresh Token.
    لا نستخدم BLOGGER_ACCESS_TOKEN نهائيًا.
    """
    if not CLIENT_ID:
        raise ValueError("CLIENT_ID غير موجود في Render Environment")
    if not CLIENT_SECRET:
        raise ValueError("CLIENT_SECRET غير موجود في Render Environment")
    if not REFRESH_TOKEN:
        raise ValueError("REFRESH_TOKEN غير موجود في Render Environment")

    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=15,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"فشل جلب Google Access Token\n"
            f"Status: {response.status_code}\n"
            f"Response: {response.text[:900]}"
        )

    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise RuntimeError(f"لم يتم العثور على access_token في الرد: {token_data}")

    return access_token


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

    intro_options = [
        "أصبح الذكاء الاصطناعي اليوم من أهم الأدوات التي تساعد الأفراد وأصحاب المشاريع وصنّاع المحتوى على إنجاز أعمالهم بسرعة وجودة أعلى.",
        "لم يعد الذكاء الاصطناعي مجرد تقنية معقدة يستخدمها المختصون فقط، بل أصبح أداة عملية يمكن لأي شخص الاستفادة منها في العمل والتعلم والربح من الإنترنت.",
        "في السنوات الأخيرة، أصبحت أدوات الذكاء الاصطناعي جزءًا أساسيًا من الحياة الرقمية، خصوصًا لمن يريد تطوير مهاراته أو بناء مشروع رقمي ناجح.",
        "أصبح استخدام أدوات الذكاء الاصطناعي مهارة مهمة لكل شخص يريد تحسين إنتاجيته وتطوير عمله الرقمي بطريقة أسرع وأكثر تنظيمًا.",
    ]

    intro = random.choice(intro_options)

    content = f"""
<h2>{title}</h2>

<p>{intro}</p>

<h3>مقدمة</h3>
<p>
يشهد العالم تطورًا سريعًا في استخدام أدوات الذكاء الاصطناعي، حيث أصبحت هذه الأدوات تساعد في الكتابة،
التصميم، التسويق، التعليم، إدارة الوقت، تحليل البيانات، وإنشاء المحتوى. ومع هذا الانتشار الكبير،
أصبح من المهم أن يعرف المستخدم العربي كيف يستفيد من هذه التقنية بطريقة صحيحة وعملية.
</p>

<p>
الكثير من الناس يستخدمون الذكاء الاصطناعي بشكل عشوائي، فيحصلون على نتائج ضعيفة أو مكررة.
لكن عندما تتعلم كيف تكتب طلبات واضحة، وكيف تراجع النتائج وتضيف عليها لمستك الخاصة،
ستلاحظ فرقًا كبيرًا في جودة المحتوى وسرعة الإنجاز.
</p>

<h3>لماذا هذا الموضوع مهم؟</h3>
<p>
أهمية هذا الموضوع تأتي من أن الذكاء الاصطناعي لم يعد خيارًا ثانويًا، بل أصبح مهارة أساسية لكل شخص يريد
مواكبة التطور الرقمي. سواء كنت طالبًا، موظفًا، صاحب مشروع، مدوّنًا، أو شخصًا يبحث عن طرق جديدة للربح
من الإنترنت، فإن فهم طريقة استخدام أدوات الذكاء الاصطناعي يمنحك أفضلية واضحة.
</p>

<p>
الذكاء الاصطناعي يساعدك على اختصار الوقت، تنظيم الأفكار، تحسين جودة النصوص، توليد أفكار جديدة،
وتحويل المهام المعقدة إلى خطوات بسيطة. لكن القيمة الحقيقية لا تكون في الأداة وحدها، بل في طريقة استخدامها.
</p>

<h3>أهم الفوائد العملية</h3>
<ul>
<li>توفير الوقت في كتابة المقالات، المنشورات، الخطط، والأفكار.</li>
<li>تحسين جودة المحتوى قبل نشره على المدونة أو مواقع التواصل.</li>
<li>مساعدة المبتدئين على فهم المواضيع المعقدة بطريقة سهلة.</li>
<li>توليد أفكار جديدة لمشاريع رقمية أو محتوى تسويقي.</li>
<li>تنظيم المهام اليومية وتحويل الأفكار إلى خطوات عملية.</li>
<li>تحسين الإنتاجية في العمل والدراسة والعمل الحر.</li>
<li>المساعدة في كتابة عناوين جذابة ووصف احترافي للمنتجات والخدمات.</li>
</ul>

<h3>كيف تبدأ بطريقة صحيحة؟</h3>
<p>
البداية الصحيحة لا تكون باستخدام عشرات الأدوات دفعة واحدة، بل بتحديد هدف واضح. اسأل نفسك:
هل تريد كتابة محتوى؟ هل تريد تحسين إنتاجيتك؟ هل تريد تعلم مهارة جديدة؟ هل تريد إنشاء مشروع رقمي؟
عندما تحدد هدفك، يصبح اختيار الأداة المناسبة أسهل بكثير.
</p>

<ol>
<li><strong>حدد الهدف:</strong> لا تبدأ بدون معرفة ما تريد الوصول إليه.</li>
<li><strong>اكتب طلبًا واضحًا:</strong> كلما كان طلبك محددًا، كانت النتيجة أفضل.</li>
<li><strong>راجع النتيجة:</strong> لا تنشر المحتوى كما هو بدون مراجعة.</li>
<li><strong>أضف أسلوبك:</strong> اجعل المقال يعبر عنك وليس مجرد نص آلي.</li>
<li><strong>حسّن التنسيق:</strong> استخدم عناوين فرعية، قوائم، وفقرات قصيرة.</li>
</ol>

<h3>مثال عملي على استخدام الذكاء الاصطناعي</h3>
<p>
بدل أن تكتب للذكاء الاصطناعي: "اكتب مقالًا عن الذكاء الاصطناعي"، الأفضل أن تكتب:
"اكتب مقالًا عربيًا منظمًا عن فوائد الذكاء الاصطناعي للمبتدئين، مع مقدمة، خطوات عملية، أمثلة، أخطاء شائعة، وخلاصة".
</p>

<p>
هذا النوع من الطلبات يعطي نتائج أفضل لأنه يوضح المطلوب بدقة. كذلك يمكنك طلب تحسين المقال بعد كتابته،
مثل: "اجعل المقال أكثر احترافية"، أو "أضف أمثلة عملية"، أو "حسّن العنوان ليكون مناسبًا لمحركات البحث".
</p>

<h3>أدوات يمكن الاستفادة منها</h3>
<p>
هناك العديد من أدوات الذكاء الاصطناعي التي يمكن استخدامها حسب الحاجة. بعض الأدوات تساعد في الكتابة،
وبعضها في التصميم، وبعضها في الترجمة، وبعضها في تنظيم الأفكار. المهم ألا تعتمد على أداة واحدة فقط،
بل جرّب أكثر من خيار واختر ما يناسبك.
</p>

<ul>
<li>أدوات كتابة المحتوى لتحسين المقالات والأفكار.</li>
<li>أدوات الترجمة لتسهيل التعامل مع المحتوى الأجنبي.</li>
<li>أدوات التصميم لإنشاء صور ومنشورات جذابة.</li>
<li>أدوات التلخيص لفهم النصوص الطويلة بسرعة.</li>
<li>أدوات التخطيط لتنظيم المشاريع والمهام.</li>
</ul>

<h3>أخطاء شائعة يجب تجنبها</h3>
<p>
رغم قوة الذكاء الاصطناعي، إلا أن استخدامه بطريقة خاطئة قد يؤدي إلى محتوى ضعيف أو مكرر.
لذلك يجب الانتباه إلى بعض الأخطاء الشائعة التي يقع فيها الكثير من المبتدئين.
</p>

<ul>
<li>نسخ المحتوى كما هو دون تعديل أو مراجعة.</li>
<li>نشر مقالات قصيرة جدًا لا تقدم قيمة حقيقية للقارئ.</li>
<li>استخدام نفس القالب في كل مقال بدون تنويع.</li>
<li>عدم التأكد من صحة المعلومات قبل النشر.</li>
<li>إهمال تحسين العنوان والوصف والكلمات المفتاحية.</li>
<li>الاعتماد الكامل على الذكاء الاصطناعي دون إضافة خبرة بشرية.</li>
</ul>

<h3>كيف تجعل المحتوى أفضل لمحركات البحث؟</h3>
<p>
لكي يكون المقال مناسبًا لمحركات البحث، يجب أن يكون واضحًا ومنظمًا ويجيب على أسئلة القارئ.
استخدم عنوانًا مباشرًا، مقدمة مفيدة، عناوين فرعية، فقرات قصيرة، وقوائم مرتبة. كما يفضل إضافة أمثلة
عملية وروابط داخلية لمقالات أخرى داخل المدونة عندما يكون ذلك مناسبًا.
</p>

<p>
لا تركز فقط على الكلمات المفتاحية، بل ركز على نية القارئ. اسأل نفسك: ما السؤال الذي يبحث عنه الزائر؟
وما الإجابة العملية التي يمكن أن أقدمها له؟ كلما كان المقال مفيدًا، زادت فرصة ظهوره في نتائج البحث.
</p>

<h3>نصيحة مهمة للمبتدئين</h3>
<p>
لا تتعامل مع الذكاء الاصطناعي كبديل كامل عنك، بل اعتبره مساعدًا ذكيًا. استخدمه لتسريع العمل،
توليد الأفكار، ترتيب المقال، وتحسين الصياغة، لكن القرار النهائي والمراجعة النهائية يجب أن تكون منك.
هذا يجعل المحتوى أكثر ثقة وجودة وقربًا من القارئ.
</p>

<h3>الخلاصة</h3>
<p>
الذكاء الاصطناعي فرصة كبيرة لكل من يريد التعلم، العمل، صناعة المحتوى، أو بناء مشروع رقمي.
لكن النجاح الحقيقي لا يعتمد على استخدام الأداة فقط، بل على طريقة التفكير، وضوح الهدف،
جودة الطلبات، والمراجعة النهائية للمحتوى.
</p>

<p>
ابدأ بخطوات بسيطة، جرّب الأدوات المتاحة، تعلم من النتائج، وحسّن أسلوبك مع الوقت.
ومع الاستمرار، ستتمكن من تحويل الذكاء الاصطناعي إلى أداة قوية تساعدك على النجاح في العالم الرقمي.
</p>
"""

    posted.add(title)
    save_posted_titles(posted)
    return title, content


def publish_to_blogger(title, content):
    try:
        if not BLOG_ID:
            raise ValueError("BLOG_ID غير موجود في Render Environment")

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
    missing = []

    if not BLOG_ID:
        missing.append("BLOG_ID")
    if not CLIENT_ID:
        missing.append("CLIENT_ID")
    if not CLIENT_SECRET:
        missing.append("CLIENT_SECRET")
    if not REFRESH_TOKEN:
        missing.append("REFRESH_TOKEN")

    if missing:
        if reply_func:
            await reply_func("❌ ناقص في Render Environment: " + ", ".join(missing))
        return

    title, content = make_article()
    status_code, result = publish_to_blogger(title, content)

    if status_code in (200, 201):
        try:
            result_json = json.loads(result)
            blogger_url = result_json.get("url", "")
        except Exception:
            blogger_url = ""

        channel_ok = True

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
                channel_ok = False
                logger.exception("Telegram channel send failed")
                if reply_func:
                    await reply_func(
                        "✅ تم النشر في Blogger\n"
                        f"⚠️ لكن فشل الإرسال للقناة:\n{str(e)[:700]}"
                    )

        if reply_func and channel_ok:
            msg = "✅ تم النشر في Blogger"
            if CHANNEL_ID:
                msg += " والقناة"
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
        "🔑 Blogger يعمل الآن بنظام Refresh Token\n"
        "📝 جودة المقال: مطوّرة وطويلة"
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
        "⏱ النشر التلقائي: كل 3 ساعات\n"
        "📝 قالب المقال: طويل ومطوّر ✅"
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
        first=60
    )

    logger.info("✅ ZakaPro AI Bot is running...")
    logger.info("⏱ Auto post every 3 hours enabled")
    logger.info("🔑 Blogger Auth uses Refresh Token")
    logger.info("📝 Long article template enabled")

    app.run_polling()


if __name__ == "__main__":
    main()
