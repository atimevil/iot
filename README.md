# 라즈베리 파이 게임 종합 세트

IoT 시스템 응용 - 5조 팀 프로젝트

## 프로젝트 개요

라즈베리 파이 4와 아두이노 풀 키트(EK100)를 활용한 게임 콘솔 시스템입니다.
웹 브라우저에서 게임을 플레이하면서 동시에 하드웨어 디스플레이와 센서를 활용합니다.

### 포함된 게임
- 🐍 **Snake Game**: 클래식 스네이크 게임
- 🧱 **Tetris**: 테트리스 블록 퍼즐
- 🐦 **Flappy Bird**: 파이프 피하기 게임

### 사용 하드웨어

**활성화된 하드웨어:**
- 라즈베리 파이 4
- 16x2 I2C LCD 디스플레이
- 8x8 도트 매트릭스 (1088BS+) - 16핀 직접 연결
- IR 리모컨 및 수신기
- 부저 (Buzzer)

**비활성화 (웹 화면으로 대체):**
- 7-Segment FND → 웹에서 점수 표시
- RGB LED → 웹에서 시각 효과 표시

## 프로젝트 구조

```
iot/
├── config/
│   └── pins.py                 # 핀 설정
├── drivers/
│   ├── lcd_driver.py           # LCD 드라이버
│   ├── ir_driver.py            # IR 리모컨 드라이버
│   ├── buzzer_driver.py        # 부저 드라이버
│   ├── led_driver.py           # LED 드라이버
│   ├── fnd_driver.py           # 7-Segment 드라이버
│   └── dotmatrix_driver.py     # 도트 매트릭스 드라이버
├── games/
│   ├── snake_game.py           # 스네이크 게임 로직
│   ├── tetris_game.py          # 테트리스 게임 로직
│   └── flappy_bird_game.py     # 플래피 버드 게임 로직
├── web/
│   ├── app.py                  # Flask 웹 애플리케이션
│   └── templates/              # HTML 템플릿
│       ├── index.html          # 메인 페이지
│       ├── snake.html          # 스네이크 게임
│       ├── tetris.html         # 테트리스 게임
│       └── flappy.html         # 플래피 버드 게임
├── requirements.txt
└── README.md
```

## 설치 방법

### 1. 라즈베리 파이 OS 업데이트
```bash
sudo apt-get update
sudo apt-get upgrade
```

### 2. Python 및 필수 패키지 설치
```bash
sudo apt-get install python3-pip python3-dev
sudo apt-get install python3-smbus i2c-tools
sudo apt-get install python3-rpi.gpio
```

### 3. I2C 활성화
```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
```

### 4. 프로젝트 클론 및 의존성 설치
```bash
cd ~/
git clone [repository-url] iot
cd iot
pip3 install -r requirements.txt
```

## 하드웨어 연결

### I2C LCD (16x2)
- SDA -> GPIO 2 (Pin 3)
- SCL -> GPIO 3 (Pin 5)
- VCC -> 5V
- GND -> GND

### IR Receiver
- OUT -> GPIO 18 (Pin 12)
- VCC -> 3.3V
- GND -> GND

### Buzzer
- Positive -> GPIO 23 (Pin 16)
- Negative -> GND

### 8x8 Dot Matrix 1088BS+ (16핀 직접 연결)

**Row Pins (Anode, +)** - 행 선택
- Row 0 -> GPIO 4 (Pin 7)
- Row 1 -> GPIO 17 (Pin 11)
- Row 2 -> GPIO 27 (Pin 13)
- Row 3 -> GPIO 22 (Pin 15)
- Row 4 -> GPIO 5 (Pin 29)
- Row 5 -> GPIO 6 (Pin 31)
- Row 6 -> GPIO 13 (Pin 33)
- Row 7 -> GPIO 19 (Pin 35)

**Column Pins (Cathode, -)** - 열 데이터
- Col 0 -> GPIO 26 (Pin 37)
- Col 1 -> GPIO 12 (Pin 32)
- Col 2 -> GPIO 16 (Pin 36)
- Col 3 -> GPIO 20 (Pin 38)
- Col 4 -> GPIO 21 (Pin 40)
- Col 5 -> GPIO 7 (Pin 26)
- Col 6 -> GPIO 8 (Pin 24)
- Col 7 -> GPIO 25 (Pin 22)

### 비활성화된 하드웨어
- **RGB LED**: 제거됨 (웹 화면에서 효과 표시)
- **7-Segment FND**: 제거됨 (웹 화면에서 점수 표시)

## 실행 방법

### 웹 서버 시작
```bash
cd ~/iot/web
python3 app.py
```

### 웹 브라우저에서 접속
```
http://[라즈베리파이-IP]:5000
```

라즈베리 파이에서 직접 실행하는 경우:
```
http://localhost:5000
```

## 게임 조작 방법

### Snake Game
- **키보드**: 화살표 키 또는 W/A/S/D
- **IR 리모컨**: 2(↑), 4(←), 6(→), 8(↓)
- **목표**: 먹이를 먹고 뱀을 키우기

### Tetris
- **키보드**: ← → (이동), ↑ (회전), ↓ (빠른 낙하)
- **IR 리모컨**: 4(←), 6(→), 5(회전)
- **목표**: 한 줄을 완성하여 지우기

### Flappy Bird
- **키보드**: 스페이스 바
- **마우스**: 화면 클릭
- **IR 리모컨**: 5번 버튼
- **목표**: 파이프 사이를 통과하기

### 공통 조작
- **ESC**: 게임 종료하고 메인 메뉴로
- **R**: 게임 재시작

## 난이도 설정

모든 게임에서 3가지 난이도를 선택할 수 있습니다:
- **Easy**: 느린 속도
- **Normal**: 보통 속도 (기본값)
- **Hard**: 빠른 속도

## 하드웨어 피드백

게임 플레이 중 다음과 같은 피드백이 제공됩니다:

**하드웨어:**
- **LCD**: 현재 게임 이름과 난이도 표시
- **도트 매트릭스 (1088BS+)**: 게임 화면 8x8 LED로 시각화
- **부저**: 점수 획득 시 효과음, 게임 오버 시 멜로디

**웹 인터페이스:**
- **점수 표시**: 실시간 점수 업데이트
- **시각 효과**: 게임 시작/종료 시 화면 효과

## 문제 해결

### I2C 장치가 인식되지 않을 때
```bash
sudo i2cdetect -y 1
```
I2C 주소 확인 후 `config/pins.py`에서 `LCD_I2C_ADDRESS` 수정

### GPIO 권한 오류
```bash
sudo usermod -a -G gpio,i2c $USER
# 재로그인 필요
```

### 도트 매트릭스가 제대로 표시되지 않을 때
```bash
# 개별 픽셀 테스트
python3 -c "from drivers.dotmatrix_driver import DotMatrix; dm = DotMatrix(); dm.display_pixel(4, 4); import time; time.sleep(3); dm.cleanup()"

# 숫자 표시 테스트
python3 -c "from drivers.dotmatrix_driver import DotMatrix; dm = DotMatrix(); dm.display_number(8); import time; time.sleep(3); dm.cleanup()"
```
- 16개 핀 연결 확인 (8 Row + 8 Column)
- Row 핀: Anode(+) 연결 확인
- Column 핀: Cathode(-) 연결 확인
- 전원 공급 확인

### 포트가 이미 사용 중일 때
```bash
sudo lsof -i :5000
sudo kill -9 [PID]
```

## 개발자

- **팀장**: 김태형
- **팀원**: 김지환, 나민서
- **지도 교수**: 송기범

## 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.
