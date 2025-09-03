# ------------------- 필요한 라이브러리 -------------------
import serial
import time
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
import json
from dotenv import load_dotenv

# ------------------- 환경 변수 & Gemini API -------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ------------------- 대화 기록 & 명령어 -------------------
HISTORY_FILE = "conversation_history.json"
COMMAND_KEYWORDS = [
    'M_Sunny', 'M_partly_cloudy', 'M_cloudy', 'M_rainy', 'M_sleet', 'M_snowy',
    'M_stop', 'M_forward', 'M_backward', 'M_turn_left', 'M_turn_right',
    'M_spin_left', 'M_spin_right', 'M_home'
]

# ------------------- 시리얼 연결 -------------------
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    print("✅ 아두이노 연결 성공")
except Exception as e:
    print(f"❌ 아두이노 연결 실패: {e}")
    exit()
time.sleep(2)

# ------------------- 대화 기록 관리 -------------------
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

# ------------------- TTS -------------------
def speak_text(text):
    tts = gTTS(text=text, lang='ko')
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")

# ------------------- STT -------------------
def recognize_speech(prompt=None):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        if prompt:
            print(prompt)
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="ko-KR")
            print("📝 인식된 텍스트:", text)
            return text
        except:
            print("⚠️ 음성 인식 실패")
            return ""

# ------------------- 명령어 추출 & 아두이노 전송 -------------------
def extract_command(text):
    text_lower = text.lower()
    for keyword in COMMAND_KEYWORDS:
        if keyword.lower() in text_lower:
            return keyword
    return None

def send_to_arduino(command):
    if command:
        try:
            arduino.write((command + '\n').encode('utf-8'))
            print("아두이노로 전송:", command)
        except Exception as e:
            print("⚠️ 아두이노 전송 오류:", e)

# ------------------- 챗봇 메인 루프 -------------------
def chat_bot():
    print("🎙️ 아이봇 음성 챗봇 시작. '마린'이라고 말하면 질문을 받을게요.")
    while True:
        trigger = recognize_speech("'마린'라고 말해주세요")
        if "마린" in trigger:
            speak_text("질문하세요")
            question = recognize_speech("질문을 말해주세요")
            if not question:
                continue

            conversation_history.append({"role": "user", "parts": question})

            prompt = build_prompt()
            response_text = generate_response(prompt)
            print(f"🤖 아이봇: {response_text}")

            # Gemini 응답에서 아두이노 명령어 추출
            command = extract_command(response_text)
            send_to_arduino(command)

            speak_text(response_text)
            conversation_history.append({"role": "model", "parts": response_text})
            save_conversation_history()

# ------------------- 실행 -------------------
if __name__ == "__main__":
    chat_bot()
