import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from database import create_document, get_documents, db
from schemas import Demolead, Demotranscript

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# ------------------------
# Demo receptionist endpoints
# ------------------------

class DemoStartRequest(BaseModel):
    name: str = Field(..., min_length=1)
    company: Optional[str] = None
    lang: Literal['en', 'fr'] = 'en'

class DemoStartResponse(BaseModel):
    session_id: str
    greeting: str

@app.post("/demo/start", response_model=DemoStartResponse)
async def demo_start(payload: DemoStartRequest):
    session_id = uuid.uuid4().hex[:12]
    # store an initial system message as transcript doc
    greeting = (
        "Bonjour! Ici Cliqo, votre réceptionniste virtuelle. Comment puis‑je vous aider aujourd’hui?"
        if payload.lang == 'fr'
        else "Hi! This is Cliqo, your AI receptionist. How can I help you today?"
    )
    # persist a lead entry
    lead = Demolead(name=payload.name, email=f"{session_id}@demo.local", company=payload.company or "Demo", message="Started demo", lang=payload.lang, source='demo')
    try:
        create_document('demolead', lead)
        create_document('demotranscript', {
            'session_id': session_id,
            'role': 'assistant',
            'text': greeting,
            'lang': payload.lang
        })
    except Exception:
        # continue even if DB not configured
        pass
    return DemoStartResponse(session_id=session_id, greeting=greeting)

class DemoMessageRequest(BaseModel):
    session_id: str = Field(..., min_length=8)
    text: str = Field(..., min_length=1)
    lang: Literal['en', 'fr'] = 'en'

class DemoMessageResponse(BaseModel):
    reply: str
    suggestions: List[str]

@app.post("/demo/message", response_model=DemoMessageResponse)
async def demo_message(payload: DemoMessageRequest):
    # Simple rule-based receptionist behavior for demo purposes
    user = payload.text.lower()

    if payload.lang == 'fr':
        if any(k in user for k in ["rendez-vous", "rdv", "planifier", "calendrier", "disponibil"]):
            reply = "Je peux planifier un rendez‑vous pour vous. Quelle date et heure préférez‑vous?"
            suggestions = ["Demain 14h", "Vendredi matin", "Semaine prochaine"]
        elif any(k in user for k in ["prix", "tarif", "coût"]):
            reply = "Nos forfaits commencent à partir du plan Démarrage et s’adaptent à votre volume d’appels. Voulez‑vous que je vous envoie la grille tarifaire?"
            suggestions = ["Envoyer les tarifs", "Parler à un agent", "Comparer les plans"]
        elif any(k in user for k in ["humain", "agent", "représentant"]):
            reply = "Je peux vous mettre en relation avec un membre de l’équipe. Préférez‑vous être rappelé ou discuter par courriel?"
            suggestions = ["Être rappelé", "Courriel", "Planifier un appel"]
        elif any(k in user for k in ["intégration", "google", "outlook", "slack", "zapier", "twilio"]):
            reply = "Cliqo s’intègre à Google Calendar, Outlook, Slack, Zapier, Twilio et plus encore. Souhaitez‑vous une intégration spécifique?"
            suggestions = ["Google Calendar", "Slack", "Zapier"]
        else:
            reply = "Je peux aider avec la planification, le routage d’appels, et les intégrations. Dites‑moi ce que vous souhaitez faire."
            suggestions = ["Planifier un rendez‑vous", "Voir les tarifs", "Parler à un humain"]
    else:
        if any(k in user for k in ["appointment", "book", "schedule", "calendar", "availability"]):
            reply = "I can schedule an appointment for you. What date and time works best?"
            suggestions = ["Tomorrow 2pm", "Friday morning", "Next week"]
        elif any(k in user for k in ["price", "pricing", "cost"]):
            reply = "Our plans start at Starter and scale with your call volume. Would you like me to send pricing?"
            suggestions = ["Send pricing", "Talk to an agent", "Compare plans"]
        elif any(k in user for k in ["human", "agent", "representative"]):
            reply = "I can connect you with our team. Would you prefer a callback or email?"
            suggestions = ["Request callback", "Email", "Schedule a call"]
        elif any(k in user for k in ["integration", "google", "outlook", "slack", "zapier", "twilio"]):
            reply = "Cliqo integrates with Google Calendar, Outlook, Slack, Zapier, Twilio, and more. Any specific integration in mind?"
            suggestions = ["Google Calendar", "Slack", "Zapier"]
        else:
            reply = "I can help with scheduling, call routing, and integrations. Tell me what you’d like to do."
            suggestions = ["Book appointment", "See pricing", "Talk to a human"]

    # persist transcript if DB available
    try:
        create_document('demotranscript', {
            'session_id': payload.session_id,
            'role': 'user',
            'text': payload.text,
            'lang': payload.lang
        })
        create_document('demotranscript', {
            'session_id': payload.session_id,
            'role': 'assistant',
            'text': reply,
            'lang': payload.lang
        })
    except Exception:
        pass

    return DemoMessageResponse(reply=reply, suggestions=suggestions)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
