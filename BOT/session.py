"""Session/stream state management for per-chat handlers.

Use enter_stream(chat_id, handler, name) to enable a streaming handler that
receives every non-command message in that chat. Disable with exit_stream or the
!exit command (mapped to exit_command).

Handlers will be invoked with the usual (data, client) signature.
"""
from typing import Callable, Dict, Optional

# Map of chat_id -> { 'handler': callable, 'name': str }
_active_streams: Dict[str, Dict[str, object]] = {}


def enter_stream(chat_id: str, handler: Callable, name: Optional[str] = None) -> None:
    """Enable streaming for a chat with a given handler."""
    _active_streams[chat_id] = {
        "handler": handler,
        "name": name or getattr(handler, "__name__", "stream"),
    }


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
