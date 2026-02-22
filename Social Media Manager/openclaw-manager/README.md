# 🤖 AgentIC: Autonomous Hardware PR Manager

AgentIC is an enterprise-grade AI agent designed to automate the lifecycle of silicon design promotion. It monitors your OpenLane/GDS benchmarks, builds intelligent reports using NVIDIA's Llama-3.1-70B model, and manages social media promotion (X/Twitter) through an autonomous reasoning loop.

---

## 🚀 Features

- **🧠 Agentic Brain**: A goal-oriented reasoning loop that decides which tools to use (Extract, List, Post) based on plain-English requests.
- **🛡️ Enterprise Infrastructure**: Built on a **Flask Webhook** architecture for instant, production-ready responses.
- **🗄️ SQLite State Management**: Persistent storage for all designs, metrics, and drafts.
- **🐆 NVIDIA LLM Integration**: Uses state-of-the-art 70B models for commercial EDA correlation and tape-out readiness scoring.
- **🚇 Instant Connectivity**: Pre-configured for **ngrok** tunnels to bridge your local machine with the world.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- [ngrok](https://ngrok.com/) account (Free)
- Telegram Bot Token ([BotFather](https://t.me/botfather))
- NVIDIA API Key

### 2. Install Dependencies
```bash
pip install flask requests openai python-dotenv tweepy sqlite3
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```ini
# NVIDIA LLM
NVIDIA_API_KEY=your_key_here

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_AUTHORIZED_USER_ID=your_id

# X (Twitter)
API_KEY=...
API_SECRET=...
ACCESS_TOKEN=...
ACCESS_SECRET=...
BEARER_TOKEN=...
```

---

## 🏁 How to Run (Local Production Mode)

To run the bot properly, follow these **3 steps** in order:

### STEP 1: Launch the Tunnel
Open a new terminal and expose your local server to the internet:
```bash
ngrok http 5000
```
*Copy the Forwarding URL (e.g., `https://xxxx.ngrok-free.app`).*

### STEP 2: Configure the Webhook
In your project terminal, run the setup script with your ngrok URL:
```bash
python setup_webhook.py https://your-xxxx.ngrok-free.app
```
*You should see `{'ok': True, 'description': 'Webhook was set'}`.*

### STEP 3: Start the Agent
Launch the main bot server:
```bash
python messenger_listener.py
```

---

## 💬 How to Interact

Talk to your bot in Telegram using plain English:
- *"Show me an inventory of my projects."*
- *"Check the latest counter design and tell me if it's tape-out ready."*
- *"That report looks great, go ahead and post it to X."*
- *"What is the physical readiness score for my latest build?"*

---

## 📂 Project Structure
- `messenger_listener.py`: The main Flask server and Agentic Brain.
- `database_manager.py`: SQLite layer for persistent storage.
- `setup_webhook.py`: Helper to link Telegram to your local machine.
- `extract_metrics.py`: Scans WSL folders for hardware benchmarks.
- `config.json`: Master configuration for paths and models.
- `bot_data.db`: The persistent database (auto-generated).

---

## ⚖️ License
MIT License - Created with 💡 for the Open Source Hardware community.
