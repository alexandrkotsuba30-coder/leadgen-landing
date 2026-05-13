from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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
OUTPUT = ROOT / "leadcore-50-reklamnyh-svyazok-2026.pdf"
FONT_DIR = Path("C:/Windows/Fonts")
REGULAR_FONT = FONT_DIR / "arial.ttf"
BOLD_FONT = FONT_DIR / "arialbd.ttf"


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
            textColor=colors.HexColor("#5f6d70"),
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
            leading=30,
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
            name="OfferTitle",
            parent=styles["Heading3"],
            fontName="LeadCoreSansBold",
            fontSize=12.5,
            leading=15,
            textColor=colors.HexColor("#0F1818"),
            spaceAfter=4,
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


OFFER_SETS = [
    (
        "Кухни и мебель под заказ",
        [
            "Кухня под новую квартиру в Минске: проект и расчет за 24 часа.",
            "Шкаф или гардеробная без лишних замеров: первый просчет до звонка.",
            "Мебель под ключ для новостройки: дизайн, производство, установка.",
            "Решение для квартиры после покупки: кухня плюс хранение в одном заказе.",
            "Фиксируем сроки и этапы в договоре, чтобы клиент не боялся затяжки.",
        ],
    ),
    (
        "Ремонт квартир",
        [
            "Смета по ремонту за 1 день без обязательства на сделку.",
            "Ремонт новой квартиры под ключ с понятным календарем этапов.",
            "Быстрый старт без хаоса: прораб, смета, материалы, контроль.",
            "Ремонт под бюджет семьи: где экономить можно, а где нельзя.",
            "Первый выезд и план работ до подписания договора.",
        ],
    ),
    (
        "Натяжные потолки",
        [
            "Потолок в новую квартиру за 1 день установки.",
            "Расчет стоимости потолка по плану квартиры до выезда замерщика.",
            "Чистый монтаж без пыли и долгого простоя объекта.",
            "Потолки по комнатам: можно запускать поэтапно, а не сразу весь объект.",
            "Подсветка, треки и решения под современный интерьер в одном предложении.",
        ],
    ),
    (
        "Двери и перегородки",
        [
            "Подбор дверей под интерьер квартиры после покупки.",
            "Монтаж с гарантией геометрии и доборов без переделок.",
            "Двери и перегородки под ключ с замером и доставкой.",
            "Сравнение вариантов по бюджету: эконом, стандарт, премиум.",
            "Установка по графику ремонта, без конфликта с другими подрядчиками.",
        ],
    ),
    (
        "Клининг и уборка после ремонта",
        [
            "Генеральная уборка после ремонта с фиксированным списком работ.",
            "Подготовим квартиру к въезду за 1 день.",
            "Уборка новой квартиры перед заселением: окна, пыль, санузлы, кухня.",
            "Выезд в удобное окно после строителей или мебельщиков.",
            "Понятная цена за квадрат без мутных доплат на месте.",
        ],
    ),
    (
        "Окна, балконы, жалюзи",
        [
            "Обновление балкона или окон после покупки квартиры.",
            "Жалюзи и шторы под замер с монтажом в один визит.",
            "Сравним решения по теплу, свету и бюджету до замера.",
            "Балкон как полезная зона: хранение, отделка, утепление.",
            "Покажем варианты прямо под планировку клиента.",
        ],
    ),
    (
        "Юридические услуги для бизнеса",
        [
            "Разбор договора и рисков для собственника за 1 встречу.",
            "Регистрация, договоры, претензии без содержания штатного юриста.",
            "Абонентское сопровождение с фиксированным объемом задач.",
            "Проверка контрагентов и документов до сделки.",
            "Понятный юридический пакет под запуск нового направления.",
        ],
    ),
    (
        "B2B-сервисы и автоматизация",
        [
            "Настроим прием заявок и базовую автоматизацию без долгой разработки.",
            "Покажем, где у бизнеса теряются лиды, и закроем узкое место.",
            "CRM, таблицы, Telegram и отчетность в одном рабочем контуре.",
            "Первый этап без SaaS-марафона: быстрый запуск и измеримый эффект.",
            "Автоматизация под конкретную задачу, а не ради красивой схемы.",
        ],
    ),
    (
        "Медицина и эстетика",
        [
            "Первичная консультация или диагностика по понятному сценарию записи.",
            "Сильный оффер не на скидку, а на уверенность и квалификацию.",
            "Запись на процедуру или прием без лишних полей и потери обращения.",
            "Кампании под локальный район или отдельную услугу.",
            "Повторные касания по теплой базе через аккуратный ретаргет.",
        ],
    ),
    (
        "Обучение и экспертные услуги",
        [
            "Разбор запроса клиента до продажи основного продукта.",
            "Мини-продукт или аудит как первый понятный вход.",
            "Оффер на результат, а не на количество уроков или часов.",
            "Воронка под консультацию, мастер-класс или стратегическую сессию.",
            "Дожим через кейсы, скрипт и календарь следующего шага.",
        ],
    ),
]


AD_ANGLES = [
    "Новый объект или новая квартира: продаем решение под свежую потребность.",
    "Экономия времени: клиенту важно получить расчет, замер или созвон быстро.",
    "Снижение риска: гарантия, договор, этапность, фиксированные сроки.",
    "Видимый результат: до/после, визуализация, кейсы, примеры объектов.",
    "Ограничение выбора: один понятный пакет вместо десяти тарифов.",
    "Прозрачная экономика: ориентир по цене, диапазону бюджета, этапам оплаты.",
    "Быстрый вход: бесплатный расчет, аудит, выезд, демонстрация, бриф.",
    "Локальный контекст: Минск, новостройки, конкретные районы или категории домов.",
    "Спокойствие после сделки: сервис, сопровождение, контроль и поддержка.",
    "Комплексность: несколько задач клиента закрываются в одном подрядчике.",
]


BUDGET_ROWS = [
    ["Кухни / мебель", "$250-600", "$8-25", "Калькулятор, квиз, визуальные кейсы"],
    ["Ремонт квартир", "$300-700", "$10-35", "Смета, этапы, примеры объектов"],
    ["Потолки / двери", "$180-450", "$5-18", "Быстрый расчет и замер"],
    ["Клининг", "$120-250", "$3-10", "Простое УТП и скорость отклика"],
    ["Юруслуги", "$250-500", "$7-30", "Узкий оффер под одну боль"],
    ["B2B-автоматизация", "$300-800", "$12-45", "Аудит / разбор как первый шаг"],
]


LANDING_CHECKLIST = [
    "Первый экран отвечает на три вопроса: что продаете, для кого и зачем оставить заявку.",
    "Один сильный оффер на странице. Не мешайте несколько несвязанных услуг.",
    "Кнопка и форма видны без долгого скролла, поля сведены к минимуму.",
    "Есть доверие: кейсы, цифры, фото, гарантии, понятный процесс.",
    "Есть ответ на страхи: цена, сроки, кто делает, что входит, как контролируется.",
    "Есть отдельный блок под мобильный трафик: короткие тексты и крупные кнопки.",
]


CALL_SCRIPT = [
    "Спасибо за заявку. Уточните, правильно ли понимаю задачу клиента.",
    "За 2-3 вопроса определите, есть ли у клиента объект, срок и бюджет.",
    "Не продавайте весь продукт сразу. Продайте следующий шаг: выезд, расчет, созвон, бриф.",
    "Зафиксируйте срок обратной связи: когда отправите расчет или предложение.",
    "Если клиент не готов, договоритесь о мягком повторном касании, а не давите.",
]


KPI_ROWS = [
    ["CTR", "От 1.2%", "Если ниже, меняем креатив или оффер."],
    ["CPC", "В рамках ниши", "Сравнивайте объявления между собой, а не абстрактно."],
    ["Цена лида", "Входит в план", "Главный KPI первого теста."],
    ["Конверсия лендинга", "От 4-8%", "Если низко, проблема обычно в оффере или первом экране."],
    ["Дозвон / ответ", "От 70%", "Слабая обработка убивает даже хорошие лиды."],
    ["Квалификация лида", "От 40%", "Фиксируйте, кто реально подходит под продукт."],
]


def bullet_list(items, styles, color="#233033"):
    return ListFlowable(
        [
            ListItem(
                Paragraph(f"<font color='{color}'>{item}</font>", styles["Body"]),
                leftIndent=0,
            )
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
    story.append(Paragraph("LeadCore · Лид-магнит для предпринимателей", styles["CoverKicker"]))
    story.append(
        Paragraph(
            "50 рекламных связок для бизнеса в Беларуси на 2026",
            styles["CoverTitle"],
        )
    )
    story.append(
        Paragraph(
            "Офферы, креативные углы, тест-бюджеты, чеклист лендинга и таблица KPI на первые 14 дней запуска.",
            styles["CoverLead"],
        )
    )

    cover_table = Table(
        [
            ["Что внутри", "Зачем это нужно"],
            ["50 офферов по нишам", "Быстро собрать объявления и офферы без пустых формулировок"],
            ["10 рекламных углов", "Запускать разные заходы, а не крутить одну и ту же мысль"],
            ["Бюджет и CPL", "Не лететь в тест вслепую"],
            ["Чеклист страницы и KPI", "Понимать, где режется конверсия и что чинить"],
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
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
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
            "Материал рассчитан на быстрый запуск. Не пытайтесь внедрить все сразу: выберите одну нишу, один оффер, один канал и один следующий шаг для клиента.",
            styles["Body"],
        )
    )

    story.append(PageBreak())
    story.append(section_title("Как использовать этот PDF, чтобы он дал деньги", styles))
    story.append(
        bullet_list(
            [
                "Выберите 1 нишу и 1 основной оффер. Не пытайтесь тестировать сразу все сегменты.",
                "Соберите простой лендинг или квиз с одной ясной выгодой и короткой формой.",
                "Под каждый оффер запустите 2-3 рекламных угла, а не 10 разных мыслей вперемешку.",
                "Сразу считайте не только лиды, но и дозвон, квалификацию и цену целевого обращения.",
                "Через 7-14 дней оставьте только те связки, где клиент понятен и экономика сходится.",
            ],
            styles,
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(section_title("12 ниш, где такие связки особенно заходят", styles))
    story.append(
        Paragraph(
            "Кухни, мебель под заказ, ремонт квартир, потолки, двери, клининг, окна и балконы, юридические услуги, B2B-автоматизация, медицина и эстетика, обучение, локальные сервисы под новую недвижимость.",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            "Если у вас широкая аудитория, сначала сузьте оффер под одну конкретную боль. Например, не «ремонт квартир», а «смета ремонта новой квартиры за 1 день».",
            styles["Body"],
        )
    )

    for index, (segment, offers) in enumerate(OFFER_SETS, start=1):
        if index in {1, 4, 7, 9}:
            story.append(PageBreak())
            story.append(section_title("50 готовых офферов и формулировок", styles))
            story.append(
                Paragraph(
                    "Используйте эти варианты как сырье. Не копируйте слово в слово: адаптируйте под вашу цену, географию, сроки и конкретную выгоду.",
                    styles["Body"],
                )
            )
        story.append(Spacer(1, 3 * mm))
        story.append(card_title(f"{index}. {segment}", styles))
        story.append(bullet_list(offers, styles))

    story.append(PageBreak())
    story.append(section_title("10 рекламных углов, которые дают сильнее оффера", styles))
    story.append(bullet_list(AD_ANGLES, styles))
    story.append(
        Paragraph(
            "Один и тот же продукт можно продавать через скорость, безопасность, экономику, эстетику, удобство или комплексность. Именно угол часто решает, зайдет ли креатив.",
            styles["Body"],
        )
    )

    story.append(PageBreak())
    story.append(section_title("Ориентиры по тест-бюджету и CPL", styles))
    budget_table = Table(
        [["Ниша", "Тест-бюджет", "Нормальный CPL", "Что важно"]] + BUDGET_ROWS,
        colWidths=[43 * mm, 31 * mm, 29 * mm, 72 * mm],
        repeatRows=1,
    )
    budget_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12191B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "LeadCoreSansBold"),
                ("FONTNAME", (0, 1), (-1, -1), "LeadCoreSans"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F5FAEB")]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D6E1D3")),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(budget_table)
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            "Важно: нормальный CPL определяется не рынком вообще, а вашей маржой, скоростью сделки и качеством обработки. Если лид дешевый, но нецелевой, это не победа.",
            styles["Body"],
        )
    )

    story.append(PageBreak())
    story.append(section_title("Чеклист лендинга, который не режет конверсию", styles))
    story.append(bullet_list(LANDING_CHECKLIST, styles))
    story.append(Spacer(1, 3 * mm))
    story.append(section_title("Скрипт первого контакта по заявке", styles))
    story.append(bullet_list(CALL_SCRIPT, styles))

    story.append(PageBreak())
    story.append(section_title("Таблица KPI на первые 14 дней", styles))
    kpi_table = Table(
        [["Показатель", "Ориентир", "Что делать, если плохо"]] + KPI_ROWS,
        colWidths=[35 * mm, 28 * mm, 112 * mm],
        repeatRows=1,
    )
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12191B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "LeadCoreSansBold"),
                ("FONTNAME", (0, 1), (-1, -1), "LeadCoreSans"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F5FAEB")]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D6E1D3")),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(kpi_table)
    story.append(Spacer(1, 5 * mm))
    story.append(section_title("Финальная мысль", styles))
    story.append(
        Paragraph(
            "Сильная реклама начинается не с кабинета, а с точного оффера и понятного следующего шага. Если хотите собрать такую связку под свою нишу, LeadCore может сделать это в формате лендинга, рекламы и системы заявок.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 6 * mm))
    cta_box = Table(
        [[Paragraph("LeadCore<br/>leadcore.by<br/>Telegram: @Alexandr_K1503", styles["CTA"])]],
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
            "Коротко по комплаенсу: аудитории, CRM-базы и телефоны используйте только при наличии законного основания и в рамках рекламных политик платформ.",
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
        title="50 рекламных связок для бизнеса в Беларуси на 2026",
        author="LeadCore",
    )
    story = build_story(styles)
    doc.build(story, onFirstPage=page_background, onLaterPages=page_background)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
