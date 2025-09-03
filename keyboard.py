# ------------------- 필요한 라이브러리 -------------------
import serial
import time
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# ------------------- 환경 변수 & Gemini API -------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ------------------- 시리얼 & 기록 -------------------
HISTORY_FILE = "conversation_history.json"
COMMAND_KEYWORDS = [
    'M_Sunny', 'M_partly_cloudy', 'M_cloudy', 'M_rainy', 'M_sleet', 'M_snowy',
    'M_stop', 'M_forward', 'M_backward', 'M_turn_left', 'M_turn_right',
    'M_spin_left', 'M_spin_right'
]

# ------------------- 시리얼 연결 -------------------
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    print("✅ 아두이노 연결 성공")
except Exception as e:
    print(f"❌ 아두이노 연결 실패: {e}")
    exit()
time.sleep(2)  # Arduino 준비 대기

# ------------------- 대화 기록 -------------------
def load_conversation_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_conversation_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(conversation_history, f, ensure_ascii=False, indent=2)

conversation_history = load_conversation_history()

# ------------------- Gemini API 응답 -------------------
def generate_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini 오류: {e}"

def build_prompt():
    prompt = ""
    for msg in conversation_history:
        role = "User" if msg["role"] == "user" else "Chatbot"
        prompt += f"{role}: {msg['parts']}\n"
    return prompt

# ------------------- 아두이노 명령어 전송 -------------------
def extract_command(text):
    text_lower = text.lower()
    for keyword in COMMAND_KEYWORDS:
        if keyword.lower() in text_lower:
            return keyword
    return None

def send_to_arduino(command):
    if command:
        try:
            arduino.write((command + '\n').encode())
            print("📤 아두이노로 전송:", command)
        except Exception as e:
            print("⚠️ 아두이노 전송 오류:", e)

# ------------------- 키보드 입력 기반 챗봇 -------------------
def chat_bot():
    print("💡 아이봇 챗봇이 시작되었습니다. 명령어 또는 질문을 입력하세요.")
    while True:
        user_input = input("👤 입력: ").strip()  # 키보드 입력
        if not user_input:
            continue

        # 대화 기록에 저장
        conversation_history.append({"role": "user", "parts": user_input})

        # Gemini API 응답
        prompt = build_prompt()
        response_text = generate_response(prompt)
        print(f"🤖 아이봇: {response_text}")

        # 명령어 추출 후 Arduino 전송
        command = extract_command(response_text)
        send_to_arduino(command)

        # 대화 기록 저장
        conversation_history.append({"role": "model", "parts": response_text})
        save_conversation_history()

# ------------------- 실행 -------------------
if __name__ == "__main__":
    chat_bot()
