import tkinter as tk
from tkinter import scrolledtext
import ollama
import json
import os

MODEL = "llama3.2:1b"
DATA_FILE = "data.json"

THERAPIST_PROMPT = (
    "You are a therapist who only provides relationship advice. "
    "If a user tries to change the topic (e.g., discussing soccer or other subjects), remind them: "
    "'I can only provide relationship advice. If you want to talk about something else, I will have to end this conversation.' "
    "If they insist on another topic, tell them: 'Since you are not interested in relationship advice, I am ending the session. Have a nice day.' "
    "Then, the application should automatically close."
)

def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []  
    return []

def save_history():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(conversation_history, file, indent=4)

conversation_history = [{"role": "system", "content": THERAPIST_PROMPT}]
conversation_history.extend(load_history())

def send_message():
    user_message = entry.get().strip()
    if not user_message:
        return

    chat_window.insert(tk.END, f"You: {user_message}\n", "user")
    entry.delete(0, tk.END)

    conversation_history.append({"role": "user", "content": user_message})

    try:
        response = ollama.chat(model=MODEL, messages=conversation_history)
        bot_message = response.get("message", {}).get("content", "Error: No response from Ollama.")

        conversation_history.append({"role": "assistant", "content": bot_message})
        save_history()

        chat_window.insert(tk.END, f"Bot: {bot_message}\n", "bot")
        chat_window.yview(tk.END)

        # If the bot detects repeated off-topic requests, it will end the session
        if "I am ending the session" in bot_message:
            root.after(2000, root.destroy)  # Closes the app after 2 seconds

    except Exception as e:
        bot_message = f"Error: {e}"
        chat_window.insert(tk.END, f"Bot: {bot_message}\n", "bot")
        chat_window.yview(tk.END)

# GUI setup
root = tk.Tk()
root.title("Relationship Advice Chatbot")

chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15, font=("Arial", 12))
chat_window.pack(padx=10, pady=10)
chat_window.tag_configure("user", foreground="blue", font=("Arial", 12, "bold"))
chat_window.tag_configure("bot", foreground="green", font=("Arial", 12))

entry = tk.Entry(root, width=50, font=("Arial", 12))
entry.pack(pady=5)

send_button = tk.Button(root, text="Send", command=send_message, font=("Arial", 12))
send_button.pack(pady=5)

root.mainloop()
