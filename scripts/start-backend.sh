#!/bin/bash

echo "🚀 EmotiGift バックエンド起動 (Mac/Linux)"
echo ""

cd backend

# 仮想環境のアクティベート
if [ ! -f venv/bin/activate ]; then
    echo "❌ 仮想環境が見つかりません。先に ./scripts/setup.sh を実行してください。"
    exit 1
fi

echo "🔧 仮想環境をアクティベート中..."
source venv/bin/activate

# .env ファイルの確認
if [ ! -f .env ]; then
    echo "❌ .env ファイルが見つかりません。"
    echo "   .env.example を .env にコピーして、GEMINI_API_KEY を設定してください。"
    exit 1
fi

echo "🔍 GEMINI_API_KEY を確認中..."
if ! grep -q "GEMINI_API_KEY=" .env; then
    echo "⚠️  GEMINI_API_KEY が設定されていない可能性があります。"
    echo "   .env ファイルを確認してください。"
fi

echo ""
echo "🎁 EmotiGift バックエンドサーバーを起動しています..."
echo "   URL: http://localhost:8000"
echo "   停止するには Ctrl+C を押してください"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000