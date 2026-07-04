# Gold & Silver 200 EMA Alert Bot — Deploy Guide

Sirf 3 cheezein tumhe khud leni hain (2-3 minute), baaki sab ready hai.

## Step 1 — Telegram Bot Token (1 min)
1. Telegram me `@BotFather` search karo, chat kholo
2. `/newbot` bhejo, ek naam do (jaise `MyGoldSilverBot`)
3. Wo tumhe ek TOKEN dega — copy kar lo
   (dikhega kuch aisa: `7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxx`)

## Step 2 — Chat ID (1 min)
1. Apne naye bot ko Telegram pe dhoondo, usse "Hi" bhejo
2. Browser me ye link kholo (TOKEN apna daalo):
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Usme `"chat":{"id":123456789` milega — wahi number tumhara CHAT_ID hai

## Step 3 — Twelve Data API Key (1 min, free)
1. https://twelvedata.com/ pe free signup karo
2. Dashboard khulte hi API Key dikhega — copy kar lo

## Step 4 — Deploy on Railway (free, 24/7)
1. https://railway.app pe jao, GitHub se login karo
2. Ye poora `gold-silver-bot` folder apne GitHub pe ek naye repo me upload kar do
   (GitHub.com pe "New repository" → "uploading an existing file" se seedha upload ho jayega)
3. Railway me **"New Project" → "Deploy from GitHub repo"** choose karo, apna repo select karo
4. Railway khud `requirements.txt` aur `Procfile` dekh ke sab install kar lega
5. Project ke **"Variables"** tab me ye 3 cheezein add karo:
   - `BOT_TOKEN` = tumhara token
   - `CHAT_ID` = tumhara chat id
   - `TWELVE_DATA_API_KEY` = tumhari api key
6. Save karte hi bot deploy ho jayega aur turant tumhe Telegram pe
   "✅ Bot start ho gaya hai" ka message aa jayega

Bas ho gaya — ab bot 24/7 chalega, har 5 min me Gold/Silver ka 200 EMA
cross check karega aur turant Telegram pe alert bhejega.

## Note
- Alert sirf tab aayega jab price **cross** kare (upar se neeche ya neeche se upar), har 5 min pe spam nahi karega
- Agar kabhi bot "Missing environment variables" bole to Railway ke Variables tab check karo
