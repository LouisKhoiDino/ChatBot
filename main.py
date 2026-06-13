from openai import OpenAI
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. Đọc cấu hình từ .env ---
load_dotenv()

PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "model": "gemini-2.5-flash",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "model": "deepseek/deepseek-r1:free",
    },
}

provider = os.getenv("PROVIDER", "groq")
if provider not in PROVIDERS:
    sys.exit(f"Provider không hợp lệ: {provider}")

cfg = PROVIDERS[provider]
api_key = os.getenv(cfg["api_key_env"])
if not api_key:
    sys.exit(f"Thiếu API key. Hãy đặt {cfg['api_key_env']} trong .env")

# --- 2. Tạo client gọi API ---
client = OpenAI(base_url=cfg["base_url"], api_key=api_key)

# --- 3. Lịch sử hội thoại ---
messages = [
    {"role": "system", "content": "Bạn là trợ lý AI thân thiện. Trả lời ngắn gọn, dùng tiếng Việt."}
]

# --- 4. Vòng lặp chat ---
print(f"Chatbot AI ({provider} / {cfg['model']}). Gõ 'quit' để thoát.\n")

while True:
    user_input = input("Bạn: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ("quit", "exit"):
        print("Tạm biệt!")
        break

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=cfg["model"],
            messages=messages,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print(f"\nBot: {reply}\n")
    except Exception as e:
        print(f"\n[Lỗi] {e}\n")
        messages.pop()            