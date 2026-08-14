from google import genai
from google.genai import types
from dotenv import load_dotenv
import json
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

app = FastAPI()
history = []


class UserInputRequest(BaseModel):
    user_input: str


SYSTEM_INSTRUCTION = """
You are a helpful warehouse operations assistant.
Keep responses concise, practical, and relevant to WMS operations.
"""


@app.get("/")
async def root():
    return {"message": "Welcome to the GenAI Chatbot API!"}


@app.get("/chat-history")
def chat_history():
    return history


def _fallback_response(prompt: str) -> str:
    text = (prompt or "").lower()

    if any(word in text for word in ["hello", "hi", "hey"]):
        return "Hello. The local WMS chatbot is online and ready to help."
    if any(word in text for word in ["sku", "inventory", "stock", "how many", "quantity"]):
        return "The live Gemini service is temporarily unavailable, but the WMS app is still configured to answer stock and SKU questions from the warehouse database once the backend agent is active."
    if any(word in text for word in ["order", "shipment", "status", "pending"]):
        return "The order status workflow is available in the WMS app. This fallback response confirms the assistant is online while the external Gemini key is being corrected."
    if any(word in text for word in ["receive", "shipping", "ship", "dispatch"]):
        return "Receiving and shipping are available in the app workflow. The fallback chatbot is active until the AI service key is fixed."
    return "The local WMS assistant is active. Please use the app for live inventory and shipping actions while the external Gemini connection is being restored."


def _generate_text(prompt: str) -> str:
    if client is None:
        return _fallback_response(prompt)

    try:
        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
        text = getattr(response, "text", "") or ""
        if text:
            return text
    except Exception:
        pass

    return _fallback_response(prompt)


@app.post("/v1/chat")
async def chat(request: UserInputRequest):
    user_input = request.user_input.strip()
    history.append({"role": "user", "content": user_input})

    response_text = _generate_text(user_input)
    history.append({"role": "model", "content": response_text})
    return {"response": response_text}


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/v1/chat/stream")
async def chat_stream(request: UserInputRequest):
    user_input = request.user_input.strip()
    history.append({"role": "user", "content": user_input})

    async def event_generator():
        chunks = []
        try:
            if client is None:
                text = _fallback_response(user_input)
                chunks.append(text)
                yield sse("delta", {"text": text})
            else:
                try:
                    stream = client.models.generate_content_stream(
                        model=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
                        contents=user_input,
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
                    )

                    for chunk in stream:
                        text = getattr(chunk, "text", "") or ""
                        if text:
                            chunks.append(text)
                            yield sse("delta", {"text": text})
                except Exception:
                    text = _fallback_response(user_input)
                    chunks.append(text)
                    yield sse("delta", {"text": text})
        finally:
            full_text = "".join(chunks)
            if full_text:
                history.append({"role": "model", "content": full_text})
        yield sse("done", {"response": "".join(chunks)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        server_header=False,
    )