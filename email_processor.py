import sqlite3
import json
import re
from datetime import datetime
from typing import Dict, Any
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DB_PATH = os.getenv("DB_PATH", "./data/email_assistant.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS processed_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        sender TEXT,
        body TEXT,
        category TEXT,
        confidence REAL,
        extracted_entities TEXT,
        draft_response TEXT,
        created_at TEXT
    )""")
    conn.commit()
    conn.close()


def classify_email(subject: str, body: str) -> Dict[str, Any]:
    prompt = f"""
    You are an AI assistant for a parking management company (GSG Parken).
    Classify the following email into one of these categories:
    - inquiry (general question)
    - complaint (customer is unhappy)
    - order (new booking/request)
    - support (technical issue)
    - invoice (payment/billing)
    - spam

    Also extract these entities if present: customer_name, phone, email, order_number, date, amount, urgency (low/medium/high).

    Respond ONLY in valid JSON format:
    {{
      "category": "...",
      "confidence": 0.0-1.0,
      "entities": {{ ... }},
      "reasoning": "short explanation"
    }}

    Email Subject: {subject}
    Email Body: {body}
    """

    if not GROQ_API_KEY:
        return {
            "category": "inquiry",
            "confidence": 0.5,
            "entities": {},
            "reasoning": "Groq API key not configured",
        }

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 500,
            },
            timeout=60,
        )
        if resp.status_code == 200:
            text = resp.json()["choices"][0]["message"]["content"]
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
    except Exception as e:
        print(f"Groq error: {e}")

    # Fallback: keyword-based classification (works without LLM)
    text = (subject + " " + body).lower()
    if any(w in text for w in ["complaint", "problem", "not working", "broken", "žalba", "problem"]):
        category = "complaint"
    elif any(w in text for w in ["order", "book", "reserve", "narudžba", "rezervacija"]):
        category = "order"
    elif any(w in text for w in ["invoice", "payment", "pay", "račun", "uplata"]):
        category = "invoice"
    elif any(w in text for w in ["support", "help", "technical", "podrška", "pomoc"]):
        category = "support"
    elif any(w in text for w in ["question", "how", "what", "pitanje", "kako"]):
        category = "inquiry"
    else:
        category = "inquiry"

    return {
        "category": category,
        "confidence": 0.6,
        "entities": {},
        "reasoning": "Fallback keyword classification",
    }


def generate_draft_response(category: str, entities: Dict) -> str:
    templates = {
        "inquiry": "Thank you for your inquiry. Our team will get back to you as soon as possible.",
        "complaint": "We apologize for the issues you experienced. We have registered your case and will contact you shortly.",
        "order": "Thank you for your order. Your request has been received and is being processed.",
        "support": "Your technical request has been received. Our support team will contact you soon.",
        "invoice": "Thank you for your payment. Your invoice has been recorded.",
        "spam": "Message marked as spam.",
    }
    return templates.get(category, "Thank you for your message.")


def process_email(subject: str, body: str, sender: str = "") -> Dict[str, Any]:
    init_db()
    result = classify_email(subject, body)
    draft = generate_draft_response(result.get("category", "inquiry"), result.get("entities", {}))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO processed_emails (subject, sender, body, category, confidence, extracted_entities, draft_response, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            subject,
            sender,
            body,
            result.get("category"),
            result.get("confidence"),
            json.dumps(result.get("entities", {})),
            draft,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    return {
        "category": result.get("category"),
        "confidence": result.get("confidence"),
        "entities": result.get("entities", {}),
        "draft_response": draft,
        "reasoning": result.get("reasoning", ""),
    }
