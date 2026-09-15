# Telegram Broker Client-Tracking Bot

Broker team ke liye bot — client details save karo, company se mile number
client ko bhejo, proof save karo, aur har member ka daily/total count track karo.

## Commands
- `/start` — bot shuru karo
- `/newclient` — naya client add karo (naam + phone)
- `/addnumber <client_id> <number>` — company se mile numaindey ka number save karo
- `/proof <client_id>` — proof bhejo (photo ya text)
- `/myclients` — apne pending clients dekho
- `/mystats` — apna aaj ka aur total count dekho
- `/teamstats` — (sirf admin) sabka count ek saath dekho

## Step 1: Local par setup (test karne ke liye)

1. Python 3.10+ install hona chahiye.
2. Terminal mein project folder kholo:
   ```
   pip install -r requirements.txt
   ```
3. `.env.example` ko copy karke `.env` naam se save karo:
   ```
   cp .env.example .env
   ```
4. `.env` file kholo aur ye fill karo:
   - `BOT_TOKEN` — BotFather se mila token
   - `ADMIN_IDS` — aapki Telegram user ID (comma se alag multiple ho sakti hain)

   Apni Telegram user ID jaanne ke liye Telegram par `@userinfobot` ko message karo.

5. Bot chalao:
   ```
   python bot.py
   ```

## Step 2: GitHub par upload karna

1. GitHub par naya repository banao (Private rakhna better hai, kyunki business data hai).
2. Terminal mein:
   ```
   cd telegram-broker-bot
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<aapka-username>/<repo-naam>.git
   git push -u origin main
   ```

   **Zaroori:** `.env` file kabhi upload mat karo — usmein aapka bot token hai.
   `.gitignore` file already `.env` ko exclude karti hai, isliye ye automatically upload nahi hogi.

## Step 3: Bot ko 24x7 chalana (free hosting)

Aapke computer/phone ko hamesha on rakhna practical nahi hai, isliye free hosting use karo:

**Railway.app (sabse aasan):**
1. [railway.app](https://railway.app) par GitHub account se login karo
2. "New Project" → "Deploy from GitHub repo" → apna repo select karo
3. "Variables" tab mein `BOT_TOKEN` aur `ADMIN_IDS` add karo (jo `.env` mein the)
4. Deploy ho jayega, bot 24x7 chalta rahega

**Render.com** bhi isi tarah free tier deta hai — "New Background Worker" banake GitHub repo connect karo aur environment variables set karo.

## Data kahan store hota hai?

Sab data `broker_bot.db` (SQLite file) mein save hota hai — ye file automatically
bot chalne par ban jati hai. Isko backup lena ho toh ye file copy kar lo.

## Notes
- Har broker apna client sirf khud dekh/manage kar sakta hai (`broker_id` se alag).
- Jab `/addnumber` use karoge, number sirf aapko wapas bot mein dikhega taaki aap
  copy karke client ko manually bhej sako (WhatsApp/call se).
- `/proof` ke baad hi us client ka count `/mystats` aur `/teamstats` mein jud'ta hai.
