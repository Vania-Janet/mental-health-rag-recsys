# Calma AI - Mental Health Voice Assistant 🍃🧘

## Demo

> **Live Demo:** [Coming Soon]
> 
> **Video Demo:** [Add your demo video here]

---

## Overview

Calma AI is an intelligent voice assistant designed to provide empathetic mental health support through conversational AI. The system combines ElevenLabs voice technology with RAG (Retrieval-Augmented Generation) to deliver personalized specialist recommendations and evidence-based mental health guidance.

**Key Features:**
- Real-time voice interaction with crisis detection
- Semantic search for mental health specialists in CDMX
- Context-aware recommendations based on symptoms, budget, and location
- Emergency response system with immediate intervention protocols
- Knowledge base with evidence-based mental health information

## Architecture

### Backend (Python/Flask)
- **Framework:** Flask with Gunicorn WSGI server
- **Vector Search:** FAISS with OpenAI embeddings (text-embedding-3-small)
- **Crisis Detection:** Multi-level keyword-based system (Critical, High, Normal)
- **Response Time:** < 500ms for warm requests

### Frontend (Next.js/TypeScript)
- **Framework:** Next.js 14+ with App Router
- **UI Components:** shadcn/ui with Radix UI primitives
- **State Management:** React hooks with localStorage persistence
- **Voice Integration:** ElevenLabs Conversational AI Widget

### Deployment
- **Backend:** Render (Python 3.12, auto-scaling)
- **Frontend:** Vercel (recommended) or Render
- **Database:** JSON-based with FAISS vector indexes

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- OpenAI API key
- ElevenLabs API key (for voice features)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/Vania-Janet/mental-health-rag-recsys.git
cd mental-health-rag-recsys

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
echo "OPENAI_API_KEY=your_key_here" > .env

# Run development server
python api_rest.py
```

### Frontend Setup

```bash
cd calma-ai-voice-assistant

# Install dependencies
npm install

# Run development server
npm run dev
```

Visit `http://localhost:3000` to see the application.

## API Endpoints

### Health Check
```http
GET /health
```

### Search Specialists
```http
POST /buscar_especialista
Content-Type: application/json

{
  "sintoma": "ansiedad",
  "genero": "femenino",
  "presupuesto": "bajo",
  "ubicacion": "Benito Juárez"
}
```

### Query Knowledge Base
```http
POST /consultar_guia_medica
Content-Type: application/json

{
  "consulta": "¿Qué hago si tengo un ataque de pánico?"
}
```

## Project Structure

```
├── api_rest.py                 # Flask API server
├── retrieval_system.py         # Specialist search with FAISS
├── knowledge_rag.py            # Knowledge base RAG system
├── render.yaml                 # Render deployment config
├── requirements.txt            # Python dependencies
├── faiss_recursos/             # Specialist vector indexes
├── faiss_pasos/                # Knowledge base indexes
└── calma-ai-voice-assistant/   # Next.js frontend
    ├── app/                    # App router pages
    ├── components/             # React components
    └── lib/                    # Utilities and integrations
```

## Deployment

### Deploy Backend to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Add environment variable: `OPENAI_API_KEY`
5. Render auto-detects `render.yaml` and deploys

### Deploy Frontend to Vercel

```bash
cd calma-ai-voice-assistant
npx vercel --prod
```

## Crisis Response System

Calma AI implements a three-tier crisis detection system:

- **Critical:** Immediate intervention for suicidal ideation or self-harm
- **High:** Urgent support for panic attacks or severe distress
- **Normal:** Standard empathetic guidance and specialist referrals

All crisis responses include direct contact information for emergency services (Línea de la Vida: 800-911-2000).

## Technology Stack

**Backend:**
- Flask 2.3+
- OpenAI API (embeddings)
- FAISS (vector similarity search)
- Gunicorn (production server)

**Frontend:**
- Next.js 14
- TypeScript
- Tailwind CSS
- Radix UI / shadcn/ui

**Voice AI:**
- ElevenLabs Conversational AI

## Legal Notice

This application provides informational support only and does not replace professional medical advice. Users experiencing mental health emergencies should contact emergency services immediately.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a pull request.

## Contact

**Repository:** [github.com/Vania-Janet/mental-health-rag-recsys](https://github.com/Vania-Janet/mental-health-rag-recsys)

---

Built with care for mental health support in Mexico City.
