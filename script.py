cat > ~/Library/Application\ Support/TelegramLogger/logger.py << 'ENDOFSCRIPT'
#!/usr/bin/env python3

import os
import time
import hashlib
import subprocess
from datetime import datetime

LOG_DIR = os.path.expanduser("~/Library/Application Support/TelegramLogger")
MAX_FILE_SIZE_MB = 500
CHECK_INTERVAL = 3
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
seen_hashes = set()

def get_current_log_path():
    today = datetime.now().strftime("%Y-%m-%d")
    existing = sorted([
        f for f in os.listdir(LOG_DIR)
        if f.startswith(f"messages_{today}") and f.endswith(".txt")
    ])
    if existing:
        latest = os.path.join(LOG_DIR, existing[-1])
        if os.path.getsize(latest) < MAX_FILE_SIZE_BYTES:
            return latest
        last_num = int(existing[-1].split("_")[-1].replace(".txt", ""))
        new_name = f"messages_{today}_{last_num + 1:03d}.txt"
        print(f"\n📂 Файл заполнен. Создан новый: {new_name}")
        return os.path.join(LOG_DIR, new_name)
    return os.path.join(LOG_DIR, f"messages_{today}_001.txt")

def write_log(text):
    # Проверка свободного места (минимум 100 МБ)
    stat = os.statvfs(LOG_DIR)
    free_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
    if free_mb < 100:
        print(f"⚠️  Мало места: {free_mb:.0f} МБ. Логирование остановлено.")
        return
    
    log_path = get_current_log_path()
    is_new = not os.path.exists(log_path)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_path, 'a', encoding='utf-8') as f:
        if is_new:
            f.write(f"{'#'*60}\n# Файл создан: {timestamp}\n{'#'*60}\n")
        f.write(f"\n{'='*60}\n[{timestamp}]\n{text.strip()}\n")
    
    size_mb = os.path.getsize(log_path) / (1024 * 1024)
    print(f"[{timestamp}] ✓ {os.path.basename(log_path)} ({size_mb:.2f}/{MAX_FILE_SIZE_MB} МБ)")

def get_telegram_content():
    script = '''
    tell application "System Events"
        if not (exists process "Telegram") then return ""
        tell process "Telegram"
            try
                set allText to ""
                set uiElements to entire contents of window 1
                repeat with el in uiElements
                    try
                        if role of el is "AXStaticText" then
                            set elValue to value of el
                            if elValue is not missing value and elValue is not "" then
                                set allText to allText & elValue & "\\n"
                            end if
                        end if
                    end try
                end repeat
                return allText
            on error
                return ""
            end try
        end tell
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script],
            capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception:
        return ""

def is_telegram_active():
    script = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        return frontApp
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script],
            capture_output=True, text=True, timeout=2)
        return 'Telegram' in result.stdout
    except Exception:
        return False

def log_content(text):
    if not text or len(text.strip()) < 5:
        return
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    if text_hash in seen_hashes:
        return
    seen_hashes.add(text_hash)
    if len(seen_hashes) > 500:
        seen_hashes.clear()
    write_log(text)

def show_stats():
    files = sorted([f for f in os.listdir(LOG_DIR)
        if f.startswith("messages_") and f.endswith(".txt")])
    if not files:
        return
    total = 0
    print("\n📊 Файлы логов:")
    for f in files:
        path = os.path.join(LOG_DIR, f)
        size = os.path.getsize(path)
        total += size
        print(f"   {f}  —  {size/1024:.1f} КБ")
    print(f"   Итого: {total/(1024*1024):.2f} МБ\n")

def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    print("="*55)
    print("  Telegram Logger запущен")
    print(f"  Папка: {LOG_DIR}")
    print(f"  Макс. размер файла: {MAX_FILE_SIZE_MB} МБ")
    print("  Проверка каждые 0.5 сек пока Telegram активен")
    print("  Ctrl+C — остановить")
    print("="*55)
    show_stats()
    last_check = 0
    while True:
        try:
            now = time.time()
            if now - last_check >= CHECK_INTERVAL:
                last_check = now
                if is_telegram_active():
                    content = get_telegram_content()
                    if content:
                        log_content(content)
            time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n✋ Логгер остановлен")
            show_stats()
            break
        except Exception:
            time.sleep(3)

if __name__ == "__main__":
    main()
ENDOFSCRIPT
