# 🍽️ Cooker-Lens

![Python](https://img.shields.io/badge/Python-3.11-red?logo=python)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)
![OpenAI](https://img.shields.io/badge/OpenAI-API-green?logo=openai)
![Mealie](https://img.shields.io/badge/Mealie-io-orange?logo=mealie)

---

## 🚀 Overview

**Cooker-Lens** is an **AI-powered Telegram bot** that automates recipe creation in Mealie from cooking videos.
Just send a TikTok link (Instagram coming soon) and the bot will:

- Download and transcribe the video.
- Extract key process images.
- Analyze and summarize content using OpenAI.
- Generate metadata and title suggestions.
- Automatically publish the recipe to [Mealie](https://mealie.io).

---

## ✨ Features

| Feature                 | Description                                                          |
|-------------------------|----------------------------------------------------------------------|
| 🎥 Video Download       | Downloads videos from TikTok (Instagram coming soon)                 |
| 📝 Speech-to-Text       | Transcribes audio to text using Vosk                                 |
| 🖼️ Frame Extraction    | Extracts key images from the video                                   |
| 🤖 AI Analysis          | Uses OpenAI to structure recipe, metadata, and select the best image |
| 🍲 Recipe Publishing    | Publishes the recipe to Mealie via API                               |
| 💬 Telegram Integration | Interacts with users via Telegram bot                                |
| 💸 Cost Estimation      | Shows OpenAI token usage and cost breakdown                          |

---

## 🛠️ Tech Stack

- **Python 3.11**
- **Docker**
- **Telegram Bot API**
- **OpenAI API**
- **Vosk (Speech Recognition)**
- **Pillow (Image Processing)**
- **pyktok (TikTok Downloading)**

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/plleopart/cooker-lens
cd mealie-ai-bot
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
TEMP_BASE_DIR=/tmp/mealie
ALLOWED_MEDIA_ORIGINS_LIST=instagram,tiktok
FFMPEG_PATH=/usr/bin/ffmpeg
VOSK_MODEL_DIR=/models/vosk
AI_PROMPT_DIR=/app/prompts/recipe_prompt.txt
OPENAI_API_KEY=your_openai_api_key
AI_MODEL=gpt-4o-mini
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=4096
MEALIER_URL=https://api.mealie.com
MEALIER_API_KEY=your_mealie_api_key
INPUT_TOKENS_PRICE_PER_MILLION=0.001
OUTPUT_TOKENS_PRICE_PER_MILLION=0.002
MEALIER_DEFAULT_CATEGORIES_ID=123,456
AI_INPUT_IMAGES=4
PYKTOK_BROWSER=firefox
AI_CONFIDENCE_THRESHOLD=8
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_MASTER_ID=0
TELEGRAM_WHITE_LIST=
TELEGRAM_BLACK_LIST=
```

---

### 🧩 Environment Variables Explained

| Variable                          | Description                                                                  |
|-----------------------------------|------------------------------------------------------------------------------|
| `TEMP_BASE_DIR`                   | Temporary directory for downloaded and processed files.                      |
| `ALLOWED_MEDIA_ORIGINS_LIST`      | Allowed media origins for downloads (e.g., `instagram,tiktok`).              |
| `FFMPEG_PATH`                     | Path to the ffmpeg executable for video processing.                          |
| `VOSK_MODEL_DIR`                  | Path to the Vosk model directory for audio transcription.                    |
| `AI_PROMPT_DIR`                   | Path to the AI prompt file.                                                  |
| `OPENAI_API_KEY`                  | OpenAI API key for AI access.                                                |
| `AI_MODEL`                        | OpenAI model to use (e.g., `gpt-4o-mini`).                                   |
| `AI_TEMPERATURE`                  | Temperature for AI text generation (controls creativity).                    |
| `AI_MAX_TOKENS`                   | Maximum tokens allowed in the AI response.                                   |
| `MEALIER_URL`                     | Base URL for the Mealie API.                                                 |
| `MEALIER_API_KEY`                 | API key for authenticating requests to Mealie.                               |
| `INPUT_TOKENS_PRICE_PER_MILLION`  | Estimated cost per million input tokens for OpenAI (USD).                    |
| `OUTPUT_TOKENS_PRICE_PER_MILLION` | Estimated cost per million output tokens for OpenAI (USD).                   |
| `MEALIER_DEFAULT_CATEGORIES_ID`   | Default category IDs for recipes in Mealie (comma-separated).                |
| `AI_INPUT_IMAGES`                 | Number of images to send to the AI for analysis.                             |
| `PYKTOK_BROWSER`                  | Browser to use with pyktok for TikTok downloads (`firefox` recommended).     |
| `AI_CONFIDENCE_THRESHOLD`         | Minimum confidence threshold to accept AI results.                           |
| `TELEGRAM_BOT_TOKEN`              | Telegram bot token.                                                          |
| `TELEGRAM_MASTER_ID`              | Telegram master (admin) user ID (`0` to disable).                            |
| `TELEGRAM_WHITE_LIST`             | Comma-separated whitelist of allowed Telegram user IDs (empty to allow all). |
| `TELEGRAM_BLACK_LIST`             | Comma-separated blacklist of blocked Telegram user IDs.                      |

---

### 3. Build and Run with Docker and Docker Compose

### 🐳 Docker

```bash
docker build -t mealie-ai-bot .
docker run --env-file .env -v $(pwd)/models:/models mealie-ai-bot
```

### 🐳 Docker Compose

You can run the bot easily using Docker Compose. Example `docker-compose.yml`:

```yaml
version: '3.8'
services:
  mealie-ai-bot:
    build: .
    env_file:
      - .env
    volumes:
      - ./models:/models
      - ./app/sources:/app/sources
      - ./app/sources/temp:/app/sources/temp
      - ./app/sources/vosk-model-es-0.42:/app/sources/vosk
    restart: unless-stopped
    command: python run.py
```

**Steps:**

1. Make sure your `.env` file is configured.
2. Run:
   ```bash
   docker compose up --build
   ```

This will start the bot with all necessary volumes for media and speech model processing.

---

### 4. Start the Bot (Without Docker)

Make sure you have Python 3.11 and all dependencies:

```bash
pip install -r requirements.txt
python run.py
```

---

## 🤖 Usage

1. **Start a chat** with your Telegram bot.
2. **Send a TikTok video link**.
3. The bot will:
    - Download and process the video.
    - Transcribe and analyze the content.
    - Suggest a title and show AI cost.
    - Publish the recipe to Mealie.
    - Reply with the recipe link.

---

## 📝 Project Structure

```
app/
  ├── ai/                # AI client and prompt handling
  ├── api/               # Mealie API integration
  ├── bot/               # Telegram bot logic
  ├── config.py          # Configuration and env variables
  ├── controller/        # Main process controller
  ├── downloader/        # Video downloaders
  ├── media/             # Media processing (audio, images)
  └── garbage/           # Temporary file cleanup
run.py                   # Entry point
requirements.txt
Dockerfile
.env.example
```

---

## 🧑‍💻 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT License

---

## 🌐 Links

- [Mealie](https://mealie.com)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [OpenAI API](https://platform.openai.com/docs/api-reference)

---

Made with ❤️ for food lovers and developers!

