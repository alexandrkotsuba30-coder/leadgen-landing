from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "leadcore-27-mest-gde-biznes-teryaet-dengi-i-zayavki.pdf"
FONT_DIR = Path("C:/Windows/Fonts")
REGULAR_FONT = FONT_DIR / "arial.ttf"
BOLD_FONT = FONT_DIR / "arialbd.ttf"


REASONS = [
    (
        "До рекламы и трафика",
        [
            "Непонятно, что именно вы продаете и в чем ваша выгода за 5 секунд.",
            "Один и тот же оффер показывается всем подряд, без разделения аудиторий.",
            "Нет простого первого шага: расчет, аудит, консультация, замер, встреча.",
            "В предложении нет цифр, сроков, рамки цены или понятного результата.",
            "Клиент не понимает, почему должен выбрать именно вас, а не похожих.",
            "Вы хотите продать сразу все, вместо одного понятного входа.",
        ],
    ),
    (
        "На сайте и посадочной странице",
        [
            "Первый экран не отвечает быстро: что, для кого и зачем оставить заявку.",
            "Слишком много текста, но мало смысла и визуальных доказательств.",
            "Форма слишком длинная или просит данные раньше, чем человек готов.",
            "Кнопка и призыв к действию слабые, общие или незаметные.",
            "Нет доверия: кейсов, цифр, отзывов, примеров, гарантий или процесса.",
            "Мобильная версия неудобная, а именно с телефона приходит много трафика.",
            "Страница грузится медленно или визуально выглядит как шаблон без доверия.",
        ],
    ),
    (
        "В рекламе и трафике",
        [
            "Вы запускаете рекламу без нескольких гипотез, а ставите все на один креатив.",
            "Нет сегментации: теплые, холодные и повторные касания смешаны.",
            "Оффер в рекламе не совпадает с тем, что человек видит после клика.",
            "Трафик ведется на общую страницу, а не на узкий оффер.",
            "Не настроена нормальная аналитика, и деньги тратятся почти вслепую.",
        ],
    ),
    (
        "В обработке заявок",
        [
            "Менеджер отвечает слишком поздно, когда интерес уже остыл.",
            "Нет понятного сценария первого контакта и квалификации лида.",
            "Лид не получает следующий шаг в разговоре: расчет, встречу, выезд, бриф.",
            "Нет повторных касаний по тем, кто не купил сразу, но интерес проявил.",
            "Заявки не фиксируются в одной системе и теряются между мессенджерами.",
            "Нет человека, который персонально отвечает за скорость и качество обработки.",
        ],
    ),
    (
        "В управлении и деньгах",
        [
            "Вы смотрите на количество лидов, но не считаете стоимость продажи.",
            "Нет понимания допустимой цены лида и запаса маржи.",
            "Не проводится еженедельный разбор: что сработало, что слило бюджет и что менять.",
        ],
    ),
]


QUICK_FIXES = [
    "Сформулируйте один сильный оффер и уберите все лишнее со страницы.",
    "Сократите форму до минимума и ускорьте первый ответ на заявку.",
    "Разведите трафик по сегментам и считайте не лиды, а деньги после лида.",
]


SELF_AUDIT = [
    ["Блок", "Что проверить у себя", "Если ответ “нет”"],
    ["Оффер", "За 5 секунд понятно, что вы продаете и зачем оставить заявку?", "Теряете внимание и доверие еще до контакта."],
    ["Страница", "Есть ли один ясный призыв и короткая форма?", "Платите за клики, но режете конверсию уже на сайте."],
    ["Доверие", "Есть ли кейсы, цифры, фото, процесс или гарантии?", "Клиент уходит сравнивать и сомневаться."],
    ["Реклама", "Есть ли минимум 2-3 гипотезы оффера и креатива?", "Один слабый креатив тянет вниз весь запуск."],
    ["Продажи", "Кто и как быстро отвечает на лид в первые 5-15 минут?", "Горячие лиды остывают раньше звонка."],
    ["Аналитика", "Считаете ли цену продажи, а не только цену лида?", "Можно радоваться дешевым лидам и при этом терять деньги."],
]


def register_fonts():
    pdfmetrics.registerFont(TTFont("LeadCoreSans", str(REGULAR_FONT)))
    pdfmetrics.registerFont(TTFont("LeadCoreSansBold", str(BOLD_FONT)))


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="LeadCoreSans",
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#233033"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName="LeadCoreSans",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#5F6D70"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverKicker",
            parent=styles["BodyText"],
            fontName="LeadCoreSansBold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#6E8F18"),
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Heading1"],
            fontName="LeadCoreSansBold",
            fontSize=27,
            leading=31,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#12191B"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverLead",
            parent=styles["BodyText"],
            fontName="LeadCoreSans",
            fontSize=12.5,
            leading=17,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334245"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="LeadCoreSansBold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#12191B"),
            spaceBefore=4,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CardTitle",
            parent=styles["Heading3"],
            fontName="LeadCoreSansBold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#12191B"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CTA",
            parent=styles["BodyText"],
            fontName="LeadCoreSansBold",
            fontSize=12,
            leading=16,
            textColor=colors.white,
            alignment=TA_CENTER,
        )
    )
    return styles


def bullet_list(items, styles):
    return ListFlowable(
        [
            ListItem(Paragraph(item, styles["Body"]), leftIndent=0)
            for item in items
        ],
        bulletType="bullet",
        bulletFontName="LeadCoreSansBold",
        bulletFontSize=10,
        bulletColor=colors.HexColor("#B8FF45"),
        leftIndent=14,
        spaceBefore=4,
        spaceAfter=8,
    )


def section_title(text, styles):
    return Paragraph(text, styles["SectionTitle"])


def card_title(text, styles):
    return Paragraph(text, styles["CardTitle"])


def page_background(canvas, doc):
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#F3F0E8"))
    canvas.rect(0, 0, width, height, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#E9F6CD"))
    canvas.circle(45 * mm, height - 38 * mm, 22 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#D9F5F0"))
    canvas.circle(width - 32 * mm, height - 24 * mm, 18 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#12191B"))
    canvas.rect(15 * mm, 12 * mm, width - 30 * mm, 0.6 * mm, stroke=0, fill=1)
    canvas.setFont("LeadCoreSans", 8.5)
    canvas.setFillColor(colors.HexColor("#5E6A6E"))
    canvas.drawString(18 * mm, 8 * mm, "LeadCore")
    canvas.drawRightString(width - 18 * mm, 8 * mm, f"Стр. {doc.page}")
    canvas.restoreState()


def build_story(styles):
    story = []
    story.append(Spacer(1, 22 * mm))
    story.append(Paragraph("LeadCore · Жесткий self-audit для владельцев бизнеса", styles["CoverKicker"]))
    story.append(
        Paragraph(
            "27 мест, где ваш бизнес теряет деньги и заявки каждый день",
            styles["CoverTitle"],
        )
    )
    story.append(
        Paragraph(
            "Если у вас уже есть сайт, реклама, менеджер или входящие обращения, этот PDF поможет быстро увидеть, где прямо сейчас утекают клиенты, рекламный бюджет и выручка.",
            styles["CoverLead"],
        )
    )

    cover_table = Table(
        [
            ["Что вы получаете", "Как это использовать"],
            ["Карту 27 точек потери", "Сразу увидите, в каком месте ломается путь клиента и продажи"],
            ["Самопроверку по 6 ключевым блокам", "Быстро отметите слабые места внутри бизнеса без долгого аудита"],
            ["Быструю оценку масштаба потерь", "Поймете, сколько денег может утекать каждый месяц"],
            ["3 приоритета на исправление", "Поймете, за что браться первым, чтобы вернуть деньги в систему"],
        ],
        colWidths=[67 * mm, 105 * mm],
    )
    cover_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12191B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "LeadCoreSansBold"),
                ("FONTNAME", (0, 1), (-1, -1), "LeadCoreSans"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LEADING", (0, 0), (-1, -1), 13),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F4FAE8")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5E2CC")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(cover_table)
    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph(
            "Это не обучение маркетингу. Это быстрый, неприятно честный срез по вашему бизнесу: где вы теряете интерес клиента, заявку, деньги и момент продажи.",
            styles["Body"],
        )
    )

    story.append(PageBreak())
    story.append(section_title("Как работать с этим PDF", styles))
    story.append(
        bullet_list(
            [
                "Пройдитесь по всем 27 пунктам и честно отметьте, где у вас есть совпадения.",
                "Если совпало 5 и больше пунктов, вы уже теряете деньги каждый месяц, даже если внешне все выглядит нормально.",
                "Если совпало 10 и больше пунктов, проблема не в количестве трафика, а в системе получения и обработки заявок.",
                "Исправляйте сначала самые дорогие утечки: оффер, страница, скорость ответа, аналитика.",
            ],
            styles,
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(section_title("Быстрый self-audit на 15 минут", styles))
    audit_table = Table(SELF_AUDIT, colWidths=[28 * mm, 74 * mm, 73 * mm], repeatRows=1)
    audit_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12191B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "LeadCoreSansBold"),
                ("FONTNAME", (0, 1), (-1, -1), "LeadCoreSans"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F5FAEB")]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D6E1D3")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(audit_table)
    story.append(Spacer(1, 4 * mm))
    story.append(section_title("Как быстро прикинуть масштаб потерь", styles))
    story.append(
        bullet_list(
            [
                "Возьмите месячный рекламный бюджет или количество входящих обращений.",
                "Прикиньте, сколько процентов заявок теряется из-за слабой страницы, плохого оффера или медленной обработки.",
                "Умножьте это на среднюю прибыль с одной продажи. Именно так вы увидите не абстрактную маркетинговую ошибку, а прямую потерю денег.",
            ],
            styles,
        )
    )

    first_page = True
    running_total = 0
    for section_name, items in REASONS:
        story.append(PageBreak())
        title_text = "27 причин потери заявок и денег" if first_page else "Продолжение диагностики"
        story.append(section_title(title_text, styles))
        story.append(
            Paragraph(
                "Ниже не теория, а типовые утечки, из-за которых даже хороший продукт, сайт или реклама не дают нормальный результат и не превращаются в деньги.",
                styles["Body"],
            )
        )
        story.append(Spacer(1, 2 * mm))
        story.append(card_title(section_name, styles))
        numbered_items = []
        for item in items:
            running_total += 1
            numbered_items.append(f"<b>{running_total}.</b> {item}")
        story.append(bullet_list(numbered_items, styles))
        first_page = False

    story.append(PageBreak())
    story.append(section_title("Что исправлять в первую очередь", styles))
    story.append(
        Paragraph(
            "Почти всегда самые дорогие потери сидят не в одном объявлении, а в связке: слабый оффер, неубедительная страница, медленный ответ, отсутствие цифр по воронке.",
            styles["Body"],
        )
    )
    story.append(bullet_list(QUICK_FIXES, styles))
    story.append(
        Paragraph(
            "Если не знаете, что именно исправлять первым, начните с одного вопроса: где бизнес теряет деньги раньше всего - до заявки, в момент заявки или после заявки.",
            styles["Body"],
        )
    )

    story.append(PageBreak())
    story.append(section_title("Когда уже пора разбирать систему глубже", styles))
    story.append(
        bullet_list(
            [
                "Реклама идет, а заявок мало или они слишком дорогие.",
                "Заявки есть, но менеджеры плохо доводят их до продажи.",
                "Сайт посещают, но люди не оставляют контакты.",
                "Собственник не понимает, где конкретно теряется выручка.",
                "Подрядчики и менеджеры говорят разное, а цифры не сходятся.",
            ],
            styles,
        )
    )
    story.append(Spacer(1, 5 * mm))
    cta_box = Table(
        [[Paragraph("LeadCore<br/>Разбор связки: оффер, страница, трафик, обработка заявок<br/>leadcore.by · Telegram: @Alexandr_K1503", styles["CTA"])]],
        colWidths=[170 * mm],
    )
    cta_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#12191B")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#12191B")),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(cta_box)
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "Коротко по комплаенсу: телефоны, CRM-базы и рекламные аудитории используйте только при наличии законного основания и в рамках правил платформ.",
            styles["Small"],
        )
    )
    return story


def build_pdf():
    register_fonts()
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="27 мест, где ваш бизнес теряет деньги и заявки каждый день",
        author="LeadCore",
    )
    story = build_story(styles)
    doc.build(story, onFirstPage=page_background, onLaterPages=page_background)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
