<p align="center">
  <img src="assets/hero.png" alt="Organizze Bot" width="500">
</p>

# Organizze Telegram Bot

A Telegram bot that integrates with [Organizze](https://organizze.com.br) personal finance app, powered by Google Gemini AI. Ask questions about your finances in natural language and get instant responses with charts and insights.

## Features

- **Natural Language Queries**: Ask anything about your finances in Portuguese
- **AI-Powered Responses**: Uses Google Gemini to understand and respond to questions
- **Visual Charts**: Generate pie charts, bar charts, and summary visualizations
- **Quick Commands**: Pre-built shortcuts for common queries
- **Secure**: Whitelist-based access control via Chat ID

---

## Quick Start

<details>
<summary><strong>1. Prerequisites</strong></summary>

- Python 3.11+
- A Telegram Bot (created via [@BotFather](https://t.me/botfather))
- Organizze account with API access
- Google Gemini API key
- A cloud platform account (GCP, AWS, Azure, etc.) or local server

</details>

<details>
<summary><strong>2. Get Your API Keys</strong></summary>

### Telegram Bot Token
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the prompts
3. Save the bot token provided

### Organizze API Key
1. Log in to [Organizze](https://app.organizze.com.br)
2. Go to **Configurações** → **API**
3. Generate and copy your API key
4. Note your account email

### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### Your Telegram Chat ID
1. Message your bot or [@userinfobot](https://t.me/userinfobot)
2. The bot will reply with your Chat ID
3. Use this to whitelist yourself

</details>

<details>
<summary><strong>3. Environment Variables</strong></summary>

The application requires the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_TOKEN` | Bot token from BotFather | `123456789:ABCdefGHI...` |
| `ORGANIZZE_EMAIL` | Your Organizze account email | `user@example.com` |
| `ORGANIZZE_API_KEY` | Organizze API key | `abc123def456...` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `ALLOWED_CHAT_IDS` | Comma-separated list of authorized Telegram Chat IDs | `123456789,987654321` |

### Local Development (.env file)

```bash
# .env
TELEGRAM_TOKEN=your_telegram_bot_token
ORGANIZZE_EMAIL=your_organizze_email
ORGANIZZE_API_KEY=your_organizze_api_key
GEMINI_API_KEY=your_gemini_api_key
ALLOWED_CHAT_IDS=your_chat_id
```

</details>

<details>
<summary><strong>4. Easy Deploy (Recommended for Beginners)</strong></summary>

The easiest way to deploy this bot is using **Railway** or **Render** - no technical knowledge required!

### Option A: Deploy on Railway (Recommended)

1. **Create a Railway account**
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account

2. **Deploy from GitHub**
   - Click "New Project" -> "Deploy from GitHub repo"
   - Select this repository: `arturovaine/telegram-bot-organizze`
   - Railway will automatically detect the Dockerfile

3. **Add your environment variables**
   - Go to your project -> "Variables" tab
   - Click "New Variable" and add each one:
     ```
     TELEGRAM_TOKEN = your_bot_token_here
     ORGANIZZE_EMAIL = your_email_here
     ORGANIZZE_API_KEY = your_api_key_here
     GEMINI_API_KEY = your_gemini_key_here
     ALLOWED_CHAT_IDS = your_chat_id_here
     ```

4. **Get your bot URL**
   - Go to "Settings" -> "Networking" -> "Generate Domain"
   - Copy the URL (looks like: `https://your-app.up.railway.app`)

5. **Connect Telegram to your bot**
   - Open this link in your browser (replace the values):
     ```
     https://api.telegram.org/bot<YOUR_TELEGRAM_TOKEN>/setWebhook?url=<YOUR_RAILWAY_URL>
     ```
   - You should see: `{"ok":true,"result":true,"description":"Webhook was set"}`

6. **Done!** Message your bot on Telegram to test it.

### Option B: Deploy on Render

1. **Create a Render account**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create a new Web Service**
   - Click "New" -> "Web Service"
   - Connect your GitHub and select this repository
   - Choose "Docker" as the environment

3. **Configure the service**
   - Name: `organizze-bot`
   - Region: Choose closest to you
   - Plan: Free (or Starter for better performance)

4. **Add environment variables**
   - Scroll to "Environment Variables"
   - Add the same 5 variables as listed above

5. **Deploy and get URL**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)
   - Copy your URL from the dashboard

6. **Set Telegram webhook** (same as Railway step 5)

### Troubleshooting

- **Bot not responding?** Check if your Chat ID is correct in `ALLOWED_CHAT_IDS`
- **Error 401?** Your Organizze API key might be wrong
- **Webhook error?** Make sure the URL ends without a trailing slash

</details>

---

## Deployment (Advanced)

<details>
<summary><strong>Google Cloud Run</strong></summary>

### Using Secret Manager (Recommended)

1. **Create secrets:**
```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create secrets
echo -n "your_telegram_token" | gcloud secrets create TELEGRAM_TOKEN --data-file=-
echo -n "your_email" | gcloud secrets create ORGANIZZE_EMAIL --data-file=-
echo -n "your_api_key" | gcloud secrets create ORGANIZZE_API_KEY --data-file=-
echo -n "your_gemini_key" | gcloud secrets create GEMINI_API_KEY --data-file=-
echo -n "your_chat_id" | gcloud secrets create ALLOWED_CHAT_IDS --data-file=-
```

2. **Grant permissions:**
```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

3. **Deploy:**
```bash
gcloud run deploy organizze-bot \
  --source . \
  --region YOUR_REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-secrets="TELEGRAM_TOKEN=TELEGRAM_TOKEN:latest,ORGANIZZE_EMAIL=ORGANIZZE_EMAIL:latest,ORGANIZZE_API_KEY=ORGANIZZE_API_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest,ALLOWED_CHAT_IDS=ALLOWED_CHAT_IDS:latest"
```

4. **Set Telegram webhook:**
```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_CLOUD_RUN_URL>&drop_pending_updates=true"
```

</details>

<details>
<summary><strong>AWS (Lambda + API Gateway)</strong></summary>

1. **Create a Lambda function** with Python 3.11 runtime

2. **Package dependencies:**
```bash
pip install -r requirements.txt -t package/
cp main.py package/
cd package && zip -r ../function.zip .
```

3. **Upload** `function.zip` to Lambda

4. **Set environment variables** in Lambda configuration

5. **Create API Gateway** trigger (HTTP API)

6. **Set Telegram webhook** to your API Gateway URL

</details>

<details>
<summary><strong>Azure (Container Apps)</strong></summary>

1. **Build and push container:**
```bash
az acr build --registry YOUR_REGISTRY --image organizze-bot:latest .
```

2. **Deploy Container App:**
```bash
az containerapp create \
  --name organizze-bot \
  --resource-group YOUR_RG \
  --image YOUR_REGISTRY.azurecr.io/organizze-bot:latest \
  --target-port 8080 \
  --ingress external \
  --secrets telegram-token=YOUR_TOKEN organizze-email=YOUR_EMAIL ... \
  --env-vars TELEGRAM_TOKEN=secretref:telegram-token ...
```

3. **Set Telegram webhook** to your Container App URL

</details>

<details>
<summary><strong>Docker (Self-hosted)</strong></summary>

1. **Build the image:**
```bash
docker build -t organizze-bot .
```

2. **Run with environment variables:**
```bash
docker run -d \
  -p 8080:8080 \
  -e TELEGRAM_TOKEN=your_token \
  -e ORGANIZZE_EMAIL=your_email \
  -e ORGANIZZE_API_KEY=your_api_key \
  -e GEMINI_API_KEY=your_gemini_key \
  -e ALLOWED_CHAT_IDS=your_chat_id \
  --name organizze-bot \
  organizze-bot
```

3. **Set up reverse proxy** (nginx/caddy) with HTTPS

4. **Set Telegram webhook** to your server URL

</details>

<details>
<summary><strong>Railway / Render / Fly.io</strong></summary>

1. **Connect your repository** to the platform

2. **Configure environment variables** in the platform dashboard

3. **Deploy** and copy the provided URL

4. **Set Telegram webhook:**
```bash
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<YOUR_URL>"
```

</details>

---

## Usage

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start`, `/help` | Show help menu with all commands |
| `/gastos_categoria` | Pie chart of expenses by category |
| `/gastos_diarios` | Bar chart of daily expenses |
| `/resumo_visual` | Summary chart (income vs expenses vs balance) |
| `/saldo` | Total balance across all accounts |
| `/extrato` | Recent transactions |
| `/resumo` | Monthly financial summary |
| `/cartoes` | Credit cards information |

### Natural Language Examples

- "Qual meu saldo total?"
- "Quanto gastei esse mês?"
- "Quanto gastei com alimentação?"
- "Quais foram minhas últimas transações?"
- "Mostra um gráfico dos meus gastos"
- "Quanto tenho na conta Nubank?"

---

## Project Structure

```
telegram-bot-organizze/
├── Dockerfile          # Container configuration
├── main.py             # Application code
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Telegram   │────▶│   Webhook   │────▶│    Bot      │
│    User     │◀────│  (HTTPS)    │◀────│  Server     │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
             ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
             │  Organizze  │          │   Gemini    │          │ Matplotlib  │
             │    API      │          │     AI      │          │   Charts    │
             └─────────────┘          └─────────────┘          └─────────────┘
```

---

## Security Considerations

<details>
<summary><strong>Best Practices</strong></summary>

- **Never commit secrets** to version control
- **Use secret managers** (GCP Secret Manager, AWS Secrets Manager, Azure Key Vault)
- **Whitelist Chat IDs** to restrict access to authorized users only
- **Enable HTTPS** for webhook endpoints (required by Telegram)
- **Rotate API keys** periodically
- **Monitor logs** for unauthorized access attempts

</details>

---

## Troubleshooting

<details>
<summary><strong>Bot not responding</strong></summary>

1. Check webhook is set correctly:
```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

2. Verify your Chat ID is in `ALLOWED_CHAT_IDS`

3. Check application logs for errors

</details>

<details>
<summary><strong>Charts not generating</strong></summary>

1. Ensure `matplotlib` is installed
2. Check if there are transactions in the current month
3. Verify Organizze API credentials are correct

</details>

<details>
<summary><strong>Pending updates flooding</strong></summary>

Reset webhook with `drop_pending_updates`:
```bash
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook?drop_pending_updates=true"
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<YOUR_URL>&drop_pending_updates=true"
```

</details>

<details>
<summary><strong>Permission errors on GCP</strong></summary>

Grant necessary IAM roles:
```bash
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format='value(projectNumber)')

# For Secret Manager
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# For Cloud Build
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

</details>

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Acknowledgments

- [Organizze](https://organizze.com.br) for the personal finance API
- [Google Gemini](https://deepmind.google/technologies/gemini/) for AI capabilities
- [python-telegram-bot](https://python-telegram-bot.org/) community for documentation
