# AI Email Automation Assistant (Groq verzija — spremna za web)

## Poslovni problem
Parkirna kompanija prima desтки e-poruka dnevno: upiti, žalbe, narudžbe, fakture. Rukovanje ručno traje sate i dovodi do zaboravljenih poruka.

## Rješenje
Python + FastAPI servis koji:
- Klasifikira ulaznu e-poštu (inquiry, complaint, order, support, invoice, spam)
- Izvlači entitete: ime klijenta, telefon, broj narudžbe, datum, iznos, hitnost
- Generiše AI draft odgovor koji se može poslati jednim klikom
- Čuva sve u SQLite bazi za kasnije pretraživanje i analizu

## Tehnologije
- Python 3.11+
- FastAPI (REST API)
- SQLite (baza podataka)
- **Groq API** (LLM u oblaku — **besplatan nivel**)
- python-dotenv, requests

## Kako pokrenuti lokalno

1. Preuzmi **Groq API ključ** na [groq.com](https://groq.com) (API Keys → Create API Key)
2. U ovom folderu:
   ```powershell
   pip install -r requirements.txt
   copy .env.example .env
   ```
3. Otvori `.env` i upiši svoj Groq ključ:
   ```
   GROQ_API_KEY=sk-tvoj-ključ-iz-groq-a
   ```
4. Pokreni server:
   ```powershell
   python main.py
   ```
5. Otvori `http://localhost:8000/docs` za testiranje API-ja

## Kako postaviti na web (Render + Vercel)

### Backend na Render.com (besplatan)
1. Otvori [render.com](https://render.com) i kreiraj nalog
2. **New → Web Service** → poveži svoj GitHub repozitorij `ai-email-assistant`
3. Build command: `pip install -r requirements.txt`
4. Start command: `python main.py`
5. U **Environment Variables** dodaj:
   - `GROQ_API_KEY` = tvoj ključ sa groq.com
6. Deploy — dobićeš URL tipo `https://ai-email-assistant.onrender.com`

### Frontend na Vercel/Netlify
1. Otvori `frontend.html` u uređivaču teksta
2. Pronađi liniju: `const API_BASE_URL = 'http://localhost:8000';`
3. Zamijeni sa svojim Render URL: `const API_BASE_URL = 'https://tvoj-sajt.onrender.com';`
4. Otvori `frontend.html` u pregledniku — radi bez instaliranja ničeg

## Primjer zahteva
```json
POST /process-email
{
  "subject": "Narudžba za parkiranje",
  "body": "Zdravo, ja sam Marko Perić, telefon 061 123 456. Hoću rezervisati mjesto zajutrom.",
  "sender": "marko@example.com"
}
```

## Primjer odgovora
```json
{
  "category": "order",
  "confidence": 0.92,
  "entities": {
    "customer_name": "Marko Perić",
    "phone": "061 123 456",
    "order_number": null,
    "date": null,
    "urgency": "medium"
  },
  "draft_response": "Hvala na narudžbeci. Vaš zahtjev je prihvćen i obrađen.",
  "reasoning": "LLM classification"
}
```

## GitHub
github.com/AfanKulaglic/ai-email-assistant
