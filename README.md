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
### 5️⃣ Arduino 코드 업로드
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

#!/usr/bin/python3
from flask import Flask, render_template
from urllib.request import urlopen
import json, sqlite3, datetime

# ======= ESP8266 정보 =======
device_ip = "192.168.0.115"   # ESP8266 실제 IP 주소 입력
port = "80"
base_url = f"http://{device_ip}:{port}/"

# ======= Flask Web Server =======
app = Flask(__name__, template_folder="./templates")

# ======= SQLite =======
DB_NAME = "button_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS button_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            swVal1 INTEGER,
            deviceIP TEXT,
            timestamp TEXT
        );
    ''')
    conn.commit()
    conn.close()

# ======= ESP8266 JSON  =======
def get_data_from_esp():
    try:
        response = urlopen(base_url, timeout=5)
        data = json.loads(response.read())
        print("[ESP8266 Data]", data)
        return data
    except Exception as e:
        print("", e)
        return None

# ======= DB =======
def insert_to_db(swVal1, deviceIP):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO button_status (swVal1, deviceIP, timestamp) VALUES (?, ?, ?)",
                (swVal1, deviceIP, now))
    conn.commit()
    conn.close()


def get_latest_data():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT swVal1, deviceIP, timestamp FROM button_status ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row if row else (None, None, None)


@app.route('/')
def index():
   
    data = get_data_from_esp()
    if data:
        swVal1 = int(data.get("swVal1", 0))
        deviceIP = data.get("deviceIP", "0.0.0.0")
        insert_to_db(swVal1, deviceIP)  # DB
    else:
        print("")

    # DB
    swVal1, deviceIP, timestamp = get_latest_data()

    # 
    bt1Val = "ON" if swVal1 == 0 else "OFF"

    return render_template("index.html",
                           bt1Val=bt1Val,
                           deviceIP=deviceIP,
                           timestamp=timestamp,
                           redLED1=(swVal1 == 0),
                           bt2Val="N/A")

# ======= Flask 실행 =======
if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=8080)





<html>
  <head>
    <meta charset="UTF-8">
    <title>LED Controller</title>
    <meta name="viewport" content="width=200, initial-scale=1, maximum-scale=1">
    <script type="text/javascript">
        function command(value) {
            if ( window.XMLHttpRequest ) {
                request = new XMLHttpRequest();
            }
            if ( !request ) {
                alert("XMLHttpRequest Error");
                return false;
            }
            var send = 'command=' + value;
            request.open('POST','/led',true);
            request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            request.setRequestHeader('Content-Length', send.length);
            request.setRequestHeader('Connection', 'close');
            request.send(send);
        }
        function reloadrefresh()
        {
            window.location.href='/'
        }
        function senChart()
        {
            window.location.href='/senChart'
        }          
        
    </script>
    <style>
        input[type=button] { background-color: #00ff00; border: 2; border-color: black; color: black; padding: 5px 30px; 
            text-decoration: none; font-size: 15px; margin: 2px; cursor: pointer;}
        input[type=button1] { background-color: #ff0000; border: 2; border-color: black; color: white; padding: 5px 30px; 
            text-decoration: none; font-size: 15px; margin: 2px; cursor: pointer;}
        input[type=button2] { background-color: #808080; border: 2; border-color: black; color: white; padding: 5px 30px; 
            text-decoration: none; font-size: 15px; margin: 2px; cursor: pointer;}
        input[type=button3] { background-color: orange; border: 2; border-color: black; color: white; padding: 5px 30px; 
            text-decoration: none; font-size: 15px; margin: 2px; cursor: pointer;}
        input[type=button4] { background-color: green; border: 2; border-color: black; color: white; padding: 5px 30px; 
            text-decoration: none; font-size: 15px; margin: 2px; cursor: pointer;}
    </style>
  </head>  
  <body>
    <table>
      <tr>
        <td>
          <h1 style = "color:white;background-color:blue;">
          ***Project:Remote Monitoring & Controlling***
          </h1>      
        </td>
      </tr>
      <tr>
        <td>
          <h2 style = "text-align:center;color:white;background-color:green;">
          Made by CTM (2021041089)
          </h2>
        </td>
      </tr>
    </table>
    
    <p></p>
    <p><h2>[BUTTONs Status]</h2></p>
    <table style = "border: 5px solid blue;">
      <tr>
        <th style = "background-color:gray; color:white; font-size:10pt;">
          <h4>Button1Val</h4>                
      </tr>
      <tr>
        <td style = "background-color:green; color:white; font-size:10pt;">{{bt1Val}}</td>
      </tr>
    </table>
    <p><h2>[LEDs Status]</h2></p>
    <table border>
      <tr>
        <td>
          <table border>
            <tr>
              <th style = "background-color:red; color:white; font-size:10pt;">
                RedLED1
              </th>
              
            </tr>
            <tr>
              <td>{% if redLED1 %}
                    ON
                  {% else %}
                    ON
                  {% endif %}              
              </td>
            </tr>
          </table>
        </td>
     
      </tr>
    </table>
    
    <p>
    <h2>[Links]</h2>
    <p>
      <a href="/">Home</a>
    </p>
    
    <h3>Latest Data (DB)</h3>
    <table border="1" style="width:60%; margin: 0 auto 20px auto">
        <tr>
            <th>Button1</th>
            <th>Device IP</th>
            <th>Stored Time</th>
        </tr>
        <tr>
            <td style="text-align:center;">{{ bt1Val }}</td>
            <td style="text-align:center;">{{ deviceIP }}</td>
            <td style="text-align:center;">{{ timestamp }}</td>
        </tr>
    </table>
    <meta http-equiv="refresh" content="5">
  </body>
</html>





