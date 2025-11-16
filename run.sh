#!/bin/bash
# Raspberry Pi Game Console Launcher

echo "🎮 라즈베리 파이 게임 콘솔 시작 중..."
echo ""

# Check if running on Raspberry Pi
if ! [ -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "⚠️  경고: 라즈베리 파이에서 실행하지 않고 있습니다."
    echo "   하드웨어 기능이 시뮬레이션 모드로 동작합니다."
    echo ""
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ 오류: Python 3가 설치되어 있지 않습니다."
    exit 1
fi

echo "✓ Python 버전: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 가상 환경을 생성하는 중..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 가상 환경 활성화 중..."
source venv/bin/activate

# Install/Update dependencies
echo "📥 의존성 패키지 확인 중..."
pip3 install -q -r requirements.txt

echo ""
echo "✓ 모든 준비가 완료되었습니다!"
echo ""
echo "🌐 웹 서버 시작 중..."
echo "   접속 주소: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""
echo "================================================"
echo ""

# Run the Flask app
cd web
python3 app.py
