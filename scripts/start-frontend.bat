@echo off
echo 🎨 EmotiGift フロントエンド起動 (Windows)
echo.

cd frontend

:: node_modules の確認
if not exist node_modules (
    echo ❌ node_modules が見つかりません。先に setup.bat を実行してください。
    pause
    exit /b 1
)

echo.
echo 🎁 EmotiGift フロントエンドを起動しています...
echo    URL: http://localhost:3000
echo    停止するには Ctrl+C を押してください
echo.
echo 💡 バックエンドサーバーも起動してください: scripts\start-backend.bat
echo.

npm start