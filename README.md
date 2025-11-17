# 라즈베리 파이 게임 종합 세트

IoT 시스템 응용 - 5조 팀 프로젝트

## 프로젝트 개요

라즈베리 파이 4와 아두이노 풀 키트(EK100)를 활용한 웹 기반 게임 콘솔 시스템입니다.
Flask와 WebSocket을 사용하여 웹 브라우저에서 게임을 플레이하고, IR 리모컨과 부저를 통해 하드웨어 피드백을 제공합니다.

### 포함된 게임
- 🐍 **Snake Game** (8x8): 클래식 스네이크 게임 - Easy/Normal/Hard 난이도
- 🧱 **Tetris** (8x16): 테트리스 블록 퍼즐
- 🍉 **수박게임 (Suika Game)**: 물리 기반 과일 합치기 퍼즐

### 사용 하드웨어

**최소 하드웨어 구성:**
- 라즈베리 파이 4
- IR 리모컨 및 수신기 (GPIO 18)
- 부저 (GPIO 23) - 게임 효과음

**웹 인터페이스로 구현:**
- 게임 화면 → HTML5 Canvas
- 점수 표시 → 웹 UI
- 시각 효과 → CSS/JavaScript
- 스코어보드 → SQLite 데이터베이스

## 프로젝트 구조

```
iot/
├── config/
│   └── pins.py                 # 핀 설정 (IR + Buzzer)
├── drivers/
│   ├── ir_driver.py            # IR 리모컨 드라이버
│   └── buzzer_driver.py        # 부저 드라이버
├── database/
│   ├── models.py               # SQLite 데이터베이스 모델
│   └── game_scores.db          # 점수 데이터베이스 (자동 생성)
├── games/
│   ├── snake_game.py           # 스네이크 게임 로직 (8x8)
│   ├── tetris_game.py          # 테트리스 게임 로직 (8x16)
│   └── suika_game.py           # 수박게임 로직 (Physics)
├── web/
│   ├── app.py                  # Flask 웹 애플리케이션
│   └── templates/              # HTML 템플릿
│       ├── index.html          # 메인 메뉴
│       ├── snake.html          # 스네이크 게임
│       ├── tetris.html         # 테트리스 게임
│       ├── suika.html          # 수박게임
│       └── scoreboard.html     # 스코어보드
├── requirements.txt
├── README.md
└── CLAUDE.md
```

## 라즈베리파이4 하드웨어 연결

### 핀 배치도 참고
라즈베리파이4는 **BCM 모드**를 사용합니다. 아래 핀 번호는 **물리적 핀 번호 (Physical Pin)**와 **BCM GPIO 번호**를 모두 표시합니다.

### IR Receiver (필수)
| IR 핀 | 연결 위치 | 라즈베리파이 핀 |
|-------|----------|----------------|
| OUT | 신호 | GPIO 18 (Physical Pin 12) |
| VCC | 전원 | 3.3V (Physical Pin 1 또는 17) |
| GND | 접지 | GND (Physical Pin 6, 9, 14, 20, 25, 30, 34, 39 중 아무거나) |

**연결 방법:**
1. IR Receiver의 OUT 핀 → 라즈베리파이 **Pin 12 (GPIO 18)**
2. IR Receiver의 VCC 핀 → 라즈베리파이 **Pin 1 (3.3V)**
3. IR Receiver의 GND 핀 → 라즈베리파이 **Pin 6 (GND)**

### Buzzer (선택 - 게임 효과음용)
| Buzzer 핀 | 연결 위치 | 라즈베리파이 핀 |
|-----------|----------|----------------|
| Positive (+) | 신호 | GPIO 23 (Physical Pin 16) |
| Negative (-) | 접지 | GND (Physical Pin 14 또는 다른 GND 핀) |

**연결 방법:**
1. Buzzer의 긴 다리(+) → 라즈베리파이 **Pin 16 (GPIO 23)**
2. Buzzer의 짧은 다리(-) → 라즈베리파이 **Pin 14 (GND)**

### 핀 맵 요약
```
라즈베리파이4 GPIO 헤더 (40핀)
┌─────┬──────┬──────┬─────┐
│  1  │ 3.3V │  2   │ 5V  │  ← Pin 1: IR VCC 연결
│  3  │ SDA  │  4   │ 5V  │
│  5  │ SCL  │  6   │ GND │  ← Pin 6: IR GND 연결
│  7  │ GP4  │  8   │ TX  │
│  9  │ GND  │  10  │ RX  │
│  11 │ GP17 │  12  │GP18 │  ← Pin 12: IR OUT 연결
│  13 │ GP27 │  14  │ GND │  ← Pin 14: Buzzer GND 연결
│  15 │ GP22 │  16  │GP23 │  ← Pin 16: Buzzer + 연결
└─────┴──────┴──────┴─────┘
```

### 하드웨어 미설치 시
- 게임은 웹 브라우저에서 **키보드만으로도** 플레이 가능합니다
- IR 리모컨과 부저 없이도 모든 기능이 정상 작동합니다
- 하드웨어가 없으면 시뮬레이션 모드로 자동 전환됩니다

## 라즈베리파이4 설치 및 실행 가이드

### 1단계: 라즈베리파이 OS 준비
```bash
# OS 업데이트
sudo apt-get update
sudo apt-get upgrade -y

# Python 및 GPIO 라이브러리 설치
sudo apt-get install python3-pip python3-dev -y
sudo apt-get install python3-rpi.gpio -y
```

### 2단계: 프로젝트 다운로드
```bash
# 홈 디렉토리로 이동
cd ~/

# Git clone (또는 USB/파일 복사)
git clone [repository-url] iot

# 프로젝트 디렉토리로 이동
cd iot
```

### 3단계: LIRC 설치 (IR 리모컨용)
```bash
# LIRC 설치
sudo apt-get install lirc -y

# LIRC 설정 편집
sudo nano /etc/lirc/lirc_options.conf
```

**lirc_options.conf 설정:**
```
driver = default
device = /dev/lirc0
```

**하드웨어 설정 (/boot/config.txt):**
```bash
sudo nano /boot/config.txt

# 파일 끝에 추가:
dtoverlay=gpio-ir,gpio_pin=18
```

**재부팅:**
```bash
sudo reboot
```

**IR 리모컨 학습 (CR2025):**
```bash
# IR 코드 기록
sudo irrecord -d /dev/lirc0 ~/lircd.conf

# 설정 복사
sudo cp ~/lircd.conf /etc/lirc/lircd.conf

# LIRC 재시작
sudo systemctl restart lircd
```

### 4단계: Python 패키지 설치
```bash
# requirements.txt에서 패키지 설치
pip3 install -r requirements.txt

# 수박게임용 물리 엔진 (필수)
pip3 install pymunk==6.5.0

# IR 리모컨 라이브러리 (필수)
pip3 install python-lirc==2.0.1
```

### 5단계: GPIO 권한 설정
```bash
# 현재 사용자를 gpio 그룹에 추가
sudo usermod -a -G gpio $USER

# 재로그인 필요 (SSH 사용 시 재접속)
# 또는 임시로 sudo로 실행 가능
```

### 6단계: 하드웨어 연결 확인
```bash
# LIRC 테스트 (IR 리모컨)
irw
# 리모컨 버튼을 누르면 코드가 표시됨
# Ctrl+C로 종료

# Buzzer 테스트
python3 -c "from drivers.buzzer_driver import Buzzer; b = Buzzer(); b.beep(0.5)"
```

### 7단계: 웹 서버 시작
```bash
cd ~/iot/web
python3 app.py
```

**서버 시작 확인:**
```
==================================================
Game Console Server Starting...
==================================================
Hardware: Available
Database: SQLite
Games: Snake (8x8), Tetris (8x16), Suika
==================================================
 * Running on http://0.0.0.0:5000
```

### 8단계: 게임 접속

**같은 네트워크의 다른 기기에서:**
1. 라즈베리파이 IP 확인:
   ```bash
   hostname -I
   ```
   예: `192.168.0.100`

2. 브라우저에서 접속:
   ```
   http://192.168.0.100:5000
   ```

**라즈베리파이에서 직접:**
```
http://localhost:5000
```

### 백그라운드 실행 (옵션)
서버를 백그라운드에서 계속 실행하려면:
```bash
cd ~/iot/web
nohup python3 app.py > ~/game_console.log 2>&1 &

# 프로세스 확인
ps aux | grep app.py

# 서버 종료
pkill -f app.py
```

## 게임 조작 방법

### 🐍 Snake Game (8x8 Grid)
1. **게임 시작**: "▶️ 시작" 버튼 클릭 → 닉네임 입력
2. **조작**:
   - **키보드**: 화살표 키
   - **IR 리모컨**: 2(↑), 4(←), 6(→), 8(↓)
3. **난이도**: Easy / Normal / Hard (게임 시작 전 선택)
4. **목표**: 먹이를 먹고 뱀을 키우기
5. **종료**: 게임 오버 시 자동으로 점수 저장

### 🧱 Tetris (8x16 Grid)
1. **게임 시작**: "▶️ 시작" 버튼 클릭 → 닉네임 입력
2. **조작**:
   - **키보드**: ← → (이동), ↑ (회전), ↓ (빠른 낙하)
   - **IR 리모컨**: 4(←), 6(→), 2(회전), 8(빠른 낙하)
3. **목표**: 한 줄을 완성하여 지우기
4. **종료**: 게임 오버 시 자동으로 점수 저장

### 🍉 수박게임 (Suika Game)
1. **게임 시작**: "▶️ 시작" 버튼 클릭 → 닉네임 입력
2. **조작**:
   - **키보드**: ← → (위치 이동), ↓/Enter/Space (과일 떨어뜨리기)
   - **IR 리모컨**: 4(←), 6(→), 5(과일 떨어뜨리기)
3. **목표**: 같은 과일을 합쳐 더 큰 과일 만들기 (체리 → 딸기 → ... → 수박)
4. **종료**: 게임 오버 시 자동으로 점수 저장

### IR 리모컨 버튼 매핑
- **2번**: 위쪽 화살표 (↑)
- **4번**: 왼쪽 화살표 (←)
- **5번**: 선택/확인 (OK)
- **6번**: 오른쪽 화살표 (→)
- **8번**: 아래쪽 화살표 (↓)

## 난이도 설정

**Snake Game만** 3가지 난이도를 선택할 수 있습니다:
- **Easy**: 느린 속도 (초보자 추천)
- **Normal**: 보통 속도 (기본값)
- **Hard**: 빠른 속도 (고수 도전)

**Tetris와 수박게임**은 단일 난이도로 제공됩니다.

## 주요 기능

### 실시간 게임 플레이
- **Flask-SocketIO**: WebSocket 기반 실시간 게임 상태 동기화
- **20 FPS**: 부드러운 화면 업데이트 (50ms 간격)
- **Canvas 렌더링**: HTML5 Canvas로 게임 화면 구현

### 하드웨어 피드백
- **부저**: 점수 획득 시 효과음, 게임 오버 시 멜로디
- **IR 리모컨**: 무선 게임 조작 (5개 버튼)

### 플레이어 시스템
- **닉네임 입력**: 모든 게임 시작 전 닉네임 입력 (최대 20자)
- **자동 저장**: 게임 오버 시 자동으로 점수 DB 저장
- **플레이어별 기록**: 닉네임과 함께 점수 저장

### 점수 시스템
- **SQLite 데이터베이스**: 모든 게임 점수 영구 저장
- **스코어보드**: 게임별/전체 최고 기록 확인 (플레이어 이름 포함)
- **통계**: 총 게임 수, 평균 점수, 최고 점수 등
- **난이도별 랭킹**: Snake 게임의 경우 난이도별 별도 랭킹
- **타임스탬프**: 점수 달성 시간 기록

### 수박게임 물리 엔진
- **Pymunk**: 2D 물리 엔진 사용
- **중력/충돌**: 현실적인 과일 물리 시뮬레이션
- **과일 합치기**: 같은 종류 과일 충돌 시 자동 합체
- **10단계 과일**: 체리(1점) → 수박(100점)

## 문제 해결

### GPIO 권한 오류
```bash
sudo usermod -a -G gpio $USER
# 재로그인 필요
```

### IR 리모컨이 작동하지 않을 때
```bash
# IR 수신 테스트
python3 -c "from drivers.ir_driver import IRRemote; ir = IRRemote(); print('Press IR buttons...')"
```
- IR 수신기 연결 확인 (GPIO 18)
- 리모컨 배터리 확인
- `config/pins.py`에서 IR 코드 값 확인 및 수정

### 부저가 소리나지 않을 때
```bash
# 부저 테스트
python3 -c "from drivers.buzzer_driver import Buzzer; b = Buzzer(); b.beep(0.5)"
```
- 부저 연결 확인 (GPIO 23)
- 부저 극성 확인 (+ → GPIO, - → GND)

### 포트가 이미 사용 중일 때
```bash
sudo lsof -i :5000
sudo kill -9 [PID]
```

### 수박게임 물리 엔진 오류
Pymunk가 설치되지 않았다면:
```bash
pip3 install pymunk==6.5.0
```

### 데이터베이스 초기화
점수 기록을 모두 삭제하려면:
```bash
rm database/game_scores.db
# 다음 실행 시 자동으로 새로 생성됨
```

## 기술 스택

### Backend
- **Flask**: 웹 서버 프레임워크
- **Flask-SocketIO**: 실시간 양방향 통신
- **SQLite**: 경량 데이터베이스

### Frontend
- **HTML5 Canvas**: 게임 화면 렌더링
- **Socket.IO**: 클라이언트 WebSocket 통신
- **JavaScript (ES6)**: 클라이언트 게임 로직
- **CSS3**: 반응형 UI 스타일링

### Hardware
- **RPi.GPIO**: 라즈베리 파이 GPIO 제어
- **Pymunk**: 2D 물리 엔진 (수박게임)

### Architecture
```
┌─────────────┐       WebSocket        ┌──────────────┐
│   Browser   │ ◄──────────────────► │ Flask Server │
│  (Canvas)   │    game_state (20FPS) │  (SocketIO)  │
└─────────────┘                        └──────┬───────┘
                                              │
                                    ┌─────────┴─────────┐
                                    │   Game Engine     │
                                    │ ┌─────┬─────┬───┐ │
                                    │ │Snake│Tetris│Sui│ │
                                    │ │ 8x8 │ 8x16 │ka │ │
                                    │ └─────┴─────┴───┘ │
                                    └─────────┬─────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────┐
                    │                         │                     │
              ┌─────▼──────┐           ┌──────▼──────┐      ┌──────▼──────┐
              │  IR Remote │           │   Buzzer    │      │  Database   │
              │  (GPIO 18) │           │  (GPIO 23)  │      │   (SQLite)  │
              └────────────┘           └─────────────┘      └─────────────┘
```

## API Endpoints

### REST API
- `GET /` - 메인 메뉴
- `GET /game/<game_name>` - 게임 페이지 (snake, tetris, suika)
- `GET /scoreboard` - 스코어보드 페이지
- `GET /api/games` - 게임 목록 조회
- `GET /api/scores/<game_name>` - 게임별 점수 조회
- `GET /api/scores/all` - 전체 점수 조회

### WebSocket Events
**Client → Server:**
- `start_game` - 게임 시작 (게임명, 난이도, 플레이어명)
- `game_input` - 게임 입력 (게임명, 액션)
- `reset_game` - 게임 리셋
- `stop_game` - 게임 종료 및 점수 저장
- `save_score` - 점수 수동 저장

**Server → Client:**
- `game_state` - 게임 상태 브로드캐스트 (20 FPS)
- `game_started` - 게임 시작 확인
- `game_reset` - 게임 리셋 확인
- `game_stopped` - 게임 종료 확인
- `error` - 오류 메시지

## 개발자

- **팀장**: 김태형
- **팀원**: 김지환, 나민서
- **지도 교수**: 송기범

## 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.
