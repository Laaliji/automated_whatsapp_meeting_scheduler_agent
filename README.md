# WhatsApp RAG Scheduler 🤖📅

An intelligent AI-powered meeting scheduling assistant that works through WhatsApp messages. It automatically creates Google Calendar events and Todoist tasks using natural language processing and RAG (Retrieval-Augmented Generation) for contextual understanding.

## ✨ Features

### Core Functionality

- **Natural Language Processing**: Understands meeting requests in conversational language
- **Google Calendar Integration**: Automatically creates calendar events
- **Todoist Integration**: Creates task reminders for meeting days
- **WhatsApp Interface**: Works through familiar WhatsApp messaging
- **RAG Context**: Remembers conversation history and user preferences

### AI Capabilities

- **Intent Classification**: Understands schedule, cancel, reschedule, and info requests
- **Smart Extraction**: Pulls dates, times, locations, and participants from messages
- **Contextual Responses**: Uses conversation history for personalized interactions
- **Meeting Type Detection**: Distinguishes between virtual and in-person meetings

### Integrations

- **Twilio WhatsApp API**: Handles incoming/outgoing messages
- **Google Calendar API**: Creates, updates, and deletes events
- **Todoist API**: Manages task reminders
- **Qdrant Vector DB**: Stores conversation context for RAG
- **OpenAI GPT-4**: Powers natural language understanding

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Twilio account with WhatsApp sandbox
- Google Cloud project with Calendar API
- Todoist account
- Qdrant vector database (optional, for RAG features)

### Installation

1. **Clone and setup**:

   ```bash
   # Linux/macOS
   git clone <your-repo>
   cd whatsapp-scheduler
   python setup.py

   # Windows (Command Prompt)
   git clone <your-repo>
   cd whatsapp-scheduler
   python setup.py

   # Windows (PowerShell)
   git clone <your-repo>
   Set-Location whatsapp-scheduler
   python setup.py
   ```

2. **Configure environment**:

   ```bash
   # Linux/macOS
   cp .env.example .env
   # Edit .env with your API keys

   # Windows (Command Prompt)
   copy .env.example .env
   # Edit .env with your API keys

   # Windows (PowerShell)
   Copy-Item .env.example .env
   # Edit .env with your API keys
   ```

3. **Start Qdrant (optional, for RAG features)**:

   ```bash
   # All platforms (with Docker)
   docker run -p 6333:6333 qdrant/qdrant
   ```

4. **Run the application**:

   ```bash
   # Linux/macOS
   source venv/bin/activate
   uvicorn app.main:app --reload

   # Windows (Command Prompt)
   venv\Scripts\activate
   uvicorn app.main:app --reload

   # Windows (PowerShell)
   venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload
   ```

## 🔧 Configuration

### Environment Variables

The application uses environment variables for configuration. A `.env` file is created during setup with placeholder values. You need to update it with your actual API keys and credentials:

- **OpenAI API Key**: For natural language processing
- **Twilio Credentials**: For WhatsApp integration
- **Google OAuth**: For Calendar API access
- **Todoist OAuth**: For task management
- **Database URLs**: For data storage
- **App Settings**: Security and debug configuration

**Important**: Never commit your `.env` file to version control as it contains sensitive credentials.

### Twilio Webhook Setup

1. In your Twilio Console, configure the WhatsApp webhook URL:

   ```
   https://your-domain.com/api/v1/webhook/whatsapp
   ```

2. For local development, use ngrok:
   ```bash
   # All platforms
   ngrok http 8000
   # Use the https URL for webhook
   ```

## 🔐 Authentication Setup

### Google Calendar Authentication

1. Visit: `http://localhost:8000/api/v1/auth/google?phone=YOUR_PHONE_NUMBER`
2. Complete OAuth flow
3. Calendar integration will be active

### Todoist Authentication

1. Visit: `http://localhost:8000/api/v1/auth/todoist?phone=YOUR_PHONE_NUMBER`
2. Complete OAuth flow
3. Task creation will be active

## 💬 Usage Examples

### Scheduling Meetings

```
"Schedule a meeting with John tomorrow at 3pm"
"Let's meet Friday at 2:30 PM at the office"
"Book a virtual call with the team next Tuesday 10am"
"Schedule lunch meeting at Cafe Central on Monday 1pm"
```

### Managing Meetings

```
"Cancel my meeting with Sarah"
"Reschedule tomorrow's meeting to Thursday"
"What meetings do I have this week?"
"Move my 3pm meeting to 4pm"
```

### Meeting Types

- **Virtual meetings**: "virtual call", "zoom meeting", "online meeting"
- **In-person meetings**: "at the office", "lunch meeting", specific addresses
- **Auto-detection**: The AI determines type based on context

## 🏗️ Architecture

![Architecture Diagram](/app/assets/Charte graphique.png)

### Core Components

```
app/
├── api/
│   ├── webhooks.py      # WhatsApp message handling
│   └── auth.py          # OAuth flows
├── services/
│   ├── ai_service.py    # OpenAI integration
│   ├── rag_service.py   # RAG context management
│   ├── calendar_service.py  # Google Calendar
│   ├── todoist_service.py   # Todoist integration
│   └── scheduler.py     # Meeting orchestration
├── models/
│   └── database.py      # SQLAlchemy models
└── core/
    └── config.py        # Configuration management
```

### Data Flow

1. **WhatsApp Message** → Twilio Webhook → FastAPI
2. **RAG Enhancement** → Retrieve Context → Qdrant Vector DB
3. **AI Processing** → Extract Intent → OpenAI GPT-4
4. **Calendar Creation** → Google Calendar API
5. **Task Creation** → Todoist API
6. **Context Storage** → Vector DB & Database
7. **Response** → WhatsApp via Twilio

## 💬 Usage Examples

Send natural language messages to your WhatsApp number:

- "Schedule a meeting tomorrow at 3pm"
- "Cancel my meeting with John"
- "What meetings do I have this week?"
- "Book a virtual call Friday 2pm"
- "Reschedule my Monday meeting to Tuesday"

## 🛠️ Development

### Running Tests

```bash
# Linux/macOS
pytest tests/

# Windows (Command Prompt)
pytest tests/

# Windows (PowerShell)
pytest tests/
```

### Database Migrations

```bash
# Linux/macOS
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Windows (Command Prompt)
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Windows (PowerShell)
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 🚀 Deployment

### Production Setup

- Use PostgreSQL instead of SQLite for better performance
- Deploy Qdrant on a server or use Qdrant Cloud
- Set up proper SSL certificates for HTTPS
- Use environment-specific configurations
- Set up monitoring and logging
- Configure proper backup strategies

### Docker Deployment

```bash
# Build image
docker build -t whatsapp-scheduler .

# Run with docker-compose
docker-compose up -d
```

## 📁 Project Structure

For detailed architecture information, see [Architecture Documentation](assets/architecture.md).

## 📝 License

MIT License - see LICENSE file for details
