# -*- coding: utf-8 -*-
import sqlite3
import datetime
import os
import sys

sys.path.insert(0, r"d:\Qoder\ai-otdel-prodazh-ru\scripts")
import drafts

db_path = r"d:\Qoder\ai-otdel-prodazh-ru\data\leads.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

batch_10 = [
    {
        "inn": "5007047254",
        "name": "ООО «НЕСТ ТЕХНО»",
        "greeting": "Сергей Сурикович",
        "email": "nest-tehno@mail.ru",
        "revenue": "1,96 млрд ₽",
        "site": "dmdveri.ru",
        "phone": "+7 (985) 504-05-05",
        "director": "ГЕНЕРАЛЬНЫЙ ДИРЕКТОР: Сафарян Сергей Сурикович"
    },
    {
        "inn": "1657191681",
        "name": "ООО «РАМ-СТРОЙ»",
        "greeting": "Рамиль Ильдарович",
        "email": "stroitel.kzn@mail.ru",
        "revenue": "1,88 млрд ₽",
        "site": None,
        "phone": "+7 927 243-60-13",
        "director": "ГЕНЕРАЛЬНЫЙ ДИРЕКТОР: Галиуллин Рамиль Ильдарович"
    },
    {
        "inn": "5020050390",
        "name": "ООО «ЛИДЕР-СТРОЙ»",
        "greeting": "Алексей Валерьевич",
        "email": "lider-stroy@mail.ru",
        "revenue": "1,11 млрд ₽",
        "site": None,
        "phone": "+7 (495) 960-62-50",
        "director": "ГЕНЕРАЛЬНЫЙ ДИРЕКТОР: Левченко Алексей Валерьевич"
    },
    {
        "inn": "5012091361",
        "name": "ООО «СК КОМПЛЕКС»",
        "greeting": "Арам Сергеевич",
        "email": "complex-usluga@mail.ru",
        "revenue": "1,00 млрд ₽",
        "site": None,
        "phone": "+7 (495) 204-36-04",
        "director": "ГЕНЕРАЛЬНЫЙ ДИРЕКТОР: Сааков Арам Сергеевич"
    },
    {
        "inn": "4501173026",
        "name": "ООО «УК-ВЕНТ»",
        "greeting": "Павел Владимирович",
        "email": "601651@gmail.com",
        "revenue": "928 млн ₽",
        "site": None,
        "phone": "+7 (919) 590-06-72",
        "director": "ДИРЕКТОР: Волков Павел Владимирович"
    },
    {
        "inn": "3257014995",
        "name": "ООО «РСУ №6»",
        "greeting": "Артур Григорьевич",
        "email": "pcy6@mail.ru",
        "revenue": "920 млн ₽",
        "site": None,
        "phone": "+7 (4832) 72-27-89",
        "director": "ГЕНЕРАЛЬНЫЙ ДИРЕКТОР: Перлин Артур Григорьевич"
    },
    {
        "inn": "5001119569",
        "name": "ООО «ГИС»",
        "greeting": "Станислав Александрович",
        "email": "info@gis-ooo.ru",
        "revenue": "491 млн ₽",
        "site": "gis-ooo.ru",
        "phone": "+7 (926) 903-46-56",
        "director": "ГЕНЕРАЛЬНЫЙ ДИРЕКТОР: Крамаров Станислав Александрович"
    },
    {
        "inn": "4345416769",
        "name": "ООО «СТРОЙГРУПП»",
        "greeting": "Роман Александрович",
        "email": "stroigrupp2015@mail.ru",
        "revenue": "387 млн ₽",
        "site": None,
        "phone": "+7 (938) 160-43-98",
        "director": "ДИРЕКТОР: Горобий Роман Александрович"
    },
    {
        "inn": "5011034152",
        "name": "ООО «АЛЬЯНС-ИНЖИНИРИНГ»",
        "greeting": "Жамшид Жумаевич",
        "email": "info@al-inj.ru",
        "revenue": "379 млн ₽",
        "site": "al-inj.ru",
        "phone": "+7 (495) 125-22-37",
        "director": "ГЕНЕРАЛЬНЫЙ ДИРЕКТОР: Неъматов Жамшид Жумаевич"
    },
    {
        "inn": "5001069967",
        "name": "ООО «ИСВЕНТ»",
        "greeting": "Игорь Алексеевич",
        "email": "zakaz@is-vent.ru",
        "revenue": "367 млн ₽",
        "site": "is-vent.ru",
        "phone": "+7 (498) 303-18-50",
        "director": "ГЕНЕРАЛЬНЫЙ ДИРЕКТОР: Серёгин Игорь Алексеевич"
    },
]

# 1. Update companies and enrichment
now_iso = datetime.datetime.utcnow().isoformat()

for item in batch_10:
    inn = item["inn"]
    email = item["email"]
    website = item.get("site")
    phone = item.get("phone")
    director = item["director"]
    
    cur.execute("""
        UPDATE companies 
        SET email = ?, website = coalesce(?, website), phone = coalesce(?, phone), director = coalesce(?, director)
        WHERE inn = ?
    """, (email, website, phone, director, inn))
    
    cur.execute("""
        INSERT OR REPLACE INTO enrichment (inn, name, website, email, director, revenue, source, confidence, checked_at, phone)
        VALUES (?, ?, ?, ?, ?, (SELECT revenue FROM companies WHERE inn = ?), 'official_verified_search', 'high', ?, ?)
    """, (inn, item["name"], website, email, director, inn, now_iso, phone))

conn.commit()
print("Updated companies and enrichment tables in leads.db.")

# 2. Prepare drafts
new_drafts = []

for lead in batch_10:
    inn = lead["inn"]
    short_cname = lead["name"]
    greeting = lead["greeting"]
    to_email = lead["email"]
    
    subject = f"Платформа «СтройИнтел» (реестр Минцифры № 35354) для {short_cname}"
    if len(subject) > 70:
        subject = f"Платформа «СтройИнтел» для {short_cname}"
    if len(subject) > 70:
        subject = "Платформа «СтройИнтел» (реестр Минцифры № 35354)"

    body = f"""Здравствуйте, {greeting}!

Обращаюсь к Вам как к руководителю {short_cname}.

Наша компания ООО «ИТ СтройИнтел» разработала российскую отраслевую ИИ-платформу «СтройИнтел» для генеральных подрядчиков и строительного контроля. 16 сентября 2026 года платформа официально включена в Единый реестр отечественного ПО Минцифры России (запись № 35354).

Платформа закрывает рутинные процессы ПТО, сметчиков и проектировщиков:
1. Исполнительная документация и закрытие работ: формирование актов АОСР по новому приказу Минстроя № 344/пр, КС-2, КС-3, общий журнал работ и журнал входного контроля по фото накладных (за 1 день вместо недели).
2. Сметы и ценообразование: автоматическая проверка и расчет смет по базе ФСНБ-2022 (ресурсно-индексный метод, 49 694 нормы ГЭСН) с региональными индексами Минстроя. Подготовка сметы занимает часы вместо недель.
3. Нормоконтроль чертежей: проверка проектной документации (PDF, DWG) на коллизии СП и ГОСТ до передачи в экспертизу или на стройплощадку.

Подтвержденный результат на реальных объектах: извлечение спецификаций из проекта на 1 370 страниц за 8 минут вместо 40 часов; журнал входного контроля на 728 позиций - за 1 рабочий день. Сервера находятся в РФ, данные защищены по 152-ФЗ.

Наше предложение:
Готовы провести бесплатную демонстрацию на одном из Ваших реальных проектов (проверить проектную документацию на коллизии, рассчитать смету или сформировать комплект документации), чтобы Вы оценили точность и экономию времени на своих цифрах.

Подскажите, пожалуйста, актуальна ли для Вас такая задача? Могу направить официальное КП с выпиской Минцифры и ответить на вопросы.

-- 
С уважением,
Илья Тарасов
ООО «ИТ СтройИнтел»
Тел.: +7-917-769-03-33
Сайт: aistroyintel.ru

Если писать не нужно, ответьте одним словом «стоп», и я больше не напишу."""

    # Double check: no em-dash or en-dash
    body = body.replace("—", "-").replace("–", "-")
    subject = subject.replace("—", "-").replace("–", "-")
    
    # Save to letters table
    cur.execute("""
        INSERT INTO letters (inn, name, to_email, subject, body, facts, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'chernovik', datetime('now'))
    """, (inn, short_cname, to_email, subject, body, "[]"))
    
    new_drafts.append({
        "inn": inn,
        "to": to_email,
        "subject": subject,
        "body": body
    })

conn.commit()
conn.close()

print(f"Added {len(new_drafts)} verified letters to database.")

# 3. Upload to IMAP
print("Uploading 10 new drafts to Yandex Mail via IMAP...")
res = drafts.append_many(new_drafts, dry=False, verbose=True)
print("\nFinished upload result:")
for r in res:
    print(r)
