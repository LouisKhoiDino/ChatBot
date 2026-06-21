import os
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI
import threading 
import itertools

def thinking_animation(stop_event):
    dots = itertools.cycle([".", "..", "...", "....", "....."])
    while not stop_event.is_set():
        sys.stdout.write(f"\rBot is thinking {next(dots)}   ")
        sys.stdout.flush()
        if stop_event.wait(0.5):
            break
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()

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
    sys.exit(f"Invalid provider: {provider}")

cfg = PROVIDERS[provider]
api_key = os.getenv(cfg["api_key_env"])
if not api_key:
    sys.exit(f"An API key is missing. Pls put an API key {cfg['api_key_env']}in .env")

client = OpenAI(base_url=cfg["base_url"], api_key=api_key)

system_message = {
    "role": "system",
    "content": "Bạn là trợ lý AI thân thiện. Trả lời đúng sự thật, dùng tiếng anh.",
}
messages = [system_message]


session_logs = []

print(f"Chatbot AI ({provider} / {cfg['model']}). Type clear to exit, type \n")

count = 0
while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue

    if user_input.lower() in ("quit", "exit"):
        if session_logs:
            try:
                with open("chat_log.txt", "w", encoding="utf-8") as f:
                    for log in session_logs:
                        f.write(f"{log['user']} | Bot: {log['bot']}\n")
                print("\n[System] Memorized messages in file 'chat_log.txt'.")
            except Exception as e:
                print(f"\n[System] Cannot write file: {e}")
        else:
            print("\n[System] No messages to memorize")
            
        print("Good Bye!")
        break

    
    if user_input.lower() in ("clear", "cls"):
        messages = [system_message]
        count = 0  
        clear_terminal()
        print(f"Chatbot AI ({provider} / {cfg['model']}). Type 'quit' to exit, 'clear' to delete history.\n")
        print("[System] History deleted.\n")
        continue

    messages.append({"role": "user", "content": user_input})

    stop = threading.Event()
    t = threading.Thread(target=thinking_animation, args=(stop,), daemon=True)
    t.start()

    try:
        response = client.chat.completions.create(
            model=cfg["model"],
            messages=messages,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        
        
       
        clean_user = user_input.replace("\n", " ")
        clean_reply = reply.replace("\n", " ")
        session_logs.append({"user": clean_user, "bot": clean_reply})

        
    except Exception as e:
       
        reply = None
        messages.pop()
        error = str(e)
    finally:
        stop.set()
        t.join()
        
    if reply is not None:
        count += 1
        

        if count >= 110:
            print("[System] Reached limit of 110 messages. Auto-reset in the next 10 seconds")
            messages = [system_message]
            count = 0  
            time.sleep(10)
            clear_terminal()
            print(f"Chatbot AI ({provider} / {cfg['model']}). Type 'quit' to exit, 'clear' to delete history\n")
        print(f"Bot: {reply}\n")
        
        print(f"Chat completed: {count}")
        
    else:
        print(f"[Error] {error}\n")
