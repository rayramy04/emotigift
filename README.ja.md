# 🎁 EmotiGift - AIが読み解く、心に響くプレゼント

[🇬🇧 English Version / 英語版はこちら](./README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-19.1.0-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-blue.svg)](https://www.typescriptlang.org/)

## 🏆 受賞歴

**優秀賞** - [技育CAMPハッカソン2025 vol.9](https://talent.supporterz.jp/events/98b0c3d3-a5d3-4083-b11d-48b71f97fded/) (2025年8月3日)

*AIを活用したパーソナライズドギフト推薦システムの革新性と技術実装が評価されました。*

## 概要

EmotiGiftは、**SNS投稿・チャット履歴をAI分析してパーソナライズされたギフトを提案する**Webアプリケーションです。Google Gemini AIがユーザーの投稿、コメント、会話内容を深く分析し、その人の性格・興味・価値観に最適なプレゼントを見つけてくれます。

### EmotiGiftの由来
**Emotion（感情）** と **Gift（ギフト）** を組み合わせた造語です。SNSやチャットに現れる感情や個性をAIが読み取り、心に響くギフトを提案するという想いを込めました。

## デモ

**[デモ動画を見る](./emotigift-demo.mp4)** | **[プレゼンテーション資料](./emotigift-presentation.pdf)**

## 主な機能

- **マルチプラットフォーム分析**: Reddit・LINE・WhatsApp対応
- **深層チャット分析**: 会話から性格・嗜好を洞察
- **スマート推薦**: 詳細な理由付きで厳選された3つのギフト提案
- **自動相手検出**: 会話相手を自動判定、グループチャットフィルタリング
- **検索最適化**: Amazon・楽天・Yahoo!ショッピング向けキーワード最適化
- **ワンクリック購入**: 商品検索への直接リンク
- **レスポンシブデザイン**: 全デバイスでシームレスに動作

## 技術スタック

| 分野 | 技術 |
|------|------|
| **フロントエンド** | React 19.1.0 + TypeScript 4.9.5 |
| **バックエンド** | FastAPI + Python 3.8+ |
| **AI** | Google Gemini 1.5 Flash |
| **スタイリング** | CSS + Tailwind CSS |

## クイックスタート

### 必要要件
- Node.js 18+ と npm 8+
- Python 3.8+
- Google Gemini APIキー（[こちらから取得](https://makersuite.google.com/app/apikey)）

### インストール

#### Mac/Linux:
```bash
git clone https://github.com/Pepper161/supporterz-hackathon.git
cd emotigift
chmod +x scripts/*.sh && ./scripts/setup.sh
```

#### Windows:
```cmd
git clone https://github.com/Pepper161/supporterz-hackathon.git
cd emotigift
scripts\setup.bat
```

### 設定

`backend/.env`ファイルを作成:
```env
GEMINI_API_KEY=your_api_key_here
```

### アプリケーション起動

#### Mac/Linux:
```bash
# バックエンド (ターミナル1)
./scripts/start-backend.sh

# フロントエンド (ターミナル2)
./scripts/start-frontend.sh
```

#### Windows:
```cmd
# バックエンド (ターミナル1)
scripts\start-backend.bat

# フロントエンド (ターミナル2)
scripts\start-frontend.bat
```

- **フロントエンド**: http://localhost:3000
- **バックエンド**: http://localhost:8000

## 使い方

### Reddit分析
1. Redditユーザー名を入力
2. 予算と関係性を設定（任意）
3. 「分析」をクリックしてAIによるギフト推薦を取得

### チャット分析（LINE・WhatsApp）
1. チャット履歴を.txtファイルとしてエクスポート
   - **LINE**: トーク → メニュー → 「トーク履歴を送信」
   - **WhatsApp**: トーク → 設定 → 「チャットをエクスポート」（メディアなし）
2. ファイルをアップロード
3. 複数人が検出された場合は分析対象を選択
4. 予算と関係性を設定（任意）
5. パーソナライズされたギフト推薦を取得

## 開発チーム

### Pepper ([GitHub: Pepper161](https://github.com/Pepper161))
**チームリーダー・フロントエンド担当**
- プロジェクト統括とチーム管理
- React/TypeScriptフロントエンド開発
- APIアーキテクチャ設計とReddit API統合
- AIプロンプトエンジニアリング
- Vercelデプロイとビルド最適化

### Ray ([GitHub: rayramy04](https://github.com/rayramy04))
**バックエンド・システム設計担当・プレゼンター**
- プロジェクトアイデア提供・企画立案
- FastAPIバックエンドシステム設計・開発
- チャット分析機能（LINE・WhatsApp対応）実装
- 内容ベース分析システムとファイルアップロード機能
- UI/UX設計（rose統一テーマ）
- エラーハンドリングとグループチャット検出
- プロジェクト最適化とドキュメント作成
- プレゼンテーション実施

### Nenneko ([GitHub: ibukye](https://github.com/ibukye))
**インフラ・検索最適化担当**
- OAuth認証システム
- 楽天ショッピング統合とキーワード最適化
- インフラ環境設定（環境変数化、レート制限）
- AIプロンプト最適化
- プレゼンテーション資料作成

### Haruto ([GitHub: KonnoHaruto](https://github.com/KonnoHaruto))
**品質保証・設計アドバイザー**
- プロダクト品質管理とバグテスト
- システム設計アドバイスと最適化提案
- ユーザビリティ検証

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

---

⭐ **このプロジェクトが役に立った場合は、ぜひスターをお願いします！**

[![GitHub stars](https://img.shields.io/github/stars/Pepper161/supporterz-hackathon.svg?style=social&label=Star)](https://github.com/Pepper161/supporterz-hackathon)
