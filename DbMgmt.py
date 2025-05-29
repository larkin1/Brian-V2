import sqlite3

def saveRecord(id: str, timestamp: int, text: str, user: str, file: str = "Messages.db") -> None:
    """Save a Record to the database. IF the database specified is uncreated, it creates one."""
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    conn.execute("""
CREATE TABLE IF NOT EXISTS messages (
    chat_id TEXT,
    text TEXT,
    timestamp INTEGER,
    sender TEXT
)
""")
    conn.commit()
    
    cursor.execute("""
INSERT INTO messages (chat_id, text, timestamp, sender) VALUES (?, ?, ?, ?)
""", (id, text, timestamp, user))
    
    conn.commit()

def getAllMessagesFromChat(id: str, user: str = None, fromTimestamp: int = None, file: str = "Messages.db") -> list:
    conn = sqlite3.connect(file)
    c = conn.cursor()
    
    if user:
        userCmd = f"AND sender={user}"
    else: userCmd = ""
    if fromTimestamp:
        timestampCmd = f"AND timestamp>={fromTimestamp}"
    else: timestampCmd = ""
    
    results = c.execute(f"SELECT * FROM messages WHERE chat_id=? {userCmd} {timestampCmd} ORDER BY timestamp", (id,))
    
    return results

if __name__ == "__main__":
    saveRecord("TestChat", 1, "Testing Text", "TestUser")