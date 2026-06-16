#!/bin/bash

echo "🎨 EmotiGift フロントエンド起動 (Mac/Linux)"
echo ""

cd frontend

# node_modules の確認
if [ ! -d node_modules ]; then
    echo "❌ node_modules が見つかりません。先に ./scripts/setup.sh を実行してください。"
    exit 1
fi

echo ""
echo "🎁 EmotiGift フロントエンドを起動しています..."
echo "   URL: http://localhost:3000"
echo "   停止するには Ctrl+C を押してください"
echo ""
echo "💡 バックエンドサーバーも起動してください: ./scripts/start-backend.sh"
echo ""

npm start