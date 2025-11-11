
# 💞 Telegram Matchmaking Bot (Webhook Edition)

A **flirty and fun matchmaking bot** built with **Python & python-telegram-bot v20+**.
This bot lets users create profiles, find potential matches, and chat anonymously — all within Telegram!

It’s designed for **webhook-based deployments**, meaning Telegram **pushes updates** directly to your bot server instead of polling. This makes it **faster, more scalable, and production-ready**.

---

## 🚀 Features

* 💬 Step-by-step **profile setup** (name, age, gender, bio, preferences, location)
* 💘 **Matchmaking engine** that connects users with compatible profiles
* 🔥 **Anonymous chat** with reveal & end options
* 💾 In-memory data storage (simple but easy to extend to SQLite or Redis)
* ⚡ Uses **webhooks** for real-time updates (no polling required)
* 🌐 Ready for deployment on **Render, Heroku, or Vercel**

---

## 🧩 Tech Stack

* **Language:** Python 3.9+
* **Framework:** [python-telegram-bot v20+](https://docs.python-telegram-bot.org/en/stable/)
* **Webhook Server:** Built-in (Flask-free, powered by PTB)
* **Hosting:** Render, Heroku, or any HTTPS-enabled service
* **Optional:** ngrok for local HTTPS tunneling

---

## 🧠 How It Works

1. User runs `/start`
2. Bot collects name, age, gender, bio, and preferences
3. Bot finds potential matches based on gender & preference
4. User can start a chat anonymously
5. During chat, either can:

   * `/reveal` → show identity and bio
   * `/end` → end the chat and return to matchmaking

---

## 🛠️ Installation & Setup

### 1. Clone this repo

```bash
git clone https://github.com/samuel-0228/telegram-matchmaking-bot.git
cd telegram-matchmaking-bot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install python-telegram-bot==20.6
```

### 4. Set environment variables

Create a `.env` file or export manually:

```bash
export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
export WEBHOOK_URL="https://yourdomain.com"   # or ngrok URL for testing
export PORT=10000
```

---

## 🌐 Webhook Setup

Telegram bots require a **public HTTPS endpoint** for webhooks.

### Option 1: Local Testing with ngrok

1. Run ngrok:

   ```bash
   ngrok http 10000
   ```
2. Copy the public HTTPS URL it gives you (e.g., `https://abcd1234.ngrok.io`)
3. Set it as your webhook:

   ```bash
   curl -F "url=https://abcd1234.ngrok.io/bot" https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
   ```

### Option 2: Deploy to Render / Heroku / Vercel

1. Add environment variables in your dashboard:

   * `BOT_TOKEN`
   * `WEBHOOK_URL` (your app’s public HTTPS domain)
   * `PORT` (Render uses port `10000` by default)
2. Deploy `bot.py` as your main entrypoint.
3. The bot will automatically set up the webhook.

---

## 🧾 Commands

| Command   | Description                        |
| --------- | ---------------------------------- |
| `/start`  | Start profile registration         |
| `/cancel` | Cancel registration                |
| `/end`    | End current chat                   |
| `/reveal` | Reveal your identity to your match |

---

## 🧰 Folder Structure

```
telegram-matchmaking-bot/
│
├── bot.py                 # Main bot script (webhook-based)
├── requirements.txt        # Dependencies (optional)
├── README.md              # This file 😎
└── .env                   # Your secret keys (not committed)
```

---

## 🧠 Example Match Flow

```
User A → /start → fills profile
User B → /start → fills profile
Bot → Finds A and B as compatible
A clicks “Chat with B” → Anonymous chat starts
A and B exchange messages
A → /reveal → shares real identity
B → /end → ends chat
```

---

## ⚙️ Extending the Bot

You can enhance this bot by:

* 🗄 Adding a database (SQLite, Firebase, Redis)
* 💌 Enabling photo-based profiles
* 🧮 Smarter matchmaking (e.g., shared interests)
* 🧠 Using persistent storage for chat history

---

## 🪶 Logging & Debugging

Logs are enabled by default:

```
2025-11-10 12:35:00 - telegram.ext._application - INFO - Bot initialized
2025-11-10 12:35:05 - root - INFO - Received message from user 12345
```

To view logs on Render:

```
$ render logs
```

---

## 🛡️ Security Notes

* Always store your `BOT_TOKEN` in environment variables — **never** hardcode it.
* Use HTTPS for webhook URLs (Telegram rejects plain HTTP).
* Avoid using in-memory storage for production; use a persistent DB.

---

## 🧑‍💻 Author

**Naod S.**
💌 Telegram Bots • Data Science • Automation
GitHub: [@yourusername](https://github.com/yourusername)

---

## 📄 License

MIT License © 2025 Samuel.


