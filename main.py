import os
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


clear_terminal()
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
        "model": "openrouter/free",
    },
}

provider = os.getenv("PROVIDER", "groq")
if provider not in PROVIDERS:
    sys.exit(f"Provider không hợp lệ: {provider}")

cfg = PROVIDERS[provider]
api_key = os.getenv(cfg["api_key_env"])
if not api_key:
    sys.exit(f"Thiếu API key. Hãy đặt {cfg['api_key_env']} trong .env")

client = OpenAI(base_url=cfg["base_url"], api_key=api_key)

# Lưu trữ tin nhắn hệ thống gốc để dùng lại khi reset
system_message = {
    "role": "system",
    "content": "Bạn là trợ lý AI thân thiện. Trả lời ngắn gọn, dùng tiếng anh.",
}
messages = [system_message]

print(f"Chatbot AI ({provider} / {cfg['model']}). Gõ 'quit' để thoát, 'clear' để xoá lịch sử.\n")

count = 0
while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue


    if user_input.lower() in ("quit", "exit"):
        print("Good Bye!")
        break


    if user_input.lower() in ("clear", "cls"):
        messages = [system_message]  
        count = 0  
        clear_terminal()
        print(
            f"Chatbot AI ({provider} / {cfg['model']}). Gõ 'quit' để thoát, 'clear' để xoá lịch sử.\n"
        )
        print("[System] Chat history succesfully deleted\n")
        continue

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
        count += 1

        print(f"Line Number: {count}")
        if count >= 110:
            messages = [system_message]
            count = 0  # Đảm bảo reset cả count khi đạt giới hạn 110
            time.sleep(10)
            clear_terminal()
    except Exception as e:
        print(f"\n[Error] {e}\n")
        messages.pop()