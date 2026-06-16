# 🎁 EmotiGift - AI-Powered Personalized Gift Recommendations

[🇯🇵 日本語版はこちら / Japanese Version](./README.ja.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-19.1.0-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-blue.svg)](https://www.typescriptlang.org/)

## 🏆 Awards

**Excellence Award** - [Geek Camp Hackathon 2025 vol.9](https://talent.supporterz.jp/events/98b0c3d3-a5d3-4083-b11d-48b71f97fded/) (August 3, 2025)

*Recognized for innovation and technical implementation of AI-powered personalized gift recommendation system.*

## Overview

EmotiGift is an **AI-powered web application that analyzes SNS posts and chat history to suggest personalized gifts**. Using Google Gemini AI, it deeply analyzes user posts, comments, and conversations to discover gifts perfectly matched to their personality, interests, and values.

### About the Name
A combination of **Emotion** and **Gift** - embodying our vision of using AI to read emotions and personalities expressed in SNS and chats, suggesting gifts that truly resonate with the recipient.

## Demo

**[Watch Demo Video](./emotigift-demo.mp4)** | **[View Presentation](./emotigift-presentation.pdf)**

## Key Features

- **Multi-Platform Analysis**: Reddit, LINE, WhatsApp support
- **Deep Chat Analysis**: Personality and preference insights from conversations
- **Smart Recommendations**: 3 carefully curated gift suggestions with detailed reasoning
- **Automatic Recipient Detection**: Auto-detects conversation partners with group chat filtering
- **Search Optimization**: Keywords optimized for Amazon, Rakuten, Yahoo! Shopping
- **One-Click Purchase**: Direct links to product searches
- **Responsive Design**: Works seamlessly on all devices

## Tech Stack

| Category | Technology |
|----------|------------|
| **Frontend** | React 19.1.0 + TypeScript 4.9.5 |
| **Backend** | FastAPI + Python 3.10+ |
| **AI** | Google Gemini 1.5 Flash |
| **Styling** | CSS + Tailwind CSS |

## Quick Start

### Prerequisites
- Node.js 18+ and npm 8+
- Python 3.10+
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

#### Mac/Linux:
```bash
git clone https://github.com/Pepper161/supporterz-hackathon.git emotigift
cd emotigift
chmod +x scripts/*.sh && ./scripts/setup.sh
```

#### Windows:
```cmd
git clone https://github.com/Pepper161/supporterz-hackathon.git emotigift
cd emotigift
scripts\setup.bat
```

### Configuration

Create `backend/.env` file:
```env
GEMINI_API_KEY=your_api_key_here
```

### Running the Application

#### Mac/Linux:
```bash
# Backend (Terminal 1)
./scripts/start-backend.sh

# Frontend (Terminal 2)
./scripts/start-frontend.sh
```

#### Windows:
```cmd
# Backend (Terminal 1)
scripts\start-backend.bat

# Frontend (Terminal 2)
scripts\start-frontend.bat
```

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

## Usage

### Reddit Analysis
1. Enter Reddit username
2. Set budget and relationship (optional)
3. Click "Analyze" to get AI-powered gift recommendations

### Chat Analysis (LINE/WhatsApp)
1. Export chat history as .txt file
   - **LINE**: Chat → Menu → "Send chat history"
   - **WhatsApp**: Chat → Settings → "Export chat" (without media)
2. Upload the file
3. Select analysis target if multiple people are detected
4. Set budget and relationship (optional)
5. Get personalized gift recommendations

## Development Team

### Pepper ([GitHub: Pepper161](https://github.com/Pepper161))
**Team Leader & Frontend Lead**
- Project coordination and team management
- React/TypeScript frontend development
- API architecture design and Reddit API integration
- AI prompt engineering
- Vercel deployment and build optimization

### Ray ([GitHub: rayramy04](https://github.com/rayramy04))
**Backend & System Design Lead & Presenter**
- Project ideation and planning
- FastAPI backend system design and development
- Chat analysis features (LINE & WhatsApp support)
- Content-based analysis system and file upload functionality
- UI/UX design (rose unified theme)
- Error handling and group chat detection
- Project optimization and documentation
- Presentation delivery

### Nenneko ([GitHub: ibukye](https://github.com/ibukye))
**Infrastructure & Search Optimization Lead**
- OAuth authentication system
- Rakuten Shopping integration and keyword optimization
- Infrastructure setup (environment variables, rate limiting)
- AI prompt optimization
- Presentation materials

### Haruto ([GitHub: KonnoHaruto](https://github.com/KonnoHaruto))
**Quality Assurance & Design Advisor**
- Product quality management and bug testing
- System design advice and optimization proposals
- Usability verification

## License

MIT License - See [LICENSE](LICENSE) file for details

---

⭐ **If this project helped you, please give us a star!**

[![GitHub stars](https://img.shields.io/github/stars/Pepper161/supporterz-hackathon.svg?style=social&label=Star)](https://github.com/Pepper161/supporterz-hackathon)
