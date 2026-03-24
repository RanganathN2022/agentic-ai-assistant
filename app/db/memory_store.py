import sqlite3

DB_PATH = "memory.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_memory (
            session_id TEXT,
            user TEXT,
            bot TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_message(session_id, user, bot):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chat_memory VALUES (?, ?, ?)",
        (session_id, user, bot)
    )

    conn.commit()
    conn.close()


def get_memory(session_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user, bot FROM chat_memory WHERE session_id=?",
        (session_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [{"user": r[0], "bot": r[1]} for r in rows]