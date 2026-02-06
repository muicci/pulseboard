# PulseBoard - Autonomous Business Signal Intelligence

PulseBoard is a real-time business intelligence platform that captures, processes, and delivers actionable signals from multiple sources.

## Architecture

- **Backend**: FastAPI server with PostgreSQL for signal tracking, events, and email management
- **Dashboard**: Glassmorphism dark-theme web UI for real-time monitoring
- **Browser Automation**: Playwright-based Gmail and Calendar scraping
- **Telegram Bot**: Command interface for signal management
- **Chrome Extension**: Quick signal capture from any webpage
- **Video**: Remotion-rendered pitch video (1080p, 30fps)

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/muicci/pulseboard.git
cd pulseboard

# 2. Copy environment variables
cp .env.example .env
# Edit .env with your actual credentials

# 3. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn asyncpg python-telegram-bot httpx playwright

# 4. Start the backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 18880

# 5. Open the dashboard
# Open dashboard/index.html in your browser
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /signals | List all signals |
| POST | /signals | Create a new signal |
| GET | /events | List all events |
| POST | /events | Create a new event |
| GET | /emails | List all emails |
| GET | /dashboard-data | Aggregated dashboard data |

## Project Structure

```
pulseboard/
├── backend/
│   ├── server.py              # FastAPI backend
│   ├── telegram_bot.py        # Telegram bot
│   └── browser_automation.py  # Gmail/Calendar automation
├── dashboard/
│   ├── index.html             # Web dashboard
│   ├── style.css              # Glassmorphism theme
│   └── app.js                 # Dashboard logic
├── extension/
│   ├── manifest.json          # Chrome MV3 manifest
│   ├── background.js          # Service worker
│   ├── content.js             # Content script
│   └── popup.html             # Extension popup
├── docs/
│   └── n8n-workflow.json      # n8n automation workflow
├── screenshots/               # Browser automation captures
├── video/                     # Remotion pitch video
├── .env.example               # Environment template
└── README.md                  # This file
```

## License

MIT
