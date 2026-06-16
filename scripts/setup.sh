#!/bin/bash

echo "🎁 EmotiGift セットアップ (Mac/Linux)"
echo ""

# Python のバージョンチェック
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python が見つかりません。Python 3.10以上をインストールしてください。"
    echo "   https://www.python.org/downloads/"
    exit 1
fi

PYTHON_CMD=""
for candidate in python3 python; do
    if command -v "$candidate" &> /dev/null && "$candidate" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"; then
        PYTHON_CMD="$candidate"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python 3.10以上が必要です。"
    python3 --version 2>/dev/null || python --version 2>/dev/null
    exit 1
fi

# Node.js のバージョンチェック
if ! command -v node &> /dev/null; then
    echo "❌ Node.js が見つかりません。Node.js 18以上をインストールしてください。"
    echo "   https://nodejs.org/"
    exit 1
fi

if ! node -e "process.exit(Number(process.versions.node.split('.')[0]) >= 18 ? 0 : 1)"; then
    echo "❌ Node.js 18以上が必要です。"
    echo "   現在のバージョン: $(node --version)"
    exit 1
fi

echo "✅ Python と Node.js が見つかりました"
echo ""

# バックエンドのセットアップ
echo "🔧 バックエンドをセットアップ中..."
cd backend

echo "  - 仮想環境を作成中..."
"$PYTHON_CMD" -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ 仮想環境の作成に失敗しました"
    exit 1
fi

echo "  - 仮想環境をアクティベート中..."
source venv/bin/activate

echo "  - 依存関係をインストール中..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依存関係のインストールに失敗しました"
    exit 1
fi

echo "  - 環境変数ファイルを作成中..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "    .env ファイルを作成しました"
    echo "    GEMINI_API_KEY を設定してください: https://makersuite.google.com/app/apikey"
else
    echo "    .env ファイルは既に存在します"
fi

cd ..

# フロントエンドのセットアップ
echo ""
echo "🎨 フロントエンドをセットアップ中..."
cd frontend

echo "  - 依存関係をインストール中..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ npm install に失敗しました"
    exit 1
fi

cd ..

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "🚀 サーバーを起動するには:"
echo "   1. ./scripts/start-backend.sh でバックエンドを起動"
echo "   2. ./scripts/start-frontend.sh でフロントエンドを起動"
echo ""
echo "📝 GEMINI_API_KEY の設定を忘れずに: backend/.env"
echo ""
