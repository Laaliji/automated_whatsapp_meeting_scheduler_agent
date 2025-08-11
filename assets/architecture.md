# WhatsApp RAG Scheduler Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   Twilio API     │    │   FastAPI       │
│   Messages      │───▶│   Webhook        │───▶│   Application   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenAI GPT-4  │◀───│   AI Service     │◀───│   RAG Service   │
│   Intent & NLP  │    │   Classification │    │   Context Mgmt  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Qdrant        │◀───│   Vector DB      │    │   Scheduler     │
│   Vector Store  │    │   Conversation   │    │   Service       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Google        │◀───│   Calendar       │    │   Todoist       │
│   Calendar API  │    │   Service        │    │   Service       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SQLite/       │◀───│   Database       │    │   User Auth     │
│   PostgreSQL    │    │   Models         │    │   OAuth Flow    │
└─────────────────┘    └──────────────────┘    └─────────────────┘

Data Flow:
1. WhatsApp Message → Twilio Webhook → FastAPI
2. RAG Service → Retrieve Context → Qdrant Vector DB
3. AI Service → Process Intent → OpenAI GPT-4
4. Scheduler Service → Create Events → Google Calendar
5. Scheduler Service → Create Tasks → Todoist
6. Store Context → Vector DB & Database
7. Response → WhatsApp via Twilio
```

## Key Components

### 1. Message Processing Layer

- **Twilio WhatsApp API**: Handles incoming/outgoing messages
- **FastAPI Webhooks**: Processes webhook requests
- **Request Validation**: Ensures message authenticity

### 2. AI & RAG Layer

- **OpenAI GPT-4**: Natural language understanding
- **RAG Service**: Context retrieval and enhancement
- **Qdrant Vector DB**: Stores conversation embeddings
- **Intent Classification**: Determines user actions

### 3. Integration Layer

- **Google Calendar Service**: Event management
- **Todoist Service**: Task creation and management
- **OAuth Authentication**: Secure API access

### 4. Data Layer

- **SQLite/PostgreSQL**: User data and meeting records
- **Vector Database**: Conversation context storage
- **Session Management**: User state tracking

## Security Features

- OAuth 2.0 for Google and Todoist
- Twilio request validation
- Environment variable configuration
- Secure token storage

## Scalability

- Async/await for concurrent processing
- Vector database for fast context retrieval
- Modular service architecture
- Database connection pooling
