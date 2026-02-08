# Project Architecture

## 📁 Project Structure

```
telegram-bot-organizze/
│
├── 🚀 main.py                      # Flask app & webhook handler (260 lines)
│   ├── Health check endpoint (GET /)
│   ├── Telegram webhook handler (POST /)
│   ├── Financial data aggregation
│   └── Request routing & error handling
│
├── 🔌 organizze_client.py          # Complete API client (700+ lines)
│   ├── OrganizzeClient class
│   ├── HTTP methods (GET, POST, PUT, DELETE)
│   ├── Error handling (401, 422, timeouts)
│   ├── 31 API endpoints implemented:
│   │   ├── Users (1 endpoint)
│   │   ├── Bank Accounts (5 endpoints)
│   │   ├── Categories (5 endpoints)
│   │   ├── Credit Cards (5 endpoints)
│   │   ├── Credit Card Invoices (3 endpoints)
│   │   ├── Transactions (6 endpoints)
│   │   ├── Transfers (5 endpoints)
│   │   └── Budgets (1 endpoint)
│   └── Automatic cents ↔ reais conversion
│
├── 🤖 ai_assistant.py              # Gemini AI integration (150 lines)
│   ├── GeminiAssistant class
│   ├── Natural language processing
│   ├── Chart command extraction
│   ├── Action command detection
│   └── Response cleaning utilities
│
├── 💬 telegram_bot.py              # Telegram utilities (200 lines)
│   ├── TelegramBot class
│   │   ├── send_message() - Text messages
│   │   ├── send_photo() - Image messages
│   │   ├── send_chat_action() - Typing indicator
│   │   └── Auto message splitting (>4096 chars)
│   ├── AuthManager class
│   │   ├── is_authorized() - Chat ID validation
│   │   ├── add_chat_id() - Add user
│   │   └── remove_chat_id() - Remove user
│   └── Command definitions (QUICK_COMMANDS)
│
├── 📊 charts.py                    # Chart generation (250 lines)
│   ├── generate_pie_chart() - Expenses by category
│   ├── generate_bar_chart() - Daily spending
│   ├── generate_summary_chart() - Income vs Expenses vs Balance
│   ├── generate_budget_progress_chart() - Budget tracking
│   ├── generate_invoice_history_chart() - Invoice trends
│   └── generate_month_comparison_chart() - Month-over-month
│
├── 📦 models.py                    # Data models (200 lines)
│   ├── Pydantic models for validation:
│   │   ├── User
│   │   ├── Account
│   │   ├── Category
│   │   ├── CreditCard
│   │   ├── Invoice
│   │   ├── Transaction
│   │   ├── Transfer
│   │   ├── Budget
│   │   └── FinancialSummary
│   └── Automatic type conversion & validation
│
├── 🧪 test_api.py                  # Testing suite (150 lines)
│   ├── test_basic_endpoints() - Read operations
│   ├── test_write_operations() - Create/Update/Delete
│   └── Comprehensive API validation
│
├── 📋 requirements.txt             # Python dependencies
│   ├── flask==3.0.0
│   ├── requests==2.31.0
│   ├── gunicorn==21.2.0
│   ├── google-generativeai==0.8.0
│   ├── matplotlib==3.8.2
│   └── pydantic==2.5.3
│
├── 🐳 Dockerfile                   # Container definition
│   ├── Python 3.11-slim base
│   ├── Gunicorn server (1 worker, 8 threads)
│   └── Port 8080
│
├── 📖 Documentation
│   ├── README.md                   # Main documentation
│   ├── API_DOCUMENTATION.md        # Complete API reference (1000+ lines)
│   ├── IMPLEMENTATION_SUMMARY.md   # Implementation details
│   └── ARCHITECTURE.md             # This file
│
└── 🖼️  assets/
    ├── hero.png                    # README hero image
    └── bot-screenshot.png          # Bot interface screenshot
```

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Telegram User                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTPS Webhook
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                     Cloud Run (GCP)                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    main.py (Flask)                     │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │         Webhook Handler (POST /)                 │ │  │
│  │  └──────────────────┬───────────────────────────────┘ │  │
│  └────────────────────┼───────────────────────────────────┘  │
│                       │                                       │
│       ┌───────────────┼───────────────┐                      │
│       │               │               │                       │
│       ▼               ▼               ▼                       │
│  ┌─────────┐   ┌──────────┐   ┌─────────────┐              │
│  │ Telegram│   │   AI     │   │  Organizze  │              │
│  │   Bot   │   │Assistant │   │   Client    │              │
│  └────┬────┘   └────┬─────┘   └──────┬──────┘              │
│       │             │                 │                       │
│       │             │                 │                       │
│  ┌────▼─────┐  ┌───▼─────┐      ┌───▼────────┐             │
│  │ send_    │  │ Gemini  │      │ Organizze  │             │
│  │ message()│  │ 2.0     │      │ API v2     │             │
│  │ send_    │  │ Flash   │      │ (REST)     │             │
│  │ photo()  │  │         │      │            │             │
│  └──────────┘  └─────────┘      └────────────┘             │
│       │                                │                      │
│       │             Charts             │                      │
│       │          ┌─────────┐           │                      │
│       └──────────┤ charts  ├───────────┘                      │
│                  │  .py    │                                  │
│                  └─────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow

### User sends message: "Quanto gastei com alimentação?"

```
1. Telegram → Cloud Run Webhook (POST /)
   ├── Extract: chat_id, message text

2. main.py: webhook()
   ├── AuthManager.is_authorized(chat_id) ✓
   ├── TelegramBot.send_chat_action('typing')
   │
   ├── get_financial_context()
   │   ├── OrganizzeClient.get_accounts()
   │   ├── OrganizzeClient.get_transactions(start_date, end_date)
   │   ├── OrganizzeClient.get_credit_cards()
   │   ├── OrganizzeClient.get_categories()
   │   └── OrganizzeClient.get_budgets(year, month)
   │   └── Returns: financial_data dict
   │
   ├── GeminiAssistant.ask(user_message, financial_data)
   │   ├── Build context prompt
   │   ├── Call Gemini API
   │   └── Returns: AI response with optional [CHART:*] commands
   │
   ├── Extract chart command (if any)
   │   ├── ai.extract_chart_command(response)
   │   └── If chart requested:
   │       ├── charts.generate_*_chart(data)
   │       └── TelegramBot.send_photo(chart_bytes)
   │   └── Else:
   │       └── TelegramBot.send_message(response_text)
   │
   └── Return 'OK' to Telegram
```

---

## 🧱 Module Dependencies

```
main.py
  ├── organizze_client
  │   └── requests
  ├── ai_assistant
  │   └── google.generativeai
  ├── telegram_bot
  │   └── requests
  ├── charts
  │   └── matplotlib
  └── models
      └── pydantic

test_api.py
  └── organizze_client
```

---

## 🔐 Environment Variables

```bash
# Required for production
TELEGRAM_TOKEN       # Bot token from @BotFather
ORGANIZZE_EMAIL      # Organizze account email
ORGANIZZE_API_KEY    # API key from Organizze settings
GEMINI_API_KEY       # Google AI Studio API key
ALLOWED_CHAT_IDS     # Comma-separated chat IDs (e.g., "123,456")

# Optional
PORT                 # Server port (default: 8080)
```

---

## 📊 Data Flow

### Financial Data Aggregation

```python
get_financial_context() returns:
{
  "today": "08/02/2026",
  "month": "fevereiro",
  "year": 2026,
  "accounts": [
    {"id": 123, "name": "Nubank", "balance": 1500.00, ...}
  ],
  "totalBalance": 5000.00,
  "income": 7000.00,
  "expenses": 3500.00,
  "balance": 3500.00,
  "recentTransactions": [...],  # Last 15
  "allTransactions": [...],     # All for month
  "creditCards": [...],
  "budgets": [...],
  "categories": [...]
}
```

This data is passed to:
1. **Gemini AI** - For natural language understanding
2. **Charts** - For visualization
3. **Telegram** - For display

---

## 🎯 Design Principles

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- `organizze_client.py` - API communication only
- `ai_assistant.py` - AI processing only
- `telegram_bot.py` - Telegram communication only
- `charts.py` - Visualization only
- `main.py` - Routing & orchestration only

### 2. **Error Handling**
Every external call is wrapped in try-except:
- API errors → Custom exceptions
- Network timeouts → Graceful fallback
- Validation errors → User-friendly messages
- Logging → Full traceback for debugging

### 3. **Type Safety**
Pydantic models ensure:
- Correct data types
- Required fields present
- Automatic conversion (cents ↔ reais)
- Runtime validation

### 4. **Testability**
Each module can be tested independently:
- `test_api.py` - Tests API client
- Mock services for unit testing
- Integration tests possible

### 5. **Extensibility**
Easy to add new features:
- New commands → Add to `QUICK_COMMANDS`
- New charts → Add function to `charts.py`
- New endpoints → Add method to `OrganizzeClient`
- New models → Add class to `models.py`

---

## 🚀 Deployment Architecture

### Cloud Run Setup

```
GCP Project: organizze-479321
Region: southamerica-east1 (São Paulo)

Service: organizze-bot
├── Container: Python 3.11 + Gunicorn
├── Resources:
│   ├── CPU: 1 vCPU
│   ├── Memory: 512 MB
│   ├── Timeout: 300s
│   └── Concurrency: 80
├── Scaling:
│   ├── Min instances: 0
│   ├── Max instances: 20
│   └── Startup probe: TCP 8080 (240s)
├── Secrets (from Secret Manager):
│   ├── TELEGRAM_TOKEN
│   ├── ORGANIZZE_EMAIL
│   ├── ORGANIZZE_API_KEY
│   ├── GEMINI_API_KEY
│   └── ALLOWED_CHAT_IDS
└── Access: Public (allow-unauthenticated)

URL: https://organizze-bot-638700698980.southamerica-east1.run.app
```

---

## 📈 Scalability

### Current Capacity

- **Concurrent users**: 80 per instance × 20 instances = 1,600
- **Requests/second**: ~50-100 (depending on complexity)
- **API rate limits**: No official limits (be respectful)

### Bottlenecks & Solutions

| Bottleneck | Solution |
|------------|----------|
| Organizze API calls | ✅ Add Redis caching layer |
| Gemini API latency | ✅ Stream responses, show typing indicator |
| Chart generation | ✅ Cache common charts (daily, monthly summaries) |
| Cold starts | ✅ Use min instances = 1 (costs ~$15/month) |

---

## 🛡️ Security Layers

```
Layer 1: GCP Secret Manager
  └── All credentials encrypted at rest

Layer 2: Chat ID Whitelist
  └── Only authorized users can access bot

Layer 3: HTTPS Only
  └── All communication encrypted in transit

Layer 4: Error Sanitization
  └── No sensitive data in logs or error messages

Layer 5: Input Validation
  └── Pydantic validates all data structures
```

---

## 📊 Monitoring

### Recommended Metrics

```bash
# Request logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=organizze-bot"

# Error rate
gcloud monitoring metrics-explorer --project=organizze-479321 \
  --metric="run.googleapis.com/request_count" \
  --filter="response_code_class>=400"

# Latency
gcloud monitoring metrics-explorer --project=organizze-479321 \
  --metric="run.googleapis.com/request_latencies"

# Active instances
gcloud monitoring metrics-explorer --project=organizze-479321 \
  --metric="run.googleapis.com/container/instance_count"
```

---

## 🔮 Future Architecture

### Planned Enhancements

1. **Redis Caching Layer**
   ```
   Cloud Run → Redis (Memorystore) → Organizze API
   ```

2. **Pub/Sub for Async Operations**
   ```
   Bot → Pub/Sub → Cloud Function → Long operation
   ```

3. **Cloud Scheduler for Notifications**
   ```
   Scheduler → Cloud Function → Check budgets → Notify users
   ```

4. **Firestore for User Preferences**
   ```
   Bot → Firestore → Store: favorite accounts, notification settings
   ```

---

## 📚 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Organizze API Docs](https://github.com/organizze/api-doc)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)

---

**Last Updated**: February 8, 2026
**Architecture Version**: 2.0
**Total Lines of Code**: 3,568
