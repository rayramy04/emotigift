@echo off
echo 🚀 EmotiGift バックエンド起動 (Windows)
echo.

cd backend

:: 仮想環境のアクティベート
if not exist venv\Scripts\activate.bat (
    echo ❌ 仮想環境が見つかりません。先に setup.bat を実行してください。
    pause
    exit /b 1
)

echo 🔧 仮想環境をアクティベート中...
call venv\Scripts\activate

:: .env ファイルの確認
if not exist .env (
    echo ❌ .env ファイルが見つかりません。
    echo    .env.example を .env にコピーして、GEMINI_API_KEY を設定してください。
    pause
    exit /b 1
)

echo 🔍 GEMINI_API_KEY を確認中...
findstr /C:"GEMINI_API_KEY=" .env >nul
if %errorlevel% neq 0 (
    echo ⚠️  GEMINI_API_KEY が設定されていない可能性があります。
    echo    .env ファイルを確認してください。
)

echo.
echo 🎁 EmotiGift バックエンドサーバーを起動しています...
echo    URL: http://localhost:8000
echo    停止するには Ctrl+C を押してください
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000