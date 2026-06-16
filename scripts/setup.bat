@echo off
echo 🎁 EmotiGift セットアップ (Windows)
echo.

:: Python のバージョンチェック
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python が見つかりません。Python 3.8以上をインストールしてください。
    echo    https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Node.js のバージョンチェック  
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js が見つかりません。Node.js 14以上をインストールしてください。
    echo    https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Python と Node.js が見つかりました
echo.

:: バックエンドのセットアップ
echo 🔧 バックエンドをセットアップ中...
cd backend

echo   - 仮想環境を作成中...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ 仮想環境の作成に失敗しました
    pause
    exit /b 1
)

echo   - 仮想環境をアクティベート中...
call venv\Scripts\activate

echo   - 依存関係をインストール中...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依存関係のインストールに失敗しました
    pause
    exit /b 1
)

echo   - 環境変数ファイルを作成中...
if not exist .env (
    copy .env.example .env
    echo     .env ファイルを作成しました
    echo     GEMINI_API_KEY を設定してください: https://makersuite.google.com/app/apikey
) else (
    echo     .env ファイルは既に存在します
)

cd ..

:: フロントエンドのセットアップ
echo.
echo 🎨 フロントエンドをセットアップ中...
cd frontend

echo   - 依存関係をインストール中...
npm install
if %errorlevel% neq 0 (
    echo ❌ npm install に失敗しました
    pause
    exit /b 1
)

cd ..

echo.
echo ✅ セットアップ完了！
echo.
echo 🚀 サーバーを起動するには:
echo    1. scripts\start-backend.bat でバックエンドを起動
echo    2. scripts\start-frontend.bat でフロントエンドを起動
echo.
echo 📝 GEMINI_API_KEY の設定を忘れずに: backend\.env
echo.
pause