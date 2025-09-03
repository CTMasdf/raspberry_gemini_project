import os
import subprocess
import time
import json
import serial
import speech_recognition as sr
from gtts import gTTS
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------- 환경 변수 & Gemini API -------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------- 경로 설정 -------------------
IMAGE_PATH = "/home/aibot/chatbot_project/capture.jpg"
HISTORY_FILE = "conversation_history.json"

# ------------------- 아두이노 시리얼 -------------------
COMMAND_KEYWORDS = [
    'M_Sunny', 'M_partly_cloudy', 'M_cloudy', 'M_rainy', 'M_sleet', 'M_snowy',
    'M_stop', 'M_forward', 'M_backward', 'M_turn_left', 'M_turn_right',
    'M_spin_left', 'M_spin_right', 'M_home'
]

try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    print("✅ 아두이노 연결 성공")
except Exception as e:
    print(f"❌ 아두이노 연결 실패: {e}")
    arduino = None
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

# ------------------- TTS -------------------
def speak_text(text):
    print("🤖 Gemini:", text)
    tts = gTTS(text=text, lang="ko")
    tts.save("response.mp3")
    os.system("mpg321 -q response.mp3")

# ------------------- 아두이노 -------------------
def extract_command(text):
    text_lower = text.lower()
    for keyword in COMMAND_KEYWORDS:
        if keyword.lower() in text_lower:
            return keyword
    return None

def send_to_arduino(command):
    if command and arduino:
        try:
            arduino.write((command + '\n').encode('utf-8'))
            print("아두이노로 전송:", command)
        except Exception as e:
            print("⚠️ 아두이노 전송 오류:", e)

# ------------------- Gemini API -------------------
def generate_response(prompt):
    try:
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

# ------------------- 사진 촬영 -------------------
def take_picture():
    subprocess.run(["rpicam-still", "-o", IMAGE_PATH])
    print("📷 사진 촬영 완료:", IMAGE_PATH)

def ask_gemini_about_image():
    if not os.path.exists(IMAGE_PATH):
        return "사진이 존재하지 않습니다."
    with open(IMAGE_PATH, "rb") as f:
        image_data = f.read()
    response = model.generate_content(
        ["방금 찍은 사진에 대해 설명해줘.", {"mime_type": "image/jpeg", "data": image_data}]
    )
    return response.text

# ------------------- 명령어 처리 -------------------
def handle_command(user_text):
    if "사진" in user_text and ("찍" in user_text or "촬영" in user_text):
        take_picture()
        answer = ask_gemini_about_image()
    else:
        conversation_history.append({"role": "user", "parts": user_text})
        prompt = build_prompt()
        answer = generate_response(prompt)
        conversation_history.append({"role": "model", "parts": answer})
        save_conversation_history()

    # 아두이노 명령어 추출
    command = extract_command(answer)
    send_to_arduino(command)

    speak_text(answer)

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

            if "종료" in question or "그만" in question:
                speak_text("대화를 종료합니다. 안녕히 계세요!")
                break

            handle_command(question)

# ------------------- 실행 -------------------
if __name__ == "__main__":
    chat_bot()
