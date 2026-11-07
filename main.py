import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from email_processor import process_email

app = FastAPI(title="AI Email Assistant", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmailRequest(BaseModel):
    subject: str
    body: str
    sender: str = ""


class EmailResponse(BaseModel):
    category: str
    confidence: float
    entities: dict
    draft_response: str
    reasoning: str


@app.post("/process-email", response_model=EmailResponse)
def process_email_endpoint(req: EmailRequest):
    return process_email(req.subject, req.body, req.sender)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
