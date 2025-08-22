import sqlite3

def saveRecord(
        chatId: str, 
        timestamp: int, 
        text: str, 
        user: str,
        messageId:str, 
        file: str = "Messages.db"
    ) -> None:
    """
    Save a Record to the database. IF the database specified is uncreated, it creates one.
    """
    
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    conn.execute("""
CREATE TABLE IF NOT EXISTS messages (
    chat_id TEXT,
    text TEXT,
    timestamp INTEGER,
    sender TEXT,
    message_id TEXT
)
""")
    conn.commit()
    
    cursor.execute("""
INSERT INTO messages (chat_id, text, timestamp, sender, message_id) VALUES (?, ?, ?, ?, ?)
""", (chatId, text, timestamp, user, messageId))
    
    conn.commit()

def getAllMessagesFromChat(
        chatId: str, 
        user: str = None, 
        fromTimestamp: int = None, 
        file: str = "Messages.db"
    ) -> list:
    """
    Fetch all messages from a given chat. 
    Can get messages from a Specified timestamp, 
    and from a specific user if these options are specified.
    """
    
    conn = sqlite3.connect(file)
    c = conn.cursor()
    
    if user:
        userCmd = f"AND sender={user}"
        
    else: userCmd = ""
    
    if fromTimestamp:
        timestampCmd = f"AND timestamp>={fromTimestamp}"
        
    else: timestampCmd = ""
    
    results = c.execute((
        "SELECT * FROM messages WHERE chat_id=? "
        f"{userCmd} {timestampCmd} ORDER BY timestamp"), (chatId,)
    )
    
    return results

def retrieveLatestMessage(file: str = "Messages.db") -> dict:
    """Find the most recent message in the database."""
    
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    result = c.execute(
        "SELECT * FROM messages ORDER BY timestamp DESC LIMIT 1"
    )
    row = result.fetchone()
    conn.close()
    return dict(row) if row else None