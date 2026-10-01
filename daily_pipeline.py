# -*- coding: utf-8 -*-
"""
daily_pipeline.py — Ежедневный автоматический конвейер AI-отдела продаж.
Запуск: python daily_pipeline.py

Работает строго по правилам безопасности:
1. Выгрузка новых компаний из реестра МСП
2. Отсев по вилкам портрета (ОКВЭД, статус, численность, выручка из ГИР БО)
3. Обогащение ЛПР (ЕГРЮЛ) и контактами
4. Проверка стоп-листа
5. Подготовка писем СТРОГО В ЧЕРНОВИКИ (никакой автоотправки адресатам)
6. Генерация суточного отчета в out/
"""

import subprocess
import sys
import os
import datetime

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "scripts")
DB_PATH = os.path.join(HERE, "data", "leads.db")
CONFIG = os.path.join(HERE, "config.json")
OUT_DIR = os.path.join(HERE, "out")

def run(cmd_list, desc):
    print(f"\n{'='*60}\n[ШАГ] {desc}\n{'='*60}")
    res = subprocess.run(cmd_list, cwd=HERE, text=True, capture_output=True, encoding='utf-8', errors='replace')
    if res.stdout:
        print(res.stdout)
    if res.returncode != 0 and res.stderr:
        print(f"Внимание/Ошибка:\n{res.stderr}")
    return res.returncode

def main():
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"Запуск конвейера AI-отдела продаж: {stamp}")

    # 1. Синхронизация стоп-листа
    run([sys.executable, os.path.join(SCRIPTS, "stoplist.py"), "--db", DB_PATH, "--import-config"], 
        "Синхронизация стоп-листа из config.json")

    # 2. Выручка из ГИР БО по необработанным компаниям (пакет 20 шт)
    run([sys.executable, os.path.join(SCRIPTS, "fns_bo.py"), "--config", CONFIG, "--db", DB_PATH, "--limit", "20", "--live"], 
        "Добор официальной выручки из ГИР БО")

    # 3. Фильтрация и воронка отсева
    run([sys.executable, "run_otsev.py"], 
        "Применение правил отсева и расчет воронки")

    # 4. Добор директоров из ЕГРЮЛ по выжившим
    run([sys.executable, os.path.join(SCRIPTS, "fns_egrul.py"), "--db", DB_PATH, "--limit", "10", "--live"], 
        "Обогащение: поиск генеральных директоров в ЕГРЮЛ")

    # 5. Раскладка в черновики (с лимитом дня)
    run([sys.executable, os.path.join(SCRIPTS, "drafts.py"), "--db", DB_PATH, "--status", "ready", "--limit", "10", "--append"], 
        "Раскладка готовых писем в папку «Черновики»")

    # 6. Обновление сводных HTML-отчетов
    run([sys.executable, os.path.join(SCRIPTS, "report.py"), "--db", DB_PATH, "--out", OUT_DIR], 
        "Генерация актуальных аналитических отчетов")

    print(f"\n[ГОТОВО] Дневной прогон завершен. Все новые письма разложены по черновикам.")
    print(f"Отчеты доступны в: {OUT_DIR}")

if __name__ == "__main__":
    main()
