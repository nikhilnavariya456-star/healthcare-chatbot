from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from groq import Groq
from starlette.middleware.sessions import SessionMiddleware

# 🔐 Auth imports
from auth_google import router as google_auth_router
from auth_local import router as local_auth_router
from auth_otp import router as otp_auth_router
from auth_utils import get_current_user

from prompt import SYSTEM_PROMPT
from models import User

# --------------------------------------------------
# App setup
# --------------------------------------------------

load_dotenv()

app = FastAPI(
    title="Healthcare Chatbot",
    version="1.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("JWT_SECRET_KEY")
)

# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(local_auth_router)
app.include_router(google_auth_router)
app.include_router(otp_auth_router)

# --------------------------------------------------
# Static & Templates
# --------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --------------------------------------------------
# AI Client
# --------------------------------------------------

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --------------------------------------------------
# In-memory chat storage
# --------------------------------------------------

chat_memory: dict[str, list] = {}
MAX_HISTORY = 10

# --------------------------------------------------
# Models
# --------------------------------------------------

class ChatRequest(BaseModel):
    user_message: str

# --------------------------------------------------
# Pages
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.get("/verify-otp", response_class=HTMLResponse)
def verify_otp_page(request: Request, email: str):
    return templates.TemplateResponse(
        "verify_otp.html",
        {"request": request, "email": email}
    )


@app.get("/local-login", response_class=HTMLResponse)
def local_login_page(request: Request):
    return templates.TemplateResponse(
        "local_login.html",
        {"request": request}
    )


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@app.get("/chat-ui", response_class=HTMLResponse)
def chat_ui(
    request: Request,
    user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "user": user}
    )


@app.api_route("/logout", methods=["GET", "POST"])
def logout(request: Request):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    request.session.clear()  # ✅ Google session clear
    return response

# --------------------------------------------------
# Chat API (SECURED)
# --------------------------------------------------

@app.post("/chat")
def chat(
    req: ChatRequest,
    user: User = Depends(get_current_user)
):
    email = user.email
    history = chat_memory.setdefault(email, [])

    user_message = req.user_message.strip()
    if not user_message:
        return {"response": "Please enter a health-related question."}

    non_health_keywords = {
        "code", "programming", "python", "java", "html", "css",
        "math", "history", "politics", "movie", "song", "game",
        "exam", "ai", "chatgpt", "technology"
    }

    if any(word in user_message.lower() for word in non_health_keywords):
        return {
            "response": (
                "I’m a healthcare-specific assistant and can only answer "
                "medical and health-related questions.\n\n"
                "This information is for educational purposes only."
            )
        }

    history.append({"role": "user", "content": user_message})
    chat_memory[email] = history[-MAX_HISTORY:]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *chat_memory[email]
    ]

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2,
        )
        answer = res.choices[0].message.content.strip()
    except Exception:
        answer = "Something went wrong. Please try again later."

    history.append({"role": "assistant", "content": answer})
    return {"response": answer}
