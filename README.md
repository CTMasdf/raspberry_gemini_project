# Raspberry Gemini Project

AI 기반 챗봇 및 로봇 제어 프로젝트입니다.  
이 프로젝트는 라즈베리파이에서 Gemini API를 활용하여 음성 및 텍스트 인터페이스로 로봇을 제어하고 상호작용하는 기능을 구현합니다.

---

## 프로젝트 파일
아래 3개중 한개를 선택해서 실행시키면 됩니다.
- [`chatbot.py`](https://github.com/CTMasdf/raspberry_gemini_project/blob/main/chatbot.py)  
  Gemini API를 이용한 챗봇 모듈
- [`final.py`](https://github.com/CTMasdf/raspberry_gemini_project/blob/main/final.py)  
  전체 로봇 제어 및 실행 메인 파일
- [`keyboard.py`](https://github.com/CTMasdf/raspberry_gemini_project/blob/main/keyboard.py)  
  키보드 입력 모듈

---

## 🚀 설치 및 실행 방법

### 1️⃣ Raspberry Pi 가상환경 생성
```bash
python3 -m venv venv
source venv/bin/activate
```
### 2️⃣ 필수 패키지 설치
```bash
pip install -r requirements.txt
```

### 3️⃣ Gemini API 키 환경 변수 설정
.env 파일 생성 후 아래 내용 추가:
```txt
GEMINI_API_KEY=여기에_토큰_입력
```

Python 코드에서 불러오기:
```bash
import os
gemini_key = os.getenv("GEMINI_API_KEY")
```

### 4️⃣ Python 코드 실행
```bash
python3 Raspberrypi.py
```
### '5' Arduino 코드 업로드
- Arduino IDE에서 arduino_code.ino 업로드
- 보드: Arduino Mega 2560 선택
- USB로 Raspberry Pi와 연결

## 📦 Requirements

`requirements.txt` 예시:

```txt
# 음성 인식
SpeechRecognition==3.8.1
PyAudio==0.2.13

# TTS (하나만 선택)
gTTS==2.3.1
# pyttsx3==2.90

# 시리얼 통신
pyserial==3.6

# 환경 변수 관리
python-dotenv==1.0.1
```
💡 Raspberry Pi Tip
PyAudio 설치 전 아래 패키지 설치가 필요합니다:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```
