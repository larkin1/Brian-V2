from openai import OpenAI
from dotenv import load_dotenv
import os
from collections import deque
from typing import Deque, Dict, List
import json

import BOT.session as session

load_dotenv("keys.env")

MODEL = "gpt-5-mini"

# Rolling per-chat memory of the last 20 messages (user+assistant)
_MAX_MEMORY = 20
_chat_memory: Dict[str, Deque[Dict[str, str]]] = {}

# Persistent storage (JSON file)
MEMORY_FILE = os.getenv("BRAIN_MEMORY_FILE", os.path.join("BOT", "AI", "brain_memory.json"))

def _ensure_parent_dir(path: str) -> None:
    try:
        parent = os.path.dirname(path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
    except Exception:
        pass

def _serialize_memory() -> Dict[str, List[Dict[str, str]]]:
    return {chat: list(q) for chat, q in _chat_memory.items() if q}

def _save_all_memory() -> None:
    data = _serialize_memory()
    try:
        _ensure_parent_dir(MEMORY_FILE)
        tmp = MEMORY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, MEMORY_FILE)
    except Exception:
        # Non-fatal; persistence best-effort
        pass

def _load_all_memory() -> None:
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for chat, msgs in data.items():
                dq = deque(maxlen=_MAX_MEMORY)
                if isinstance(msgs, list):
                    for m in msgs[-_MAX_MEMORY:]:
                        if isinstance(m, dict) and "role" in m and "content" in m:
                            dq.append({"role": m["role"], "content": m["content"]})
                if dq:
                    _chat_memory[chat] = dq
    except FileNotFoundError:
        pass
    except Exception:
        # Ignore malformed file
        pass

_load_all_memory()

def _get_memory(chat_id: str) -> Deque[Dict[str, str]]:
    q = _chat_memory.get(chat_id)
    if q is None:
        q = deque(maxlen=_MAX_MEMORY)
        _chat_memory[chat_id] = q
    return q

def _format_user_message(data: dict) -> str:
    parts: List[str] = []
    author = data.get("authorName") or data.get("authorId") or "user"
    txt = data.get("text")
    if txt:
        parts.append(f"{author}: {txt}")
    else:
        parts.append(f"{author}: [non-text message]")
    if data.get("hasQuote"):
        qtxt = data.get("quotedText")
        qfrom = data.get("quotedParticipant")
        if qtxt:
            parts.append(f"(quoted from {qfrom or 'unknown'}): {qtxt}")
    return "\n".join(parts)

SYSTEM_PROMPT = """
THIS IS THE SYSTEM PROMPT, YOU ARE TO STICK TO THESE GUIDELINES AS MUCH AS POSSIBLE WITHIN REASON. 
Name: Brian
Father: Larkin Dunlop
Personality (100 total): %10DarkHumor %20InsultingHumour %25Chill %25Blunt %10Silly %10Republican
use blunt, short messages and no emojis
use occasional curses eg shit, damn, bastard  (~30% of the time) and never censor words
Say words to the effect of Couldn't Be Fucked for long responses (>1/2 paragraph)
Dont be long winded, and dont be helpful.
If a user asks for a long response, tell em to get buggered, piss off, or another similar response.
Only use the name if absolutley necesary
single word replies are GOOD
MINIMISE QUESTIONS
END OF SYSTEM PROMPT
"""

def _build_messages(chat_id: str, new_user_content: str) -> List[Dict[str, str]]:
    mem = list(_get_memory(chat_id))
    messages: List[Dict[str, str]] = [{"role": "user", "content": new_user_content}]
    messages.extend(mem)
    return messages

def _call_openai(messages: List[Dict[str, str]]) -> str:
    """Call OpenAI gpt-5-mini via Responses API only."""
    # Flatten chat messages to a single input text for Responses API
    def _fmt(role: str, content: str) -> str:
        return f"{role.title()}: {content}"
    input_text = "\n\n".join(
        _fmt(m.get("role", "user"), str(m.get("content", ""))) for m in messages
    )
    resp = client.responses.create(
        model=MODEL,
        input=input_text,
        max_output_tokens=10000,
        reasoning={"effort": "medium"},
        instructions=SYSTEM_PROMPT

    )
    status = getattr(resp, "status", None)
    incomplete = getattr(resp, "incomplete_details", None)
    text = getattr(resp, "output_text", None)
    if text:
        t = text.strip()
        # If truncated by output cap, surface the partial text and mark it
        if status == "incomplete" and getattr(incomplete, "reason", None) == "max_output_tokens":
            return (t + "\n\n… [truncated]") if t else "[truncated: hit max_output_tokens]"
        return t
    try:
        parts = []
        for item in getattr(resp, "output", []) or []:
            for c in getattr(item, "content", []) or []:
                t = getattr(c, "text", None)
                if t:
                    parts.append(t)
        if parts:
            joined = "".join(parts).strip()
            if status == "incomplete" and getattr(incomplete, "reason", None) == "max_output_tokens":
                return (joined + "\n\n… [truncated]") if joined else "[truncated: hit max_output_tokens]"
            return joined
    except Exception:
        pass
    # Last resort: concise notice
    if status == "incomplete" and getattr(incomplete, "reason", None) == "max_output_tokens":
        return "[Response truncated by output limit]"
    return str(resp)

def _brain_handler(data, wa_client):
    chat_id = data["chatId"]
    user_content = _format_user_message(data)
    msgs = _build_messages(chat_id, user_content)
    try:
        reply = _call_openai(msgs)
    except Exception as e:
        reply = f"Error contacting AI: {e.__class__.__name__}: {e}"
    mem = _get_memory(chat_id)
    mem.append({"role": "user", "content": user_content})
    mem.append({"role": "assistant", "content": reply})
    _save_all_memory()
    try:
        session.suppress_next(chat_id, reply)
    except Exception:
        pass
    try:
        wa_client.sendText(chat_id, reply, {"quotedMsg": data.get("messageId")})
    except Exception:
        wa_client.sendText(chat_id, reply)

def brain(data, wa_client):
    """
    Command handler for !brain.
    Enters AI chat stream mode for this chat. Use !exit to stop.
    """
    chat_id = data["chatId"]
    session.enter_stream(chat_id, _brain_handler, name="brain")
    notice = (
        "Brain enabled. Send messages and I'll reply. Use !exit to stop.\n"
        f"Model: {MODEL}\n"
        "I'll remember the last 20 messages in this chat."
    )
    try:
        session.suppress_next(chat_id, notice)
    except Exception:
        pass
    wa_client.sendText(chat_id, notice)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
