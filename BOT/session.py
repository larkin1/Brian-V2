"""Session/stream state management for per-chat handlers.

Use enter_stream(chat_id, handler, name) to enable a streaming handler that
receives every non-command message in that chat. Disable with exit_stream or the
!exit command (mapped to exit_command).

Handlers will be invoked with the usual (data, client) signature.
"""
from typing import Callable, Dict, Optional, List

import threading

# Map of chat_id -> { 'handler': callable, 'name': str }
_active_streams: Dict[str, Dict[str, object]] = {}
# Per-chat suppression of next message(s) by exact text, to avoid echo loops
_suppress_next: Dict[str, List[str]] = {}

# Introduce a dictionary to keep track of timers for each active chat
_active_timers: Dict[str, threading.Timer] = {}

def set_inactivity_timer(chat_id: str) -> None:
    """Set or reset the inactivity timer for a chat."""
    if chat_id in _active_timers:
        _active_timers[chat_id].cancel()  # Cancel the existing timer if it exists

    def timeout_callback():
        if exit_stream(chat_id):
            # client.sendText(chat_id, "Session exited due to inactivity.")
            _active_timers.pop(chat_id, None)

    # Start a new timer for 30 seconds
    timer = threading.Timer(30.0, timeout_callback)
    _active_timers[chat_id] = timer
    timer.start()

def enter_stream(chat_id: str, handler: Callable, name: Optional[str] = None) -> None:
    """Enable streaming for a chat with a given handler."""
    _active_streams[chat_id] = {
        "handler": handler,
        "name": name or getattr(handler, "__name__", "stream"),
    }
    set_inactivity_timer(chat_id)  # Start the inactivity timer


def exit_stream(chat_id: str) -> bool:
    """Disable streaming for a chat. Returns True if a stream existed."""
    return _active_streams.pop(chat_id, None) is not None


def is_active(chat_id: str) -> bool:
    return chat_id in _active_streams


def get_handler(chat_id: str) -> Optional[Callable]:
    entry = _active_streams.get(chat_id)
    return entry["handler"] if entry else None


def get_name(chat_id: str) -> Optional[str]:
    entry = _active_streams.get(chat_id)
    return entry["name"] if entry else None


# Command function to exit stream via !exit

def exit_command(data, client):
    chat_id = data["chatId"]
    if exit_stream(chat_id):
        client.sendText(chat_id, "Exited stream mode.")
    else:
        client.sendText(chat_id, "No active stream.")


# Echo suppression helpers
def suppress_next(chat_id: str, text: str) -> None:
    """Mark the next outgoing message with this text in this chat to be ignored by the dispatcher."""
    _suppress_next.setdefault(chat_id, []).append(text)


def should_suppress(chat_id: str, text: Optional[str]) -> bool:
    """Return True and consume suppression if this (chat, text) is marked for one-time ignore."""
    if text is None:
        return False
    pending = _suppress_next.get(chat_id)
    if not pending:
        return False
    try:
        idx = pending.index(text)
    except ValueError:
        return False
    # Remove the matched item
    pending.pop(idx)
    if not pending:
        _suppress_next.pop(chat_id, None)
    return True

